# -*- coding: utf-8 -*-

import FinanceDataReader as fdr
import json

from pykrx import stock

import line_alert #라인 메세지를 보내기 위함!


line_alert.SendMessage("Make Stock Code List Start!!")


KoreaStockList = list()

#에러 여부!
Is_Error = False

try:

    print("<-------GET KOSPI--------->")
    kospi_list = stock.get_market_ticker_list(market="KOSPI")
    print("<-------GET KOSDAQ------->")
    kosdaq_list = stock.get_market_ticker_list(market="KOSDAQ")
    print("<------------------------>")

    KoreaStockList = kospi_list + kosdaq_list
    print(KoreaStockList)


    print("count--> ", len(KoreaStockList))


    #2천개가 안될리가 없다 
    if len(KoreaStockList) < 2000:
        Is_Error = True


except Exception as e:
    print("Exception by First")
    Is_Error = True



if Is_Error == True:


    print("<-------GET KOSPI--------->")
    df_kr1 = fdr.StockListing('KOSPI')
    print("<-------GET KOSDAQ------->")
    df_kr2= fdr.StockListing('KOSDAQ')
    print("<------------------------>")

    OriKoreaStockList = df_kr1['Symbol'].to_list() + df_kr2['Symbol'].to_list()

    print("before count--> ", len(OriKoreaStockList))

    for v in OriKoreaStockList:
        if v not in KoreaStockList: #중복 제거한다!
            #글자수 가 6자리인 것만 가지고 온다. 숫자로만 되어 있거나 5개는 숫자 끝에 1개는 영문으로 된것만 가지고 온다.
            if len(v) == 6 and (v.isdigit() == True or v[0:-1].isdigit() == True): 
                KoreaStockList.append(v)
    print(KoreaStockList)

    print("count--> ", len(KoreaStockList))



    result = "First Try Failed But Make Stock Code Done KR: "+ str(len(KoreaStockList))
    print(result)
    line_alert.SendMessage(result)

else:
    result = "Make Stock Code Done KR: "+ str(len(KoreaStockList))
    print(result)
    line_alert.SendMessage(result)



#파일 경로입니다.
korea_file_path = "/var/autotrade/KrStockCodeList.json"
#파일에 리스트를 저장합니다
with open(korea_file_path, 'w') as outfile:
    json.dump(KoreaStockList, outfile)



print("##########################################################")

print("<------------------------>")
df_us1 = fdr.StockListing('NASDAQ')
print("<------------------------>")
df_us2 = fdr.StockListing('NYSE')
print("<------------------------>")
df_us3 = fdr.StockListing('AMEX')
print("<------------------------>")


OriUSStockList = df_us1['Symbol'].to_list() + df_us2['Symbol'].to_list() + df_us3['Symbol'].to_list()

print("before count--> ", len(OriUSStockList))

USStockList = list()
for v in OriUSStockList:
    if v not in USStockList: #중복 제거한다!
        if v.find(' ') == -1 and v.find('.') == -1: #공백이나 쩜이 있는 코드는 일단 제외시킨다!
            USStockList.append(v)
print(USStockList)

print("count--> ", len(USStockList))

#파일 경로입니다.
us_file_path = "/var/autotrade/UsStockCodeList.json"
#파일에 리스트를 저장합니다
with open(us_file_path, 'w') as outfile:
    json.dump(USStockList, outfile)


result = "Make Stock Code Done US: "+ str(len(USStockList))
print(result)
line_alert.SendMessage(result)

