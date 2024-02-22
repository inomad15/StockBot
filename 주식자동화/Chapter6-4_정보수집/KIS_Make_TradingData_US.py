# -*- coding: utf-8 -*-
'''

데이터 수집 봇의 추천 crontab 설정
https://blog.naver.com/zacra/223224122535


하다가 잘 안되시면 계속 내용이 추가되고 있는 아래 FAQ를 꼭꼭 체크하시고

주식/코인 자동매매 FAQ
https://blog.naver.com/zacra/223203988739

그래도 안 된다면 구글링 해보시고
그래도 모르겠다면 클래스 댓글, 블로그 댓글, 단톡방( https://blog.naver.com/zacra/223111402375 )에 질문주세요! ^^

클래스 제작 후 전략의 많은 발전이 있었습니다.
백테스팅으로 검증해보고 실제로 제가 현재 돌리는 최신 전략을 완강 후 제 블로그에서 체크해 보셔요!
https://blog.naver.com/zacra

기다릴게요 ^^!

'''
import KIS_Common as Common
import pprint
import json
import line_alert #라인 메세지를 보내기 위함!


Common.SetChangeMode("VIRTUAL")


USStockList = list()
#파일 경로입니다.
US_file_path = "/var/autotrade/UsStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(US_file_path, 'r') as json_file:
        USStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")



line_alert.SendMessage("Make Trading Data US Start!!")


UsTradingDataList = list()


for stock_code in USStockList:


    try:
        print(stock_code, " ..Start.. ")
        
        df = Common.GetOhlcv("US",stock_code)
        pprint.pprint(df)
        
        TradingDataDict = dict()

        TradingDataDict['StockCode'] = stock_code #종목코드
        
        
        TradingDataDict['StockPrice_0'] = float(df['close'].iloc[-1]) #현재가(종가) 
        TradingDataDict['StockPrice_1'] = float(df['close'].iloc[-2]) #전날 종가
        TradingDataDict['StockPrice_2'] = float(df['close'].iloc[-3]) #전전날 종가
        
        
        TradingDataDict['StockRate'] = float(df['change'].iloc[-1]) * 100.0 #등락률!
        
        
        
        
        ############################## 거래대금 #######################################
        TradingDataDict['StockMoney_0'] = float(df['value'].iloc[-1]) #현재 기록된 거래대금
        TradingDataDict['StockMoney_1'] = float(df['value'].iloc[-2]) #그 전날 거래대금
        TradingDataDict['StockMoneyRate'] = TradingDataDict['StockMoney_0'] / TradingDataDict['StockMoney_1'] #전날 거래대금 대비 몇 배인지!
        #############################################################################
        
        
        
        
        ############################## 이동평균 #######################################
        #이동평균...
        try:
            TradingDataDict['StockMA5_0'] = Common.GetMA(df,5,-1) #현재 종가기준 5일 이동평균선
            TradingDataDict['StockMA5_1'] = Common.GetMA(df,5,-2) #그 전 5일 이동평균선
            TradingDataDict['StockMA5_2'] = Common.GetMA(df,5,-3) #그 전전 5일 이동평균선
        except Exception as e:
            TradingDataDict['StockMA5_0'] = 0
            TradingDataDict['StockMA5_1'] = 0
            TradingDataDict['StockMA5_2'] = 0
            
            
            
        
        #이동평균...
        try:
            TradingDataDict['StockMA20_0'] = Common.GetMA(df,20,-1) #현재 종가기준 20일 이동평균선
            TradingDataDict['StockMA20_1'] = Common.GetMA(df,20,-2) #그 전 20일 이동평균선
            TradingDataDict['StockMA20_2'] = Common.GetMA(df,20,-3) #그 전전 20일 이동평균선
        except Exception as e:
            TradingDataDict['StockMA20_0'] = 0
            TradingDataDict['StockMA20_1'] = 0
            TradingDataDict['StockMA20_2'] = 0
            
            
        
        #이동평균...
        try:
            TradingDataDict['StockMA60_0'] = Common.GetMA(df,60,-1) #현재 종가기준 60일 이동평균선
            TradingDataDict['StockMA60_1'] = Common.GetMA(df,60,-2) #그 전 60일 이동평균선
            TradingDataDict['StockMA60_2'] = Common.GetMA(df,60,-3) #그 전전 60일 이동평균선
        except Exception as e:
            TradingDataDict['StockMA60_0'] = 0
            TradingDataDict['StockMA60_1'] = 0
            TradingDataDict['StockMA60_2'] = 0
            
        
        #이동평균...
        try:
            TradingDataDict['StockMA120_0'] = Common.GetMA(df,120,-1) #현재 종가기준 60일 이동평균선
            TradingDataDict['StockMA120_1'] = Common.GetMA(df,120,-2) #그 전 60일 이동평균선
            TradingDataDict['StockMA120_2'] = Common.GetMA(df,120,-3) #그 전전 60일 이동평균선
        except Exception as e:
            TradingDataDict['StockMA120_0'] = 0
            TradingDataDict['StockMA120_1'] = 0
            TradingDataDict['StockMA120_2'] = 0
        #############################################################################     




        
        ############################## RSI #######################################
        #RSI...
        try:
            TradingDataDict['StockRSI_0'] = Common.GetRSI(df,14,-1) #현재 종가기준 RSI14 
            TradingDataDict['StockRSI_1'] = Common.GetRSI(df,14,-2) #그 전 RSI14 
            TradingDataDict['StockRSI_2'] = Common.GetRSI(df,14,-3) #그 전전 RSI14 
        except Exception as e:
            TradingDataDict['StockRSI_0'] = 0
            TradingDataDict['StockRSI_1'] = 0
            TradingDataDict['StockRSI_2'] = 0
        ############################################################################# 
            



        ############################## BB #######################################
        #현재 종가 기준 볼린저 밴드
        try:
            BB_0 = Common.GetBB(df,20,-1)
            TradingDataDict['StockBB_Middle_0'] = BB_0['ma']
            TradingDataDict['StockBB_Upper_0'] = BB_0['upper']
            TradingDataDict['StockBB_Lower_0'] = BB_0['lower']
            
        except Exception as e:
            TradingDataDict['StockBB_Middle_0'] = 0
            TradingDataDict['StockBB_Upper_0'] = 0
            TradingDataDict['StockBB_Lower_0'] = 0
            
            
        #그전 종가 기준 볼린저 밴드
        try:
            BB_1 = Common.GetBB(df,20,-2)
            TradingDataDict['StockBB_Middle_1'] = BB_1['ma']
            TradingDataDict['StockBB_Upper_1'] = BB_1['upper']
            TradingDataDict['StockBB_Lower_1'] = BB_1['lower']
            
        except Exception as e:
            TradingDataDict['StockBB_Middle_1'] = 0
            TradingDataDict['StockBB_Upper_1'] = 0
            TradingDataDict['StockBB_Lower_1'] = 0
            
            
        #그전전 종가 기준 볼린저 밴드
        try:
            BB_2 = Common.GetBB(df,20,-3)
            TradingDataDict['StockBB_Middle_2'] = BB_2['ma']
            TradingDataDict['StockBB_Upper_2'] = BB_2['upper']
            TradingDataDict['StockBB_Lower_2'] = BB_2['lower']
            
        except Exception as e:
            TradingDataDict['StockBB_Middle_2'] = 0
            TradingDataDict['StockBB_Upper_2'] = 0
            TradingDataDict['StockBB_Lower_2'] = 0
            
        ############################################################################# 
        
        UsTradingDataList.append(TradingDataDict)
        
        pprint.pprint(TradingDataDict)
            

        print(stock_code, " ..Done.. ")

    except Exception as e:
        print("Exception ", e)

print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
pprint.pprint(UsTradingDataList)

print("--------------------------------------------------------")


#파일 경로입니다.
Us_data_file_path = "/var/autotrade/UsTradingDataList.json"
#파일에 리스트를 저장합니다
with open(Us_data_file_path, 'w') as outfile:
    json.dump(UsTradingDataList, outfile)


line_alert.SendMessage("Make Stock Trading Data US Done!!" + str(len(UsTradingDataList)))

