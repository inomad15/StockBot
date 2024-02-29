#-*-coding:utf-8 -*-
'''

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
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit
import line_alert


import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

#내가 매수할 총 코인 개수
MaxCoinCnt = 5.0

#처음 매수할 비중(퍼센트)
FirstRate = 10.0
#추가 매수할 비중 (퍼센트)
WaterRate = 10.0

#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()
TotalMoeny = myUpbit.GetTotalMoney(balances) #총 원금
TotalRealMoney = myUpbit.GetTotalRealMoney(balances) #총 평가금액
#내 총 수익율
TotalRevenue = (TotalRealMoney - TotalMoeny) * 100.0/ TotalMoeny
#코인당 매수할 최대 매수금액
CoinMaxMoney = TotalMoeny / MaxCoinCnt
#처음에 매수할 금액 
FirstEnterMoney = CoinMaxMoney / 100.0 * FirstRate 
#그 이후 매수할 금액 
WaterEnterMoeny = CoinMaxMoney / 100.0 * WaterRate

print("2024-02-29 updated version")
print("-----------------------------------------------")
print (f"Total Money : {myUpbit.GetTotalMoney(balances):.0f}")
print (f"Total Real Money : {myUpbit.GetTotalRealMoney(balances):.0f}")
print (f"Total Revenue : {TotalRevenue:.2f}")
print("-----------------------------------------------")
print (f"CoinMaxMoney : {CoinMaxMoney:.0f}")
print (f"FirstEnterMoney : {FirstEnterMoney:.0f}")
print (f"WaterEnterMoeny : {WaterEnterMoeny:.0f}")

#매수 대상 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-XRP']
Tickers = pyupbit.get_tickers("KRW")

for ticker in Tickers:
    try: 
        #이미 매수된 코인
        if myUpbit.IsHasCoin(balances,ticker) == True:
            
            print("-----------------------------------------------")
            print("##### Having Coin :",ticker)

            time.sleep(0.05)
            df5 = pyupbit.get_ohlcv(ticker,interval="minute5") #5분봉 데이타를 가져온다.
            
            #RSI지표를 구한다.
            rsi5_min_before = myUpbit.GetRSI(df5,14,-3)
            rsi5_min = myUpbit.GetRSI(df5,14,-2)

            macd_before3, macd_s_before3 = myUpbit.get_macd(df5, -4)
            macd_before2, macd_s_before2 = myUpbit.get_macd(df5, -3)
            macd_now, macd_s_now = myUpbit.get_macd(df5, -2)

            #수익율을 구한다.
            revenu_rate = myUpbit.GetRevenueRate(balances,ticker)
            #현재 코인의 총 매수금액
            NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)
            time.sleep(0.05)
            
            #원화 잔고를 가져온다
            won = float(upbit.get_balance("KRW"))
            print(f"# Remaining Won : {won:.0f}")
            print(f"{ticker} price : {df5['close'].iloc[-1]}")
            print(f"- Recently RSI : {rsi5_min_before:.0f} -> {rsi5_min:.0f}")
            print(f"- Now Revenue : {revenu_rate:.2f}")
            print(f"- Coin Total Money : {NowCoinTotalMoney:.0f}")
    
            
            #5분봉 기준 RSI지표 70 이상이면서 수익권일때 분할 매도를 한다.
            if macd_now > macd_s_now and macd_before3 < macd_before2 and macd_before2 > macd_now)rsi5_min >= 70.0 and revenu_rate >= 3.0:
                print("!!!!!!!!!!!!!!! Revenue Success Sell Coin! !!!!!!!!!!!!!!!!!!!")

                #현재 걸려있는 지정가 주문을 취소한다. 왜? 아래 매수매도 로직이 있으니깐 
                myUpbit.CancelCoinOrder(upbit,ticker)

                #최대코인매수금액의 1/10보다 작다면 전체 시장가 매도 
                if NowCoinTotalMoney < (CoinMaxMoney / 10.0):
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))
                    line_alert.SendMessage(f"5분봉 매도신호 {ticker} 전액 매도")
                #최대코인매수금액의 1/10보다 크다면 1회 매수금액으로 시장가 매도 
                else:
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,FirstEnterMoney)
                    line_alert.SendMessage(f"5분봉 매도신호 {ticker} 매도")

                #팔았으면 원화를 다시 가져올 필요가 있다.
                won = float(upbit.get_balance("KRW"))
               

            print("------------------------------------")
            print("##### Try Add Buy :",ticker)
            
            time.sleep(0.05)
            df5 = pyupbit.get_ohlcv(ticker,interval="minute5") #5분봉 데이타를 가져온다.


            #RSI지표를 구한다.
            rsi5_min_before = myUpbit.GetRSI(df5,14,-3)
            rsi5_min = myUpbit.GetRSI(df5,14,-2)


            print(f"- Recently RSI : {rsi5_min_before:.0f} -> {rsi5_min:.0f}")


            #5분봉 기준 RSI지표 30 이하에서 빠져나오면서 아직 매수한 코인이 MaxCoinCnt보다 작다면 매수 진행!
            if rsi5_min_before <= 30.0 and rsi5_min > 30.0 and myUpbit.GetHasCoinCnt(balances) <= MaxCoinCnt :
                print("!!!!!!!!!!!!!! ADD Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                 #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                line_alert.SendMessage(f"5분봉 매수신호 {ticker} 추가매수")


            time.sleep(0.05)
            df5 = pyupbit.get_ohlcv(ticker,interval="minute5") #5분봉 데이타를 가져온다.

            #5분봉 기준 5일선 값을 구한다.
            ma5_before3 = myUpbit.GetMA(df5,5,-4)
            ma5_before2 = myUpbit.GetMA(df5,5,-3)
            ma5 = myUpbit.GetMA(df5,5,-2)

            #5분봉 기준 20일선 값을 구한다.
            ma20 = myUpbit.GetMA(df5,20,-2)

            print(f"ma20 : {ma20:.0f}")
            print(f"ma5 : {ma5_before3:.0f} -> {ma5_before2:.0f} -> {ma5_before3:.0f}")


            #5일선이 20일선 밑에 있을 때 5일선이 상승추세로 꺽이면 매수를 진행하자!!
            if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!! DANTA DANTA ADD Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                line_alert.SendMessage("5분봉 매수신호")

        
        #아직 매수안한 코인 ###########################################################################
        else:

            #관심종목 이외의 코인은 스킵
            if myUpbit.CheckCoinInList(LovelyCoinList,ticker) == False:
                continue

            print("------------------------------------")
            print("----- Try Fisrt Buy ----- :",ticker)
            
            time.sleep(0.05)
            df5 = pyupbit.get_ohlcv(ticker,interval="minute5") #5분봉 데이타를 가져온다.


            #RSI지표를 구한다.
            rsi5_min_before = myUpbit.GetRSI(df5,14,-3)
            rsi5_min = myUpbit.GetRSI(df5,14,-2)


            print(f"- Recently RSI : {rsi5_min_before:.0f} -> {rsi5_min:.0f}")


            #5분봉 기준 RSI지표 30 이하에서 빠져나오면서 아직 매수한 코인이 MaxCoinCnt보다 작다면 매수 진행!
            if rsi5_min_before <= 30.0 and rsi5_min > 30.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!! First Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                 #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                line_alert.SendMessage("5분봉 매수신호")


            time.sleep(0.05)
            df5 = pyupbit.get_ohlcv(ticker,interval="minute5") #5분봉 데이타를 가져온다.

            #5분봉 기준 5일선 값을 구한다.
            ma5_before3 = myUpbit.GetMA(df5,5,-4)
            ma5_before2 = myUpbit.GetMA(df5,5,-3)
            ma5 = myUpbit.GetMA(df5,5,-2)

            #5분봉 기준 20일선 값을 구한다.
            ma20 = myUpbit.GetMA(df5,20,-2)

            print(f"ma20 : {ma20:.0f}")
            print(f"ma5 : {ma5_before3:.0f} -> {ma5_before2:.0f} -> {ma5_before3:.0f}")


            #5일선이 20일선 밑에 있을 때 5일선이 상승추세로 꺽이면 매수를 진행하자!!
            if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!! DANTA DANTA First Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                line_alert.SendMessage("5분봉 매수신호")
                    

    except Exception as e:
        print("error:", e)



























