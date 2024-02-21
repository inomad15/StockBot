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
import time
import KIS_API_Helper_KR as KisKR
import line_alert #라인 메세지를 보내기 위함!



Common.SetChangeMode("REAL")


KoreaStockList = list()
#파일 경로입니다.
korea_file_path = "/var/autotrade/KrStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KoreaStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")



line_alert.SendMessage("Make Stock Data Korea Start!!")


KrStockDataList = list()


for stock_code in KoreaStockList:

    try:


        print(stock_code, " ..Start.. ")

        data = KisKR.GetCurrentStatus(stock_code)

        
        
        if data['StockNowStatus'] == '00' or data['StockNowStatus'] == '55' or data['StockNowStatus'] == '57' : 

            if data['StockMarket'] == "ETN" or data['StockMarket'] == "ETF" or (float(data['StockPER']) == 0 and float(data['StockPBR']) == 0 and float(data['StockEPS']) == 0  and float(data['StockBPS']) == 0) :
                print("Maybe...ETF..ETN.. ")
            else:

                KrStockDataList.append(data)
                
                pprint.pprint(data)
            

            
        time.sleep(0.2)

        print(stock_code, " ..Done.. ")

    except Exception as e:
        print("Exception ", e)




print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
pprint.pprint(KrStockDataList)

print("--------------------------------------------------------")


#파일 경로입니다.
kr_data_file_path = "/var/autotrade/KrStockDataList.json"
#파일에 리스트를 저장합니다
with open(kr_data_file_path, 'w') as outfile:
    json.dump(KrStockDataList, outfile)



line_alert.SendMessage("Make Stock Data Korea Done!!" + str(len(KrStockDataList)))

