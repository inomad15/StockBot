#-*-coding:utf-8 -*-


import KIS_Common as Common
import pandas as pd
import json
import pprint

'''
import talib
import numpy as np
import tulipy as ti
'''
#pip3 install tulipy

Common.SetChangeMode("VIRTUAL") 

stock_code = "027410"

df = Common.GetOhlcv("KR",stock_code) #일봉 데이터 

#############################################################################
#  지표 사용 예제  골든크로스~!!!   

print("stock_code: ", stock_code)

#골든 크로스 예제~!
StockMA5_1 = Common.GetMA(df,5,-2)
StockMA5_2 = Common.GetMA(df,5,-3)

StockMA20_1 = Common.GetMA(df,20,-2)
StockMA20_2 = Common.GetMA(df,20,-3)

print("StockMA5_1 ", StockMA5_1)
print("StockMA20_1 ", StockMA20_1)
print("StockMA5_2 ", StockMA5_2)
print("StockMA20_2 ", StockMA20_2)

if StockMA5_2 < StockMA20_2 and StockMA5_1 > StockMA20_1:
    print("골든 크로스!!!!")
else:
    print("골든 크로스 아님 !!!!")
    
    
    
#트레이딩 데이터 읽어서~
KrTradingDataList = list()
#파일 경로입니다.
korea_file_path = "/var/autotrade/KrTradingDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KrTradingDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")
    
    

df_tr = pd.DataFrame(KrTradingDataList)

#골든 크로스
df_tr = df_tr[df_tr.StockMA5_1 < df_tr.StockMA20_1].copy()
df_tr = df_tr[df_tr.StockMA5_0 > df_tr.StockMA20_0].copy()

pprint.pprint(df_tr)

#############################################################################



'''

#############################################################################
#    새로운 지표 사용 예제  골든크로스~!!! 

#MACD값을 구해줍니다!
#MACD함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 macd는 MACD값, macd_siginal값이 시그널값, ocl이 오실레이터 값이 됩니다
print("\n------------- MACD -------------------")
macd_before = Common.GetMACD(df,-2) #이전캔들의 MACD
print("before - MACD:",macd_before['macd'], ", MACD_SIGNAL:", macd_before['macd_siginal'],", ocl:", macd_before['ocl'])
print("-----------------------------------------------")
macd = Common.GetMACD(df,-1) #현재캔들의 MACD
print("now - MACD:",macd['macd'], ", MACD_SIGNAL:", macd['macd_siginal'],", ocl:", macd['ocl'])
print("-----------------------------------------------\n")



#일목균형표(일목구름) 구해줍니다!
#일목균형표(일목구름)함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 conversion는 전환선, base는 기준선
#huhang_span은 후행스팬, sunhang_span_a는 선행스팬1, sunhang_span_b는 선행스판2 입니다.
print("\n-------------- 일목균형표 --------------------------")
ic_before = Common.GetIC(df,-2) #이전캔들의 일목균형표
print("before - Conversion:",ic_before['conversion'], ", Base:", ic_before['base'],", HuHang_Span:", ic_before['huhang_span'],", SunHang_Span_a:", ic_before['sunhang_span_a'],", SunHang_Span_b:", ic_before['sunhang_span_b'])

print("-----------------------------------------------")
ic = Common.GetIC(df,-1) #현재캔들의 일목균형표
print("now - Conversion:",ic['conversion'], ", Base:", ic['base'],", HuHang_Span:", ic['huhang_span'],", SunHang_Span_a:", ic['sunhang_span_a'],", SunHang_Span_b:", ic['sunhang_span_b'])
print("-----------------------------------------------\n")




print("\n------------- 스토캐스틱 ------------------")
#이전 캔들의 스토캐스틱
Stoch_dic_before = Common.GetStoch(df,5,-2)
print("before - fast_k:",Stoch_dic_before['fast_k'],", slow_d:", Stoch_dic_before['slow_d'])

print("-----------------------------------------------")
#현재 캔들의 스토캐스틱
Stoch_dic_now = Common.GetStoch(df,5,-1)
print("now - fast_k:",Stoch_dic_now['fast_k'],", slow_d:", Stoch_dic_now['slow_d'])
print("-----------------------------------------------\n")

#############################################################################

'''


'''

#############################################################################
#  TA-LIB 예시  


integer = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
print(integer[-1],integer[-2]) #현재 캔들 기준의 값과 이전 캔들 기준의 값
print(integer.to_string())



#볼린저 밴드 값을 가져온다.
upperband, middleband, lowerband = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

print("--------------------BBANDS-------------------------")
#이전 캔들의 값
print(upperband[-2],middleband[-2],lowerband[-2])

#현재 캔들의 값(변동 중...)
print(upperband[-1],middleband[-1],lowerband[-1])
print("---------------------------------------------------")




print("-------------------CCI-------------------------")
real = talib.CCI(df['high'],df['low'],df['close'], timeperiod=20)
print(real[-1], real[-2]) #현재 캔들 기준의 값과 이전 캔들 기준의 값





print("-------------------STOCHRSI--------------------------")



fastk, fastd = talib.STOCHRSI(df['close'], timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0)
print(fastk[-2],fastd[-2])
print(fastk[-1],fastd[-1])



rsi = talib.RSI(df['close'], timeperiod=14)
rsinp = rsi.values
rsinp = rsinp[np.logical_not(np.isnan(rsinp))]
fastk, fastd = ti.stoch(rsinp, rsinp, rsinp, 14, 3, 3)

print("--", fastk[-2],fastd[-2])
print("--", fastk[-1],fastd[-1])


print("---------------------------------------------------")

#############################################################################
'''