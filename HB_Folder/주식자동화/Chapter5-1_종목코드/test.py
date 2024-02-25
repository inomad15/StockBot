import KIS_Common as Common
import KIS_API_Helper_KR as KisKR
import json
import pandas as pd
import pprint

Common.SetChangeMode("REAL")

KoreaStockList = list()
#파일 경로입니다.
korea_file_path = "/var/autobot/KrStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KoreaStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")
    
    
for stock_code in KoreaStockList:
    print(stock_code, KisKR.GetStockName(stock_code))
    
    
    


























