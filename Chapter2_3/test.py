import KIS_Common as Common
import KIS_API_Helper_KR as KisKR

import pprint
import time

#REAL 실계좌 VIRTUAL 모의 계좌
Common.SetChangeMode("VIRTUAL") 

#현재 장이 열렸는지 여부
if KisKR.IsMarketOpen() == True:
    print("Maket is Open!!")
else:
    print("Maket is Closed!!")



print("                                     ")
print("------------------------------------")
print("                                     ")


#내 잔고 확인
pprint.pprint(KisKR.GetBalance())

print("                                     ")
print("------------------------------------")
print("                                     ")

#내 보유 주식 리스트 확인
pprint.pprint(KisKR.GetMyStockList())


print("                                     ")
print("------------------------------------")
print("                                     ")


stock_code = "005930" #삼성전자 종목코드

current_price = KisKR.GetCurrentPrice(stock_code)

#삼성전자의 현재 가격 
print(current_price)


print("                                     ")
print("------------------------------------")
print("                                     ")



#삼성전자 2주 시장가 매수
pprint.pprint(KisKR.MakeBuyMarketOrder(stock_code,2))

print("                                     ")
print("------------------------------------")
print("                                     ")

#영상엔 안 나와 있지만
#모의계좌의 경우 시장가 매수의 경우에도 딜레이가 걸리는 경우가 있습니다.
#즉 지연체결 문제가 있다는 점을 알고 계세요~!! 
#3초 정도 쉬어주지만 3초 후에 주문 체결이 완료 된다는 보장은 없습니다!
time.sleep(3.0)


#삼성전자 1주 시장가 매도
pprint.pprint(KisKR.MakeSellMarketOrder(stock_code,1))

print("                                     ")
print("------------------------------------")
print("                                     ")


buy_price = current_price * 0.9

#삼성전자 1주 지정가 매수
pprint.pprint(KisKR.MakeBuyLimitOrder(stock_code,1,buy_price))

print("                                     ")
print("------------------------------------")
print("                                     ")




sell_price = current_price * 1.1

#삼성전자 1주 지정가 매도 
pprint.pprint(KisKR.MakeSellLimitOrder(stock_code,1,sell_price))

print("                                     ")
print("------------------------------------")
print("                                     ")




#전체 주문리스트에서 현재 오픈된 주문을 가져온다
pprint.pprint(KisKR.GetOrderList("","ALL","OPEN"))

print("                                     ")
print("------------------------------------")
print("                                     ")



