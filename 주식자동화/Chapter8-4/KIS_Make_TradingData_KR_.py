# -*- coding: utf-8 -*-
'''
추천 crontab 설정은 아래 포스팅을 꼭 체크해 보세요!
https://blog.naver.com/zacra/223224122535


하다가 잘 안되시면 계속 내용이 추가되고 있는 아래 FAQ를 꼭꼭 체크하시고

주식/코인 자동매매 FAQ
https://blog.naver.com/zacra/223203988739

그래도 안 된다면 구글링 해보시고
그래도 모르겠다면 클래스 댓글, 블로그 댓글, 단톡방( https://blog.naver.com/zacra/223111402375 )에 질문주세요! ^^

클래스 제작 완료 후 많은 시간이 흘렀고 그 사이 전략에 많은 발전이 있었습니다.
제가 직접 투자하고자 백테스팅으로 검증하여 더 안심하고 있는 자동매매 전략들을 블로그에 공개하고 있으니
완강 후 꼭 블로그&유튜브 심화 과정에 참여해 보세요! 기다릴께요!!

아래 빠른 자동매매 가이드 시간날 때 완독하시면 방향이 잡히실 거예요!
https://blog.naver.com/zacra/223086628069


'''
import KIS_Common as Common
import pprint
import json
import line_alert #라인 메세지를 보내기 위함!


Common.SetChangeMode("VIRTUAL")


KoreaStockList = list()
#파일 경로입니다.
korea_file_path = "/var/autobot/KrStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KoreaStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")



line_alert.SendMessage("Make Trading Data Korea Start!!")


KrTradingDataList = list()


for stock_code in KoreaStockList:


    try:
        print(stock_code, " ..Start.. ")
        
        df = Common.GetOhlcv("KR",stock_code)
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
        
        



        ############################## MACD #######################################
        #현재 종가 MACD
        try:
            MACD_0 = Common.GetMACD(df,-1)
            TradingDataDict['StockMACD_macd_0'] = MACD_0['macd']
            TradingDataDict['StockMACD_macd_signal_0'] = MACD_0['macd_siginal']
            TradingDataDict['StockMACD_ocl_0'] = MACD_0['ocl']
            
        except Exception as e:
            TradingDataDict['StockMACD_macd_0'] = 0
            TradingDataDict['StockMACD_macd_signal_0'] = 0
            TradingDataDict['StockMACD_ocl_0'] = 0
            
            
        #그전 종가 기준
        try:
            MACD_1 = Common.GetMACD(df,-2)
            TradingDataDict['StockMACD_macd_1'] = MACD_1['macd']
            TradingDataDict['StockMACD_macd_signal_1'] = MACD_1['macd_siginal']
            TradingDataDict['StockMACD_ocl_1'] = MACD_1['ocl']
            
        except Exception as e:
            TradingDataDict['StockMACD_macd_1'] = 0
            TradingDataDict['StockMACD_macd_signal_1'] = 0
            TradingDataDict['StockMACD_ocl_1'] = 0
            
        #그전 종가 기준
        try:
            MACD_2 = Common.GetMACD(df,-3)
            TradingDataDict['StockMACD_macd_2'] = MACD_2['macd']
            TradingDataDict['StockMACD_macd_signal_2'] = MACD_2['macd_siginal']
            TradingDataDict['StockMACD_ocl_2'] = MACD_2['ocl']
            
        except Exception as e:
            TradingDataDict['StockMACD_macd_2'] = 0
            TradingDataDict['StockMACD_macd_signal_2'] = 0
            TradingDataDict['StockMACD_ocl_2'] = 0
            
            
        ############################################################################# 
        
        KrTradingDataList.append(TradingDataDict)
        
        pprint.pprint(TradingDataDict)
            

        print(stock_code, " ..Done.. ")

    except Exception as e:
        print("Exception ", e)

print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
pprint.pprint(KrTradingDataList)

print("--------------------------------------------------------")


#파일 경로입니다.
kr_data_file_path = "/var/autobot/KrTradingDataList.json"
#파일에 리스트를 저장합니다
with open(kr_data_file_path, 'w') as outfile:
    json.dump(KrTradingDataList, outfile)


line_alert.SendMessage("Make Stock Trading Data Korea Done!!" + str(len(KrTradingDataList)))

