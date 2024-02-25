import yaml

import json
import requests

from datetime import datetime, timedelta
from pytz import timezone

import KIS_API_Helper_US as KisUS
import KIS_API_Helper_KR as KisKR

import time
import random


import FinanceDataReader as fdr
import pandas_datareader.data as web
from pykrx import stock

import numpy
import pandas as pd

import yfinance


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
    
    if dist == "REAL" or dist == "REAL2":
        key = "REAL_APP_KEY"
    elif dist == "REAL3":
        key = "REAL3_APP_KEY"
    elif dist == "REAL4":
        key = "REAL4_APP_KEY"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_APP_KEY"
        
    return stock_info[key]


#앱시크릿을 리턴!
def GetAppSecret(dist = "REAL"):
    
    global stock_info
    
    key = ""
    
    if dist == "REAL" or dist == "REAL2":
        key = "REAL_APP_SECRET"
    elif dist == "REAL3":
        key = "REAL3_APP_SECRET"
    elif dist == "REAL4":
        key = "REAL4_APP_SECRET"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_APP_SECRET"
        
    return stock_info[key]


#계좌 정보를 리턴!
def GetAccountNo(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL" or dist == "REAL2":
        key = "REAL_CANO"
    elif dist == "REAL3":
        key = "REAL3_CANO"
    elif dist == "REAL4":
        key = "REAL4_CANO"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_CANO"
        
    return stock_info[key]


#계좌 정보(상품코드)를 리턴!
def GetPrdtNo(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL":
        key = "REAL_ACNT_PRDT_CD"
    elif dist == "REAL2":
        key = "REAL2_ACNT_PRDT_CD"
    elif dist == "REAL3":
        key = "REAL3_ACNT_PRDT_CD"
    elif dist == "REAL4":
        key = "REAL4_ACNT_PRDT_CD"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_ACNT_PRDT_CD"
        
    return stock_info[key]




#토큰 저장할 경로
def GetTokenPath(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "REAL" or dist == "REAL2":
        key = "REAL_TOKEN_PATH"
    elif dist == "REAL3":
        key = "REAL3_TOKEN_PATH"
    elif dist == "REAL4":
        key = "REAL4_TOKEN_PATH"
    elif dist == "VIRTUAL":
        key = "VIRTUAL_TOKEN_PATH"
        
    return stock_info[key]


 
#URL주소를 리턴!
def GetUrlBase(dist = "REAL"):
    global stock_info
    
    key = ""
    
    if dist == "VIRTUAL":
        key = "VIRTUAL_URL"
    else:
        key = "REAL_URL"
        

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




#https://blog.naver.com/zacra/222986007794
def GetOhlcv2(area, stock_code, limit = 500):

    df = None

    if area == "KR":

        df = web.DataReader(stock_code, "naver", GetFromNowDateStr(area,"BAR",-limit),GetNowDateStr(area,"BAR"))


    else:
        df = yfinance.download(stock_code, period='3y')

    print(df)

    df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume' ]]
    df.columns = [ 'open', 'high', 'low', 'close', 'volume']
    df = df.astype({'open':float,'high':float,'low':float,'close':float,'volume':float})
    df.index.name = "Date"


    #거래량과 시가,종가,저가,고가의 평균을 곱해 대략의 거래대금을 구해서 value 라는 항목에 넣는다 ㅎ
    df.insert(5,'value',((df['open'] + df['high'] + df['low'] + df['close'])/4.0) * df['volume'])
    df.insert(6,'change',(df['close'] - df['close'].shift(1)) / df['close'].shift(1))

    df[[ 'open', 'high', 'low', 'close', 'volume', 'change']] = df[[ 'open', 'high', 'low', 'close', 'volume', 'change']].apply(pd.to_numeric)


    time.sleep(0.2)
        


    return df

    




#pykrx를 통해 지수 정보를 읽어온다!
#아래 2줄로 활용가능한 지수를 체크할 수 있다!!
#for index_v in stock.get_index_ticker_list(market='KOSDAQ'): #KOSPI 지수도 확인 가능!
#    print(index_v, stock.get_index_ticker_name(index_v))

def GetIndexOhlcvPyKrx(index_code, limit = 500):


    df = stock.get_index_ohlcv(GetFromNowDateStr("KR","NONE",-limit), GetNowDateStr("KR","NONE"), index_code)


    df = df[[ '시가', '고가', '저가', '종가', '거래량', '거래대금' ]]
    df.columns = [ 'open', 'high', 'low', 'close', 'volume', 'value']
    df.index.name = "Date"

    df.insert(6,'change',(df['close'] - df['close'].shift(1)) / df['close'].shift(1))

    df[[ 'open', 'high', 'low', 'close', 'volume', 'change']] = df[[ 'open', 'high', 'low', 'close', 'volume', 'change']].apply(pd.to_numeric)


    time.sleep(0.2)


    return df






'''
!!!!!stock_type 유형!!!!!

TARGET_FIX : 
첫 주문한 지정가격이 절대 변하지 않는다. 체결되기 전까지 매일 매일 재주문!!!

NORMAL : 
지정된 카운팅에 해당하는 날 전에는 계속 타겟 가격으로 주문을 넣다가 
카운팅 날짜 부터는 현재가 그 다음날에는 지정가로 일 단위로 주문을 넣는 루즈한 로직


DAY_END : 
지정가로 주문을 넣지만 하루안에 주문을 끝낸다.  장중에 매시간마다 해당 주문을 체크해서 현재가로 지정가 주문을 변경 (체결 확률 업! ) 
마지막 장 끝나기 전 시간에도 수량이 남아있다면 이때는 시장가로 마무리 !


DAY_END_TRY_ETF:
DAY_END랑 비슷하지만 ETF의 NAV와 괴리율을 고려해서 하루안에 끝내거나 다음 날로 넘김 (클래스 설명 참조)

'''
#area 지역: US or KR, 종목코드, 목표 가격, 수량 (양수면 매수 음수면 매도) 연속성 주문 시스템!
def AutoLimitDoAgain(botname, area, stock_code, target_price, do_amt, stock_type = "NORMAL"):

    #수량이 0이면 거른다!
    if int(do_amt) == 0:
        return None


    if area == "KR":
        print("KR")

        MyStockList = KisKR.GetMyStockList()


        stock_amt = 0
        for my_stock in MyStockList:
            if my_stock['StockCode'] == stock_code:
                stock_amt = int(my_stock['StockAmt'])
                break

        AutoLimitData = dict()
        AutoLimitData['Area'] = area                #지역
        AutoLimitData['NowDist'] = GetNowDist()     #구분
        AutoLimitData['BotName'] = botname          #봇 이름
        AutoLimitData['StockCode'] = stock_code      #종목코드
        AutoLimitData['TargetPrice'] = float(target_price)   #타겟 주문 가격
        AutoLimitData['OrderAmt'] = int(do_amt)              #주문 수량 양수면 매수 음수면 매도 
        
        OrderData = None

        #사야된다
        if do_amt > 0:
            AutoLimitData['TargetAmt'] = stock_amt + abs(AutoLimitData['OrderAmt'])  #최종 목표 수량 (현재수량 + 주문수량)

            try:

                OrderData = KisKR.MakeBuyLimitOrder(stock_code,abs(do_amt),target_price)
                AutoLimitData['OrderNum'] = OrderData["OrderNum"]      #주문아이디1
                AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]    #주문아이디2
                AutoLimitData['OrderTime'] = OrderData["OrderTime"]    #주문시간

            except Exception as e:

                #시간 정보를 읽는다
                time_info = time.gmtime()
                AutoLimitData['OrderNum'] = 0
                AutoLimitData['OrderNum2'] = 0
                AutoLimitData['OrderTime'] = GetNowDateStr(area) + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec)

                        

        #팔아야 된다!
        else:

            AutoLimitData['TargetAmt'] = stock_amt - abs(AutoLimitData['OrderAmt']) #최종 목표 수량 (현재수량 - 주문수량)

            try:
                    
                OrderData = KisKR.MakeSellLimitOrder(stock_code,abs(do_amt),target_price)
                AutoLimitData['OrderNum'] = OrderData["OrderNum"]
                AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]   
                AutoLimitData['OrderTime'] = OrderData["OrderTime"]   

            except Exception as e:

                #시간 정보를 읽는다
                time_info = time.gmtime()
                AutoLimitData['OrderNum'] = 0
                AutoLimitData['OrderNum2'] = 0
                AutoLimitData['OrderTime'] = GetNowDateStr(area) + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec)

                        
                        
        AutoLimitData['IsCancel'] = 'N'  #주문 취소 여부
        AutoLimitData['IsDone'] = 'N'    #주문 완료 여부
        AutoLimitData['TryCnt'] = 0    #재주문 숫자 
        AutoLimitData['DelDate'] =  GetFromNowDateStr(area,"NONE",10)    #10일 미래의 날짜 즉 10일 후에는 해당 데이터를 삭제처리할 예정 (어자피 하루만 유효한 주문들이다. 하루 지나고 삭제해도 되지만 참고를 위해 10일간 남겨둔다)
        AutoLimitData['StockType'] = stock_type #stock_type 유형

        #해당 데이터의 ID를 만든다! 여러 항목의 조합으로 고유하도록!  이 아이디를 리턴해 봇에서 줘서 필요한 봇은 이 아이디를 가지고 리스트를 만들어 사용하면 된다!
        AutoLimitData['Id'] = AutoLimitData['NowDist'] + botname + area + str(stock_code) + str(AutoLimitData["OrderNum"]) + str(AutoLimitData["OrderNum2"]) + str(AutoLimitData["OrderTime"]) + str(do_amt) + str(target_price) 
    

        SaveAutoLimitDoAgainData(AutoLimitData)




        #등록된 해당 주문 데이터 ID를 리턴한다
        return AutoLimitData['Id']

        


    else:
        print("US")


        MyStockList = KisUS.GetMyStockList()


        stock_amt = 0
        for my_stock in MyStockList:
            if my_stock['StockCode'] == stock_code:
                stock_amt = int(my_stock['StockAmt'])
                break

        AutoLimitData = dict()
        AutoLimitData['Area'] = area                #지역
        AutoLimitData['NowDist'] = GetNowDist()     #구분
        AutoLimitData['BotName'] = botname          #봇 이름
        AutoLimitData['StockCode'] = stock_code      #종목코드
        AutoLimitData['TargetPrice'] = float(target_price)   #타겟 주문 가격
        AutoLimitData['OrderAmt'] = int(do_amt)              #주문 수량 양수면 매수 음수면 매도 
        
        #사야된다
        if do_amt > 0:
            AutoLimitData['TargetAmt'] = stock_amt + abs(AutoLimitData['OrderAmt'])  #최종 목표 수량 (현재수량 + 주문수량)


            try:

                OrderData = KisUS.MakeBuyLimitOrder(stock_code,abs(do_amt),target_price)
                AutoLimitData['OrderNum'] = OrderData["OrderNum"]      #주문아이디1
                AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]    #주문아이디2
                AutoLimitData['OrderTime'] = OrderData["OrderTime"]    #주문시간


            except Exception as e:

                #시간 정보를 읽는다
                time_info = time.gmtime()
                AutoLimitData['OrderNum'] = 0
                AutoLimitData['OrderNum2'] = 0
                AutoLimitData['OrderTime'] = GetNowDateStr(area)  + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec) 


        #팔아야 된다!
        else:

            AutoLimitData['TargetAmt'] = stock_amt - abs(AutoLimitData['OrderAmt']) #최종 목표 수량 (현재수량 - 주문수량)

            try:
                OrderData = KisUS.MakeSellLimitOrder(stock_code,abs(do_amt),target_price)
                AutoLimitData['OrderNum'] = OrderData["OrderNum"]
                AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]   
                AutoLimitData['OrderTime'] = OrderData["OrderTime"]   

            except Exception as e:

                #시간 정보를 읽는다
                time_info = time.gmtime()
                AutoLimitData['OrderNum'] = 0
                AutoLimitData['OrderNum2'] = 0
                AutoLimitData['OrderTime'] = GetNowDateStr(area)  + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec) 



        AutoLimitData['IsCancel'] = 'N' #주문 취소 여부
        AutoLimitData['IsDone'] = 'N'   #주문 완료 여부
        AutoLimitData['TryCnt'] = 0    #재주문 숫자 
        AutoLimitData['DelDate'] =  GetFromNowDateStr(area,"NONE",10)    #10일 미래의 날짜 즉 10일 후에는 해당 데이터를 삭제처리할 예정 (어자피 하루만 유효한 주문들이다. 하루 지나고 삭제해도 되지만 참고를 위해 10일간 남겨둔다)
        AutoLimitData['StockType'] = stock_type #stock_type 유형


        #해당 데이터의 ID를 만든다! 여러 항목의 조합으로 고유하도록!  이 아이디를 리턴해 봇에서 줘서 필요한 봇은 이 아이디를 가지고 리스트를 만들어 사용하면 된다!
        AutoLimitData['Id'] = AutoLimitData['NowDist'] + botname + area + str(stock_code) + str(AutoLimitData["OrderNum"]) + str(AutoLimitData["OrderNum2"]) + str(AutoLimitData["OrderTime"]) + str(do_amt) + str(target_price) 
    

        SaveAutoLimitDoAgainData(AutoLimitData)


            

        #등록된 해당 주문 데이터 ID를 리턴한다
        return AutoLimitData['Id']
            


#자동 주문 데이터를 각 봇 파일에 저장을 하는 함수!
def SaveAutoLimitDoAgainData(AutoLimitData):


    #파일 경로입니다.
    auto_order_file_path = "/var/autobot/" + AutoLimitData['Area'] + "_" + AutoLimitData['NowDist'] + "_" + AutoLimitData['BotName'] + "AutoOrderList.json"

    #이렇게 랜덤하게 쉬어줘야 혹시나 있을 중복 파일 접근 방지!
    time.sleep(random.random()*0.1)
    
    #자동 주문 리스트 읽기!
    AutoOrderList = list()
    try:
        with open(auto_order_file_path, 'r') as json_file:
            AutoOrderList = json.load(json_file)
    except Exception as e:
        print("Exception by First")

    #!!!! 넘어온 데이터를 리스트에 추가하고 저장하기!!!!
    AutoOrderList.append(AutoLimitData)
    with open(auto_order_file_path, 'w') as outfile:
        json.dump(AutoOrderList, outfile)





    #봇마다 고유한 경로(자동주문리스트 파일의 경로)를 1개씩 저장해 둔다
    #이를 for문 돌면 전체 모든 봇의 자동주문 리스트에 접근해서 처리할 수 있다
    time.sleep(random.random()*0.1)
    bot_path_file_path = "/var/autobot/BotOrderListPath.json"
    BotOrderPathList = list()
    try:
        with open(bot_path_file_path, 'r') as json_file:
            BotOrderPathList = json.load(json_file)

    except Exception as e:
        print("Exception by First")



    #읽어와서 중복되지 않은 것만 등록한다!
    IsAlreadyIn = False
    for botOrderPath in BotOrderPathList:
        if botOrderPath == auto_order_file_path:
            IsAlreadyIn = True
            break

    #현재 저 파일에 없다면 추가해준다!!
    if IsAlreadyIn == False:
        BotOrderPathList.append(auto_order_file_path)

        with open(bot_path_file_path, 'w') as outfile:
            json.dump(BotOrderPathList, outfile)





#주문 아이디를 받아 해당 주문을 취소하는 로직
def DelAutoLimitOrder(AutoOrderId):

    bot_path_file_path = "/var/autobot/BotOrderListPath.json"

    #각 봇 별로 들어가 있는 자동 주문 리스트!!!
    BotOrderPathList = list()
    try:
        with open(bot_path_file_path, 'r') as json_file:
            BotOrderPathList = json.load(json_file)

    except Exception as e:
        print("Exception by First")

    IsFindOrder = False
    time.sleep(random.random()*0.01)
    #오토 리미트 주문 데이터가 있는 모든 봇을 순회하며 처리한다!!
    for botOrderPath in BotOrderPathList:

        #이 botOrderPath는 각 봇의 고유한 경로 (리미트 오토 주문들이 저장되어 있는 파일 경로)
        print("----->" , botOrderPath)

        AutoOrderList = list()

        try:
            with open(botOrderPath, 'r') as json_file:
                AutoOrderList = json.load(json_file)

        except Exception as e:
            print("Exception by First")



       
        
        #해당 봇의 읽어온 주문 데이터들을 순회합니다.
        for AutoLimitData in AutoOrderList:

            try:

                #해당 주문을 찾았다!!!
                if AutoLimitData['Id'] == AutoOrderId:


                    #해당 주문의 계좌를 바라보도록 셋팅 합니다!!
                    SetChangeMode(AutoLimitData['NowDist']) 

                    ########## 현재 살아있는 주문을 취소!!! #######

                    #내 주식 잔고 리스트를 읽어서 현재 보유 수량 정보를 stock_amt에 넣어요!
                    MyStockList = KisUS.GetMyStockList()
                    if AutoLimitData['Area'] == "KR":
                        MyStockList = KisKR.GetMyStockList()


                    #미체결 수량이 들어갈 변수!
                    GapAmt = 0

                    stock_amt = 0
                    for my_stock in MyStockList:
                        if my_stock['StockCode'] == AutoLimitData['StockCode']:
                            stock_amt = int(my_stock['StockAmt'])
                            print(my_stock['StockName'], stock_amt)
                            break

                    #일단 목표로 하는 수량에서 현재 보유수량을 빼줍니다.
                    #이는 종목의 주문이 1개일 때 유효합니다. 왜 그런지 그리고TargetAmt값이 뭔지는 KIS_Common의 AutoLimitDoAgain함수를 살펴보세요
                    GapAmt = abs(AutoLimitData['TargetAmt'] - stock_amt)

                    Is_Except = False
                    try:

                        #주문리스트를 읽어 온다! 퇴직연금계좌 IRP계좌에서는 이 정보를 못가져와 예외가 발생합니다!!
                        OrderList = KisKR.GetOrderList(AutoLimitData['StockCode'])

                        print(len(OrderList) , " <--- Order OK!!!!!!")
                        
                        #주문 번호를 이용해 해당 주문을 찾습니다!!!
                        for OrderInfo in OrderList:
                            if OrderInfo['OrderNum'] == AutoLimitData['OrderNum'] and float(OrderInfo["OrderNum2"]) == float(AutoLimitData['OrderNum2']):
                                GapAmt = abs(OrderInfo["OrderResultAmt"] - OrderInfo["OrderAmt"])

                                if AutoLimitData['Area'] == "KR":
                                    KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                else:
                                    KisUS.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum2'],AutoLimitData['OrderAmt'],KisUS.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                        
                                break

                    except Exception as e:
                        #예외 발생!
                        Is_Except = True
                        print("Exception", e)

                    #예외가 발생했다면 
                    if Is_Except == True:
                        try:
                            #취소!
                            if AutoLimitData['Area'] == "KR":
                                KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                            else:
                                #미국은 2차 시도! 최초 주문수량으로 취소가 되는지 남은 미체결 수량으로 취소가 되는지 불분명..이렇게 하면 위에서 1번 여기서 1번 취소처리 함으로써 취소가 안된 주문을 확실히 취소 처리 할 수 있다!
                                KisUS.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum2'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                        except Exception as e:
                            print("Exception", e)
       

                    ##########실제로 리스트에서 제거#######
                    AutoOrderList.remove(AutoLimitData)

                    with open(botOrderPath, 'w') as outfile:
                        json.dump(AutoOrderList, outfile)

                    IsFindOrder = True

                    break



            except Exception as e:
                print("Exception by First")

        if IsFindOrder == True:
            break

#해당 봇의 모든 주문데이터를 취소하는 로직!
def AllDelAutoLimitOrder(bot_name):

    bot_path_file_path = "/var/autobot/BotOrderListPath.json"

    #각 봇 별로 들어가 있는 자동 주문 리스트!!!
    BotOrderPathList = list()
    try:
        with open(bot_path_file_path, 'r') as json_file:
            BotOrderPathList = json.load(json_file)

    except Exception as e:
        print("Exception by First")

    IsFindBot = False
    time.sleep(random.random()*0.01)
    #오토 리미트 주문 데이터가 있는 모든 봇을 순회하며 처리한다!!
    for botOrderPath in BotOrderPathList:

        #이 botOrderPath는 각 봇의 고유한 경로 (리미트 오토 주문들이 저장되어 있는 파일 경로)
        print("----->" , botOrderPath)

        AutoOrderList = list()

        try:
            with open(botOrderPath, 'r') as json_file:
                AutoOrderList = json.load(json_file)

        except Exception as e:
            print("Exception by First")


        #해당 봇의 읽어온 주문 데이터들을 순회합니다.
        for AutoLimitData in AutoOrderList:

            if AutoLimitData['BotName'] == bot_name:
                print("DELETE ", bot_name , " ORDER ->" , AutoLimitData['Id'])
                DelAutoLimitOrder(AutoLimitData['Id'])
                IsFindBot = True
        

        if IsFindBot == True:
            break



############################################################################################################################################################

#종가 데이터를 가지고 오는데 신규 상장되서 이전 데이터가 없다면 신규 상장일의 정보를 리턴해준다!
def GetCloseData(df,st):
    
    if len(df) < abs(st):
        return df['close'].iloc[-len(df)] 
    else:
        return df['close'].iloc[st] 
        

#넘어온 종목 코드 리스트에 해당 종목이 있는지 여부를 체크하는 함수!
def CheckStockCodeInList(stock_code_list,find_code):
    InOk = False
    for stock_code in stock_code_list:
        if stock_code == find_code:
            InOk = True
            break

    return InOk

        

############################################################################################################################################################

#이동평균선 수치를 구해준다 첫번째: 일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetMA(ohlcv,period,st):
    close = ohlcv["close"]
    ma = close.rolling(period).mean()
    return float(ma.iloc[st])


#RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetRSI(ohlcv,period,st):
    delta = ohlcv["close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    RS = _gain / _loss
    return float(pd.Series(100 - (100 / (1 + RS)), name="RSI").iloc[st])


#볼린저 밴드를 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
#차트와 다소 오차가 있을 수 있습니다.
def GetBB(ohlcv,period,st,uni = 2.0):
    dic_bb = dict()

    ohlcv = ohlcv[::-1]
    ohlcv = ohlcv.shift(st + 1)
    close = ohlcv["close"].iloc[::-1]

    unit = uni
    bb_center=numpy.mean(close[len(close)-period:len(close)])
    band1=unit*numpy.std(close[len(close)-period:len(close)])

    dic_bb['ma'] = float(bb_center)
    dic_bb['upper'] = float(bb_center + band1)
    dic_bb['lower'] = float(bb_center - band1)

    return dic_bb

