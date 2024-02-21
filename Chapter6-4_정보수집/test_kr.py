import KIS_Common as Common
import KIS_API_Helper_KR as KisKR

import json
import pandas as pd
import pprint


'''

{'StockBB_Lower_0': 6581.003759402924,
  'StockBB_Lower_1': 6552.671013694215,
  'StockBB_Lower_2': 6582.497025582643,
  'StockBB_Middle_0': 8177.0,
  'StockBB_Middle_1': 8204.5,
  'StockBB_Middle_2': 8263.5,
  'StockBB_Upper_0': 9772.996240597076,
  'StockBB_Upper_1': 9856.328986305785,
  'StockBB_Upper_2': 9944.502974417357,
  'StockCode': '159010',
  'StockMA120_0': 7975.825,
  'StockMA120_1': 7960.375,
  'StockMA120_2': 7952.616666666667,
  'StockMA20_0': 8177.0,
  'StockMA20_1': 8204.5,
  'StockMA20_2': 8263.5,
  'StockMA5_0': 7814.0,
  'StockMA5_1': 7490.0,
  'StockMA5_2': 7318.0,
  'StockMA60_0': 8818.533333333333,
  'StockMA60_1': 8804.3,
  'StockMA60_2': 8801.85,
  'StockMoneyRate': 4.431365419184734,
  'StockMoney_0': 13377274050.0,
  'StockMoney_1': 3018770240.0,
  'StockPrice_0': 8740.0,
  'StockPrice_1': 7850.0,
  'StockPrice_2': 7750.0,
  'StockRSI_0': 56.45551302846315,
  'StockRSI_1': 45.08730524435424,
  'StockRSI_2': 43.54967984603703,
  'StockRate': 11.337579617834393},



'''
Common.SetChangeMode("VIRTUAL")

KrTradingDataList = list()
#파일 경로입니다.
korea_file_path = "/var/autobot/KrTradingDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KrTradingDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")
    
    

df = pd.DataFrame(KrTradingDataList)


#아래 예들은 단순 예시들로 다양한 조건을 만들수 있습니다 
'''
# 정배열...
df = df[df.StockPrice_0 > df.StockMA5_0].copy()
df = df[df.StockMA5_0 > df.StockMA20_0].copy()
df = df[df.StockMA20_0 > df.StockMA60_0].copy()
df = df[df.StockMA60_0 > df.StockMA120_0].copy()
'''

'''
#역배열
df = df[df.StockPrice_0 < df.StockMA5_0].copy()
df = df[df.StockMA5_0 < df.StockMA20_0].copy()
df = df[df.StockMA20_0 < df.StockMA60_0].copy()
df = df[df.StockMA60_0 < df.StockMA120_0].copy()
'''

'''
#RSI지표가 30에서 빠져나왔을 때
df = df[df.StockRSI_1 < 30.0].copy()
df = df[df.StockRSI_0 > 30.0].copy()
'''

'''
#볼밴 하단밖에서 안으로 들어 왔을 때 
df = df[df.StockBB_Lower_1 > df.StockPrice_1].copy()
df = df[df.StockBB_Lower_0 < df.StockPrice_0].copy()
'''


df = df[df.StockMoney_0 > 50000000000].copy()
df = df[df.StockMoneyRate > 5.0].copy()




df = df.sort_values(by="StockRate", ascending=False)
pprint.pprint(df)





#한국 퀀트 시스템 개발할때 한국 시총이나 재무지표가 들어 있는 파일
KrStockDataList = list()
#파일 경로입니다.
StockData_file_path = "/var/autobot/KrStockDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(StockData_file_path, 'r') as json_file:
        KrStockDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")



df_sd = pd.DataFrame(KrStockDataList)



TopCnt = 20
NowCnt = 0

#추가로 읽어온 재무정보(시총,영업이익등)으로 필터하지 않을 때 예 
for idx, row in df.iterrows():
    
    if NowCnt < TopCnt:

        print("-----------------------------------")
        print(KisKR.GetStockName(row['StockCode']), "(",row['StockCode'],")")
        print("거래대금: ", row['StockMoney_0'])
        print("전날대비 거래대금: ", row['StockMoneyRate'])
        print("등락률 : ", round(row['StockRate'],2))
        
        for idx2, row2 in df_sd.iterrows():
            
            if row['StockCode'] == row2['StockCode']:
                pprint.pprint(row2)
                
                        
                print("시총: ", row2['StockMarketCap'])
                print("현재가 : ", row2['StockNowPrice'])
                print("영업이익 : ", row2['StockOperProfit'])
                print("EPS(주당 순이익) : ", row2['StockEPS'])
                print("BPS(주당 순자산(-부채))) : ", row2['StockBPS'])
                print("PER(현재가 / 주당 순자산) : ", row2['StockPER'])
                print("PBR(현재가 / 주당 순자산) : ", row2['StockPBR'])
                print("ROE(EPS / BPS), ROA, GP/A 등 : ", row2['StockROE'])
                
                break
        
        

        print("-----------------------------------")


        NowCnt += 1



#추가로 읽어온 재무정보(시총,영업이익등)으로 필터할때 예
#영업이익 0 이상인 걸로 체크!
'''
for idx, row in df.iterrows():
    
    if NowCnt < TopCnt:

        for idx2, row2 in df_sd.iterrows():
            
            if row['StockCode'] == row2['StockCode']:
                #pprint.pprint(row2)
                

                if float(row2['StockOperProfit']) > 0:
                    
                                
                    print("-----------------------------------")
                    print(KisKR.GetStockName(row['StockCode']), "(",row['StockCode'],")")
                    print("거래대금: ", row['StockMoney_0'])
                    print("전날대비 거래대금: ", row['StockMoneyRate'])
                    print("등락률 : ", round(row['StockRate'],2))
                    
                                                
                    print("시총: ", row2['StockMarketCap'])
                    print("현재가 : ", row2['StockNowPrice'])
                    print("영업이익 : ", row2['StockOperProfit'])
                    print("EPS(주당 순이익) : ", row2['StockEPS'])
                    print("BPS(주당 순자산(-부채))) : ", row2['StockBPS'])
                    print("PER(현재가 / 주당 순자산) : ", row2['StockPER'])
                    print("PBR(현재가 / 주당 순자산) : ", row2['StockPBR'])
                    print("ROE(EPS / BPS), ROA, GP/A 등 : ", row2['StockROE'])
                
        
                    NowCnt += 1
                    
                break
        
        

        print("-----------------------------------")


'''  
        