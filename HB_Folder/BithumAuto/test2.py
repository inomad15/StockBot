import pybithumb
import datetime
import pytz
import pandas as pd
import ccxt
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

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

url = "https://api.bithumb.com/info/balance"

payload = { "currency": "BTC" }
headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "Api-Key": "2cec93709e9c7bd0352f4bf3e559f9ff",
    "Api-Nonce": "현재시각(ms)",
    "Api-Sign": "상세 가이드 참고"
}

response = requests.post(url, data=payload, headers=headers)

print(response.text)