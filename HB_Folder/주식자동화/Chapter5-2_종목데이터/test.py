import KIS_Common as Common
import KIS_API_Helper_KR as KisKR
import json
import pandas as pd
import pprint



TargetStockList = list()
#파일 경로입니다.
korea_file_path = "/var/autobot/KrStockDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        TargetStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")


print("TotalStockCodeCnt: " , len(TargetStockList))


df = pd.DataFrame(TargetStockList)

df = df[df.StockMarketCap >= 50.0].copy()
df = df[df.StockDistName != "금융"].copy()
df = df[df.StockDistName != "금융업"].copy()  
df = df[df.StockDistName != "외국증권"].copy()




df = df.sort_values(by="StockMarketCap")
pprint.pprint(df)

print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

pprint.pprint(df[0:20])





