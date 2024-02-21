import KIS_Common as Common
import KIS_API_Helper_KR as KisKR
import json
import pandas as pd
import pprint



stockcode = "224060"

url = "https://finance.naver.com/item/main.naver?code=" + stockcode
dfs = pd.read_html(url,encoding='euc-kr')

#pprint.pprint(dfs[4])

data_dict = dfs[4]


data_keys = list(data_dict.keys())

for key in data_keys:
    if stockcode in key:
        print(key)
        print(data_dict[key][5]) #매출액
        print(data_dict[key][6]) #영업이익
        print(data_dict[key][8]) #영업이익증가율
        print(data_dict[key][11]) #ROE
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$")




'''
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

df = df[df.StockEPS > 0].copy()


df = df.sort_values(by="StockMarketCap")
pprint.pprint(df)

print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

pprint.pprint(df[0:20])
'''
