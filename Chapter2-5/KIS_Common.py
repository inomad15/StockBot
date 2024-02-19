import yaml

import json
import requests

from datetime import datetime, timedelta
from pytz import timezone

import KIS_API_Helper_US as KisUS
import KIS_API_Helper_KR as KisKR

import time



import FinanceDataReader as fdr
import pandas_datareader.data as web

# pip3 install pandas-datareader
# pip3 install -U finance-datareader


import pandas as pd


stock_info = None

#설정 파일 정보를 읽어 옵니다.
with open('/var/autobot/myStockInfo.yaml', encoding='UTF-8') as f:
    stock_info = yaml.load(f, Loader=yaml.FullLoader)
    
    

############################################################################################################################################################
NOW_DIST = ""

#계좌 전환 함수! REAL 실계좌 VIRTUAL 모의계좌
def SetChangeMode(dist = "REAL"):
    global NOW_DIST 
    NOW_DIST = dist


#현재 선택된 계좌정보를 리턴!
def GetNowDist():
    global NOW_DIST 
    return NOW_DIST

############################################################################################################################################################

#앱 키를 반환하는 함수
def GetAppKey(dist = "REAL"):
    
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_APP_KEY"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_APP_KEY"
        
    return stock_info[key]


#앱시크릿을 리턴!
def GetAppSecret(dist = "REAL"):
    
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_APP_SECRET"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_APP_SECRET"
        
    return stock_info[key]


#계좌 정보를 리턴!
def GetAccountNo(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_CANO"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_CANO"
        
    return stock_info[key]


#계좌 정보를 리턴!
def GetPrdtNo(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_ACNT_PRDT_CD"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_ACNT_PRDT_CD"
        
    return stock_info[key]


#URL주소를 리턴!
def GetUrlBase(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_URL"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_URL"
        
    return stock_info[key]





#토큰 저장할 경로
def GetTokenPath(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_TOKEN_PATH"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_TOKEN_PATH"
        
    return stock_info[key]


        

#토큰 값을 리퀘스트 해서 실제로 만들어서 파일에 저장하는 함수!! 첫번째 파라미터: "REAL" 실계좌, "VIRTUAL" 모의계좌
def MakeToken(dist = "REAL"):


    headers = {"content-type":"application/json"}
    body = {
        "grant_type":"client_credentials",
        "appkey":GetAppKey(dist), 
        "appsecret":GetAppSecret(dist)
        }

    PATH = "oauth2/tokenP"
    URL = f"{GetUrlBase(dist)}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    

    if res.status_code == 200:
        my_token = res.json()["access_token"]

        #빈 딕셔너리를 선언합니다!
        dataDict = dict()

        #해당 토큰을 파일로 저장해 둡니다!
        dataDict["authorization"] = my_token
        with open(GetTokenPath(dist), 'w') as outfile:
            json.dump(dataDict, outfile)   

        print("TOKEN : ", my_token)

        return my_token

    else:
        print('Get Authentification token fail!')  
        return "FAIL"


#파일에 저장된 토큰값을 읽는 함수.. 만약 파일이 없다면 MakeToken 함수를 호출한다!
def GetToken(dist = "REAL"):
        
    #빈 딕셔너리를 선언합니다!
    dataDict = dict()

    try:

        #이 부분이 파일을 읽어서 딕셔너리에 넣어주는 로직입니다. 
        with open(GetTokenPath(dist), 'r') as json_file:
            dataDict = json.load(json_file)


        return dataDict['authorization']

    except Exception as e:
        print("Exception by First")

        #처음에는 파일이 존재하지 않을테니깐 바로 토큰 값을 구해서 리턴!
        return MakeToken(dist)


############################################################################################################################################################
#해시키를 리턴한다!
def GetHashKey(datas):

    PATH = "uapi/hashkey"
    URL = f"{GetUrlBase(NOW_DIST)}/{PATH}"

    headers = {
    'content-Type' : 'application/json',
    'appKey' : GetAppKey(NOW_DIST),
    'appSecret' : GetAppSecret(NOW_DIST),
    }

    res = requests.post(URL, headers=headers, data=json.dumps(datas))

    if res.status_code == 200 :
        return res.json()["HASH"]
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None

############################################################################################################################################################


############################################################################################################################################################
#한국인지 미국인지 구분해 현재 날짜정보를 리턴해 줍니다!
def GetNowDateStr(area = "KR", type= "NONE" ):
    timezone_info = timezone('Asia/Seoul')
    if area == "US":
        timezone_info = timezone('America/New_York')

    now = datetime.now(timezone_info)
    if type.upper() == "NONE":
        return now.strftime("%Y%m%d")
    else:
        return now.strftime("%Y-%m-%d")

#현재날짜에서 이전/이후 날짜를 구해서 리턴! (미래의 날짜를 구할 일은 없겠지만..)
def GetFromNowDateStr(area = "KR", type= "NONE" , days=100):
    timezone_info = timezone('Asia/Seoul')
    if area == "US":
        timezone_info = timezone('America/New_York')

    now = datetime.now(timezone_info)

    if days < 0:
        next = now - timedelta(days=abs(days))
    else:
        next = now + timedelta(days=days)

    if type.upper() == "NONE":
        return next.strftime("%Y%m%d")
    else:
        return next.strftime("%Y-%m-%d")
############################################################################################################################################################

#통합 증거금 사용시 잔고 확인!
def GetBalanceKrwTotal():
    kr_data = KisKR.GetBalance()
    us_data = KisUS.GetBalance("KRW")

    balanceDict = dict()

    balanceDict['RemainMoney'] = str(float(kr_data['RemainMoney']) + float(us_data['RemainMoney']))
    #주식 총 평가 금액
    balanceDict['StockMoney'] = str(float(kr_data['StockMoney']) + float(us_data['StockMoney']))
    #평가 손익 금액
    balanceDict['StockRevenue'] = str(float(kr_data['StockRevenue']) + float(us_data['StockRevenue']))
    #총 평가 금액
    balanceDict['TotalMoney'] = str(float(kr_data['TotalMoney']) + float(us_data['TotalMoney']))

    return balanceDict




############################################################################################################################################################
#OHLCV 값을 한국투자증권 혹은 FinanceDataReader 혹은 야후 파이낸스에서 가지고 옴!
def GetOhlcv(area, stock_code, limit = 500):

    Adjlimit = limit * 1.7 #주말을 감안하면 5개를 가져오려면 적어도 7개는 뒤져야 된다. 1.4가 이상적이지만 혹시 모를 연속 공휴일 있을지 모르므로 1.7로 보정해준다

    df = None

    except_riase = False

    try:

        if area == "US":

            print("----First try----")
            df = KisUS.GetOhlcv(stock_code,"D")

            #한투에서 100개 이상 못가져 오니깐 그 이상은 아래 로직을 탄다. 혹은 없는 종목이라면 역시 아래 로직을 탄다
            if Adjlimit > 100 or len(df) == 0:

                #미국은 보다 빠른 야후부터 
                except_riase = False
                try:
                    print("----Second try----")
                    df = GetOhlcv2(area,stock_code,Adjlimit)
                except Exception as e:
                    except_riase = True
                    
                if except_riase == True:
                    print("----Third try----")
                    df = GetOhlcv1(area,stock_code,Adjlimit)

        
        else:

            print("----First try----")
            df = KisKR.GetOhlcv(stock_code,"D")
            

            #한투에서 100개 이상 못가져 오니깐 그 이상은 아래 로직을 탄다. 혹은 없는 종목이라면 역시 아래 로직을 탄다
            if Adjlimit > 100 or len(df) == 0:

                #한국은 KRX 정보데이터시스템 부터 
                except_riase = False
                try:
                    print("----Second try----")
                    df = GetOhlcv1(area,stock_code,Adjlimit)
                except Exception as e:
                    except_riase = True
                    
                if except_riase == True:
                    print("----Third try----")
                    df = GetOhlcv2(area,stock_code,Adjlimit)


    except Exception as e:
        print(e)
        except_riase = True
    

    if except_riase == True:
        return df
    else:
        print("---", limit)
        return df[-limit:]




#한국 주식은 KRX 정보데이터시스템에서 가져온다. 그런데 미국주식 크롤링의 경우 investing.com 에서 가져오는데 안전하게 2초 정도 쉬어야 한다!
# https://financedata.github.io/posts/finance-data-reader-users-guide.html
def GetOhlcv1(area, stock_code, limit = 500):

    df = fdr.DataReader(stock_code,GetFromNowDateStr(area,"BAR",-limit),GetNowDateStr(area,"BAR"))

    df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = [ 'open', 'high', 'low', 'close', 'volume']
    df.index.name = "Date"

    #거래량과 시가,종가,저가,고가의 평균을 곱해 대략의 거래대금을 구해서 value 라는 항목에 넣는다 ㅎ
    df.insert(5,'value',((df['open'] + df['high'] + df['low'] + df['close'])/4.0) * df['volume'])


    df.insert(6,'change',(df['close'] - df['close'].shift(1)) / df['close'].shift(1))

    df[[ 'open', 'high', 'low', 'close', 'volume', 'change']] = df[[ 'open', 'high', 'low', 'close', 'volume', 'change']].apply(pd.to_numeric)

    #미국주식은 2초를 쉬어주자! 안그러면 24시간 정지당할 수 있다!
    if area == "US":
        time.sleep(2.0)
    else:
        time.sleep(0.2)


    return df



#야후 파이낸스에서 정보 가져오기! 
# https://pandas-datareader.readthedocs.io/en/latest/
def GetOhlcv2(area, stock_code, limit = 500):

    df = None

    if area == "KR":

        except_riase = False
        try:
            df = web.DataReader(stock_code + ".KS", "yahoo", GetFromNowDateStr(area,"BAR",-limit),GetNowDateStr(area,"BAR"))
        except Exception as e:
            except_riase = True

        if except_riase == True:
            try:
                df = web.DataReader(stock_code + ".KQ", "yahoo", GetFromNowDateStr(area,"BAR",-limit),GetNowDateStr(area,"BAR"))
            except Exception as e:
                print("")

    else:
        df = web.DataReader(stock_code, "yahoo", GetFromNowDateStr(area,"BAR",-limit),GetNowDateStr(area,"BAR"))



    df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume' ]]
    df.columns = [ 'open', 'high', 'low', 'close', 'volume']
    df.index.name = "Date"

    #거래량과 시가,종가,저가,고가의 평균을 곱해 대략의 거래대금을 구해서 value 라는 항목에 넣는다 ㅎ
    df.insert(5,'value',((df['open'] + df['high'] + df['low'] + df['close'])/4.0) * df['volume'])


    df.insert(6,'change',(df['close'] - df['close'].shift(1)) / df['close'].shift(1))

    df[[ 'open', 'high', 'low', 'close', 'volume', 'change']] = df[[ 'open', 'high', 'low', 'close', 'volume', 'change']].apply(pd.to_numeric)


    time.sleep(0.2)
        


    return df


    
