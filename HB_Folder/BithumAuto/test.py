import pybithumb
import datetime
import pytz
import pandas as pd
import ccxt
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키
import line_alert

from cryptography.fernet import Fernet

#암호화 복호화 클래스
class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Bithumb_ApiKey = simpleEnDecrypt.decrypt(my_key.bithumb_apikey)
Bithumb_Secret = simpleEnDecrypt.decrypt(my_key.bithumb_secret)

# Bithumb API 연결 설정
bithumb = ccxt.bithumb({
    'apiKey': Bithumb_ApiKey,
    'secret': Bithumb_Secret,
})

mybithumb = pybithumb.Bithumb(Bithumb_ApiKey, Bithumb_Secret)

import requests
import time  # Api-Nonce를 생성하기 위해 사용

# API 정보
api_key = Bithumb_ApiKey  # 실제 API 키로 대체
api_secret = Bithumb_Secret  # 실제 API 시크릿으로 대체

# API Nonce 값 (현재 시각 ms 단위)
api_nonce = str(int(time.time() * 1000))

# API 서명 생성 (이 부분은 빗썸의 서명 생성 방식에 따라 달라질 수 있음)
api_sign = ...  # Api-Nonce와 Api-Secret을 사용하여 서명을 생성하는 로직

# 요청 헤더
headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "Api-Key": api_key,
    "Api-Nonce": api_nonce,
    "Api-Sign": api_sign
}

# 요청 URL 및 파라미터
url = "https://api.bithumb.com/info/balance"
payload = {"currency": "BTC"}

# API 요청 및 응답
response = requests.post(url, data=payload, headers=headers)

# 응답 출력
print(response.text)
