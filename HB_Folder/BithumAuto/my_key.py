#-*-coding:utf-8 -*-

'''
여러분의 시크릿 키와 엑세스 키를 
ende_key.py에 있는 키를 활용해서 암호화한 값을 넣으세요

마찬가지 방법으로 아래 로직을 실행하시면 됩니다.. (ende_key.py 참조)

from cryptography.fernet import Fernet

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

         

simpleEnDecrypt = SimpleEnDecrypt(b'NcUgge50agCYGXpJmpcxsE5_0do84kKNdI6DsG-iwm8=') #ende_key.py 에 있는 키를 넣으세요

access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경


print("access_key: ", simpleEnDecrypt.encrypt(access))

print("scret_key: ", simpleEnDecrypt.encrypt(secret))

simpleEnDecrypt = SimpleEnDecrypt(b'e60FoElc9gROZFnq7HPkN5-BtoTzJw0CEQQgI2xUBS4=')
ori_str = "1bbd29a05b0b99f72a26a3cde71f8817"
print(ori_str)
de_str = simpleEnDecrypt.encrypt(ori_str)
print(de_str)
re_str = simpleEnDecrypt.decrypt(de_str)
print(re_str)

'''

bithumb_apikey = "gAAAAABlwNifnWLY4n79CgP7lxnb8-gTpP2-D3gr1lzc3w9zVTFDHwxR5i2A3HEQTRfISWYsO3zD_BmLR3GcH6tLKqufQaQ95_nKNlVzKQFdY-BV5Pc9wopZLYYCB8DUszg0m-PdqHL2"          # 본인 값으로 변경
bithumb_secret = "gAAAAABlwNj1cPFn_D9a47jy0fMytvK51SxnK6G5hmjPr8Am6xCCfwlTUdcI4QvdZIjNsfW7kSEE8pzHOHCdL5TVj5_D815ZQKWM4PcNGIQAFlO1iCESkgsUwbksAV4wv3sRoO4AGPuA"          # 본인 값으로 변경
