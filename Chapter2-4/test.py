import KIS_Common as Common
import KIS_API_Helper_US as KisUS
#import KIS_API_Helper_KR as KisKR

import pprint
import time

#통합증거금을 사용하시는 분은 강의 영상을 잘 봐주세요!!

#REAL 실계좌 VIRTUAL 모의 계좌
Common.SetChangeMode("VIRTUAL") 


#현재 장이 열렸는지 여부
if KisUS.IsMarketOpen() == True:
    print("Maket is Open!!")
else:
    print("Maket is Closed!!")



print("                                     ")
print("------------------------------------")
print("                                     ")


#내 잔고 확인
pprint.pprint(KisUS.GetBalance())
#pprint.pprint(KisKR.GetBalance())

#통합 증거금용 잔고 확인
#pprint.pprint(Common.GetBalanceKrwTotal())

print("                                     ")
print("------------------------------------")
print("                                     ")

#내 보유 주식 리스트 확인
pprint.pprint(KisUS.GetMyStockList())



print("                                     ")
print("------------------------------------")
print("                                     ")


stock_code = "AAPL" #애플 종목코드

current_price = KisUS.GetCurrentPrice(stock_code)

#애플의 현재 가격 
print(current_price)


print("                                     ")
print("------------------------------------")
print("                                     ")



#애플 1주 현재가로 지정가 매수
pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,1,current_price))

print("                                     ")
print("------------------------------------")
print("                                     ")



#시장가는 없는데 시장가 효과로 매수하려면???

buy_price = current_price * 1.1

#애플 2주를 현재가보다 10%나 높은금액에 매수하겠다고 주문을 넣으면??
pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,2,buy_price))
#바로 주문이 체결되는데 시장가로 체결되는걸 볼 수 있음

print("                                     ")
print("------------------------------------")
print("                                     ")


#모의 계좌는 지연 체결이 되며 3초정도 기다렸다고 주문이 완전히 체결된다는 보장은 없어요!!
time.sleep(3.0)



sell_price = current_price * 1.1

#애플 1주 10%위에 지정가 매도 주문
pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,1,sell_price))

print("                                     ")
print("------------------------------------")
print("                                     ")





sell_price = current_price * 0.9

#애플 1주 10% 아래에 지정가 매도 주문을 넣으면???
pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,1,sell_price))
#바로 주문이 체결되는데 시장가로 체결되는걸 볼 수 있음

print("                                     ")
print("------------------------------------")
print("                                     ")


#모의 계좌는 지연 체결이 되며 3초정도 기다렸다고 주문이 완전히 체결된다는 보장은 없어요!!
time.sleep(3.0)


#전체 주문리스트에서 현재 오픈된 주문을 가져온다
pprint.pprint(KisUS.GetOrderList("","ALL","OPEN"))

print("                                     ")
print("------------------------------------")
print("                                     ")


