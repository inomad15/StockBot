#-*-coding:utf-8 -*-

import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit
import line_alert

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

# 암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

# 암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

# 업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

ticker = ['KRW-BTC']
# 내가 매수할 총 코인 개수
MaxCoinCnt = 3.0

# 처음 매수할 비중(퍼센트)
FirstRate = 10.0
# 추가 매수할 비중 (퍼센트)
WaterRate = 10.0

# 내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()
TotalMoeny = myUpbit.GetTotalMoney(balances) #총 원금
TotalRealMoney = myUpbit.GetTotalRealMoney(balances) #총 평가금액
# 내 총 수익율
TotalRevenue = (TotalRealMoney - TotalMoeny) * 100.0/ TotalMoeny
# 코인당 매수할 최대 매수금액
CoinMaxMoney = TotalMoeny / MaxCoinCnt
# 1차 매수 금액 
FirstEnterMoney = CoinMaxMoney / 100.0 * FirstRate 
# 2차 매수 금액 
WaterEnterMoeny = CoinMaxMoney / 100.0 * WaterRate
 # 보유 코인 수익율
revenu_rate = myUpbit.GetRevenueRate(balances,ticker)
# 보유 코인 총 매수금액
NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)
won = float(upbit.get_balance("KRW"))
coinamount = float(upbit.get_balance(ticker))

print(balances)

if myUpbit.IsHasCoin(balances,ticker) == True:
    print(f"- Coin Total Money : {NowCoinTotalMoney:,.0f}")
    print(coinamount)

# df15 = pyupbit.get_ohlcv(ticker,interval="minute15") #5분봉 데이타를 가져온다.
# print(df15)
# # RSI지표
# rsi15_min_before = myUpbit.GetRSI(df15,14,-3)
# rsi15_min = myUpbit.GetRSI(df15,14,-2)

# # MACD 지표
# macd_before3, macd_s_before3 = myUpbit.get_macd(df15, -4)
# macd_before2, macd_s_before2 = myUpbit.get_macd(df15, -3)
# macd_now, macd_s_now = myUpbit.get_macd(df15, -2)

# print("2024-03-01 updated version")
# print("-----------------------------------------------")
# print (f"Total Money : {myUpbit.GetTotalMoney(balances):,.0f}")
# print (f"Total Real Money : {myUpbit.GetTotalRealMoney(balances):,.0f}")
# print (f"Total Revenue : {TotalRevenue:.2f}")
# print("-----------------------------------------------")
# print (f"CoinMaxMoney : {CoinMaxMoney:,.0f}")
# print (f"FirstEnterMoney : {FirstEnterMoney:,.0f}")
# print (f"WaterEnterMoeny : {WaterEnterMoeny:,.0f}")

# print(f"- Coin Total Money : {NowCoinTotalMoney:,.0f}")
# print(f"# Coin Amount : {coinamount:.2f}")
# print(f"# Remaining Won : {won:,.0f}")
# print(f"{ticker} price : {df15['close'].iloc[-1]:,.0f}")
# print(f"macd : {macd_before3:,.0f} -> {macd_before2:,.0f} -> {macd_now:,.0f}")
# print(f"macd_signal : {macd_s_now:,.0f}")
# print(f"- Recently RSI : {rsi15_min_before:.0f} -> {rsi15_min:.0f}")
# print(f"- Now Revenue : {revenu_rate:.2f}")