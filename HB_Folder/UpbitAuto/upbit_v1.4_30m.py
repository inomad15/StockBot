#-*-coding:utf-8 -*-

import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit
import line_alert
import telegram
import asyncio

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

# 암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

# 암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

# 업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

# 텔레그램 비동기 함수 정의
async def send_telegram_message():
    bot = telegram.Bot(token='6785990806:AAF4Khbpp7FWFjdjmgkiLu0ulSfDyGMTOk8')
    await bot.send_message(chat_id="5165569281", text=text_contents)

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

won = float(upbit.get_balance("KRW"))

print("2024-03-17 updated version")
print("-----------------------------------------------")
print (f"Total Money : {myUpbit.GetTotalMoney(balances):,.0f}")
print (f"Total Real Money : {myUpbit.GetTotalRealMoney(balances):,.0f}")
print (f"Total Revenue : {TotalRevenue:.2f}")
print (f"Remaining Won : {won:,.0f}")
print("-----------------------------------------------")
print (f"CoinMaxMoney : {CoinMaxMoney:,.0f}")
print (f"FirstEnterMoney : {FirstEnterMoney:,.0f}")
print (f"WaterEnterMoeny : {WaterEnterMoeny:,.0f}")

text_contents = f"업비트 \n총 매수금액 : {myUpbit.GetTotalMoney(balances):,.0f}  \n\
총 평가금액: {myUpbit.GetTotalRealMoney(balances):,.0f} \n수익률 : {TotalRevenue:.2f}"
asyncio.run(send_telegram_message())

# 매수 대상 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-XRP']
Tickers = pyupbit.get_tickers("KRW")
    

for ticker in Tickers:
    try: 
    ##### 보유 중인 코인 ####################################################################
        
        if myUpbit.IsHasCoin(balances,ticker) == True:
            
            print("-----------------------------------------------")
            print("##### Having Coin :",ticker)

            time.sleep(0.05)
            df30 = pyupbit.get_ohlcv(ticker,interval="minute30") #30분봉 데이타를 가져온다.
            
            # RSI지표
            rsi30_min_before = myUpbit.GetRSI(df30,14,-3)
            rsi30_min = myUpbit.GetRSI(df30,14,-2)

            # MACD 지표
            macd_before3, macd_s_before3 = myUpbit.get_macd(df30, -4)
            macd_before2, macd_s_before2 = myUpbit.get_macd(df30, -3)
            macd_now, macd_s_now = myUpbit.get_macd(df30, -2)

            # 보유 코인 수익율
            revenu_rate = myUpbit.GetRevenueRate(balances,ticker)
            # 보유 코인 총 매수금액
            NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)
            
            time.sleep(0.05)
            
            #원화 잔고를 가져온다
            
            coinamount = float(upbit.get_balance(ticker))
            now_price = df30['close'].iloc[-1]
            now_eval_money = now_price * coinamount
            
            print(f"- Total Buy Money : {NowCoinTotalMoney:,.0f}")
            print(f"- Now evaluation Money : {now_eval_money:,.0f}")
            print(f"- Now Revenue : {revenu_rate:.2f}")
            print(f"- Coin Amount : {coinamount:.2f}")
            
            print(f"{ticker} price : {df30['close'].iloc[-1]:,.0f}")
            print(f"macd : {macd_before3:,.0f} -> {macd_before2:,.0f} -> {macd_now:,.0f}")
            print(f"macd_signal : {macd_s_now:,.0f}")
            print(f"Recently RSI : {rsi30_min_before:.0f} -> {rsi30_min:.0f}")
            
            text_contents = f"{ticker} \n매수금액 : {NowCoinTotalMoney:,.0f} \n평가금액: {now_eval_money:,.0f} \n수익률 : {revenu_rate:.2f}"
            asyncio.run(send_telegram_message())
            
            text_contents = f"MACD : {macd_before3:,.0f} -> {macd_before2:,.0f} -> {macd_now:,.0f}\nMACD_signal : {macd_s_now:,.0f} \nRSI : {rsi30_min_before:.0f} -> {rsi30_min:.0f}"
            asyncio.run(send_telegram_message())
            
        ### MACD 하락전환 시 수익권일 때 분할 매도 ###
            if macd_now > macd_s_now and macd_before3 < macd_before2 and macd_before2 > macd_now and revenu_rate >= 2.0:
                print("!!!!!!!!!!!!!!! Revenue Success Sell Coin! !!!!!!!!!!!!!!!!!!!")

                # 현재 걸려있는 지정가 주문을 취소한다.
                myUpbit.CancelCoinOrder(upbit,ticker)

                # 최대코인매수금액의 1/10보다 작다면 전체 시장가 매도 
                if NowCoinTotalMoney < (CoinMaxMoney / 10.0):
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,coinamount)
                    text_contents = f"업비트 30분봉 MACD 하락전환 {ticker} 전액 매도"          
                    asyncio.run(send_telegram_message())
                    
                # 최대코인매수금액의 1/10보다 크다면 1회 매수금액으로 시장가 매도 
                else:
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,coinamount/10)
                    text_contents = f"업비트 30분봉 MACD 하락전환 {ticker} 일부 매도"          
                    asyncio.run(send_telegram_message())                   

                #팔았으면 원화를 다시 가져올 필요가 있다.
                won = float(upbit.get_balance("KRW"))
        
        ### RSI 하락전환 시 수익권일 때 분할 매도 ###
            if rsi30_min_before >= 70.0 and rsi30_min < 70.0 and revenu_rate >= 2.0:
                print("!!!!!!!!!!!!!!! Revenue Success Sell Coin! !!!!!!!!!!!!!!!!!!!")

                # 현재 걸려있는 지정가 주문을 취소한다.
                myUpbit.CancelCoinOrder(upbit,ticker)

                # 최대코인매수금액의 1/10보다 작다면 전체 시장가 매도 
                if NowCoinTotalMoney < (CoinMaxMoney / 10.0):
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,coinamount)
                    text_contents = f"업비트 30분봉 RSI 하락전환 {ticker} 전액 매도"          
                    asyncio.run(send_telegram_message())
                    
                # 최대코인매수금액의 1/10보다 크다면 1회 매수금액으로 시장가 매도 
                else:
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,coinamount/10)
                    text_contents = f"업비트 30분봉 RSI 하락전환 {ticker} 일부 매도"          
                    asyncio.run(send_telegram_message())                   

                #팔았으면 원화를 다시 가져올 필요가 있다.
                won = float(upbit.get_balance("KRW"))   

            print("------------------------------------")
            print("##### Try Add Buy :",ticker)
            
            time.sleep(0.05)
            df30 = pyupbit.get_ohlcv(ticker,interval="minute30") #30분봉 데이타를 가져온다.

            #RSI지표를 구한다.
            rsi30_min_before = myUpbit.GetRSI(df30,14,-3)
            rsi30_min = myUpbit.GetRSI(df30,14,-2)

            print(f"- Recently RSI : {rsi30_min_before:.0f} -> {rsi30_min:.0f}")


        ### RSI지표 30선 위로 상향돌파 시 추가매수 ###
            if rsi30_min_before <= 30.0 and rsi30_min > 30.0 and myUpbit.GetHasCoinCnt(balances) <= MaxCoinCnt :
                print("!!!!!!!!!!!!!! ADD Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                 #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                text_contents = f"업비트 30분봉 RSI 상승전환 {ticker} 추가매수"          
                asyncio.run(send_telegram_message())
                
            time.sleep(0.05)

            df30 = pyupbit.get_ohlcv(ticker,interval="minute30") #30분봉 데이타를 가져온다.

            # MACD 지표
            macd_before3, macd_s_before3 = myUpbit.get_macd(df30, -4)
            macd_before2, macd_s_before2 = myUpbit.get_macd(df30, -3)
            macd_now, macd_s_now = myUpbit.get_macd(df30, -2)
            
            print(f"macd_signal : {macd_s_now:,.0f}")
            print(f"macd : {macd_before3:,.0f} -> {macd_before2:,.0f} -> {macd_now:,.0f}")

        ### MACD 상승전환 시 추가매수 ###
            if rsi30_min_before < 40 and macd_now < macd_s_now and macd_before3 > macd_before2 and macd_before2 < macd_now and myUpbit.GetHasCoinCnt(balances) <= MaxCoinCnt :
                print("!!!!!!!!!!!!!! DANTA DANTA ADD Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                text_contents = f"업비트 30분봉 MACD 상승전환 {ticker} 추가매수"          
                asyncio.run(send_telegram_message())
                
        #     #30분봉 기준 5일선 값을 구한다.
        #     ma5_before3 = myUpbit.GetMA(df30,5,-4)
        #     ma5_before2 = myUpbit.GetMA(df30,5,-3)
        #     ma5 = myUpbit.GetMA(df30,5,-2)

        #     #30분봉 기준 20일선 값을 구한다.
        #     ma20 = myUpbit.GetMA(df30,20,-2)

        #     print(f"ma20 : {ma20:.0f}")
        #     print(f"ma5 : {ma5_before3:.0f} -> {ma5_before2:.0f} -> {ma5_before3:.0f}")


        # ### 5일 이평선 상승전환 시 추가매수 ###
        #     if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and myUpbit.GetHasCoinCnt(balances) <= MaxCoinCnt :
        #         print("!!!!!!!!!!!!!! DANTA DANTA First Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
        #         #시장가 매수를 한다.
        #         balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
        #         line_alert.SendMessage(f"30분봉 MA 상승전환 {ticker} 추가매수")

        
    ### 신규 매수 ###########################################################################
        else:

            #관심종목 이외의 코인은 스킵
            if myUpbit.CheckCoinInList(LovelyCoinList,ticker) == False:
                continue

            print("------------------------------------")
            print("##### Try Fisrt Buy :",ticker)
            
            time.sleep(0.05)
            df30 = pyupbit.get_ohlcv(ticker,interval="minute30") #30분봉 데이타를 가져온다.

            #RSI지표를 구한다.
            rsi30_min_before = myUpbit.GetRSI(df30,14,-3)
            rsi30_min = myUpbit.GetRSI(df30,14,-2)

            print(f"- Recently RSI : {rsi30_min_before:.0f} -> {rsi30_min:.0f}")


        ### RSI지표 30선 위로 상향돌파 시 신규매수 ###
            if rsi30_min_before <= 30.0 and rsi30_min > 30.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!! First Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                 #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                text_contents = f"업비트 30분봉 RSI 상승전환 {ticker} 신규매수"          
                asyncio.run(send_telegram_message())
                
            time.sleep(0.05)
            df30 = pyupbit.get_ohlcv(ticker,interval="minute30") #30분봉 데이타를 가져온다.

            # MACD 지표
            macd_before3, macd_s_before3 = myUpbit.get_macd(df30, -4)
            macd_before2, macd_s_before2 = myUpbit.get_macd(df30, -3)
            macd_now, macd_s_now = myUpbit.get_macd(df30, -2)
            
            print(f"macd_signal : {macd_s_now:,.0f}")
            print(f"macd : {macd_before3:,.0f} -> {macd_before2:,.0f} -> {macd_now:,.0f}")

        ### MACD 상승전환 시 신규매수 ###
            if rsi30_min_before < 40 and macd_now < macd_s_now and macd_before3 > macd_before2 and macd_before2 < macd_now and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!! DANTA DANTA First Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
                #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                text_contents = f"업비트 30분봉 MACD 상승전환 {ticker} 신규매수"          
                asyncio.run(send_telegram_message())
                            
            
        #     #30분봉 기준 5일선 값을 구한다.
        #     ma5_before3 = myUpbit.GetMA(df30,5,-4)
        #     ma5_before2 = myUpbit.GetMA(df30,5,-3)
        #     ma5 = myUpbit.GetMA(df30,5,-2)

        #     #30분봉 기준 20일선 값을 구한다.
        #     ma20 = myUpbit.GetMA(df30,20,-2)

        #     print(f"ma20 : {ma20:.0f}")
        #     print(f"ma5 : {ma5_before3:.0f} -> {ma5_before2:.0f} -> {ma5_before3:.0f}")


        # ### 5일 이평선 상승전환 시 신규매수 ###
        #     if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
        #         print("!!!!!!!!!!!!!! DANTA DANTA First Buy GoGoGo !!!!!!!!!!!!!!!!!!!!!!!")
        #         #시장가 매수를 한다.
        #         balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
        #         line_alert.SendMessage(f"30분봉 MA 상승전환 {ticker} 신규매수")
                    

    except Exception as e:
        print("error:", e)



























