import yaml

import json
import requests

from datetime import datetime, timedelta
from pytz import timezone

stock_info = None

#설정 파일 정보를 읽어 옵니다.
with open('/var/autotrade/myStockInfo.yaml', encoding='UTF-8') as f:
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

