# -*- coding: utf-8 -*-
'''

아래 구글 드라이브 링크에 권한 요청을 해주세요!
이후 업데이트 사항은 여기서 실시간으로 편하게 다운로드 하시면 됩니다. (클래스 구독이 끝나더라도..)
https://drive.google.com/drive/folders/1mKGGR355vmBCxB7A3sOOSh8-gQs1CiMF?usp=drive_link




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

import KIS_API_Helper_US as KisUS
import KIS_API_Helper_KR as KisKR
import line_alert
import time
import json
import pprint
import random

SELL_LIMIT_DATE = 0
BUY_LIMIT_DATE = 1

Common.SetChangeMode('VIRTUAL') 

IsKRMarketOpen = False
IsUSMarketOpen = False

try:

    IsKRMarketOpen = KisKR.IsMarketOpen() 
    IsUSMarketOpen = KisUS.IsMarketOpen() 

except Exception as e:

    Common.SetChangeMode('REAL') 
    IsKRMarketOpen = KisKR.IsMarketOpen() 
    IsUSMarketOpen = KisUS.IsMarketOpen() 



#시간 정보를 읽는다
time_info = time.gmtime()

#현재 서버기준 시간 0이면 아침 9시다!
NowHour = time_info.tm_hour
print("NOW HOUR: ", NowHour)


bot_path_file_path = "/var/autotrade/BotOrderListPath.json"

#각 봇 별로 들어가 있는 자동 주문 리스트!!!
BotOrderPathList = list()
try:
    with open(bot_path_file_path, 'r') as json_file:
        BotOrderPathList = json.load(json_file)

except Exception as e:
    print("Exception by First")


time.sleep(random.random()*0.01)
#오토 리미트 주문 데이터가 있는 모든 봇을 순회하며 처리한다!!
for botOrderPath in BotOrderPathList:

    #이 botOrderPath는 각 봇의 고유한 경로 (리미트 오토 주문들이 저장되어 있는 파일 경로)
    print("----->" , botOrderPath)

    AutoOrderList = list()

    try:
        with open(botOrderPath, 'r') as json_file:
            AutoOrderList = json.load(json_file)

    except Exception as e:
        print("Exception by First")


    #해당 봇의 읽어온 주문 데이터들을 순회합니다.
    for AutoLimitData in AutoOrderList:

        try:
            #해당 주문의 계좌를 바라보도록 셋팅 합니다!!
            Common.SetChangeMode(AutoLimitData['NowDist']) 

            #한번 프린트 해줍니다
            print("$$$$$$$$$$$$$$$$$$CHECK$$$$$$$$$$$$$$$$$$")
            pprint.pprint(AutoLimitData)

            #주문이 완료가 안된 미체결 수량이 남아 있는 주문은 이 봇이 실행된 시점에 적절한 처리를 해야 합니다.
            if AutoLimitData['IsDone'] == 'N':
                #KR일 경우
                if AutoLimitData['Area'] == "KR":
                    
                    #장이 열린 경우에만 필요한 처리를 할 수 있어요
                    if IsKRMarketOpen == True:

                        #미체결 수량이 들어갈 변수!
                        GapAmt = 0

                        #내 주식 잔고 리스트를 읽어서 현재 보유 수량 정보를 stock_amt에 넣어요!
                        MyKRStockList = KisKR.GetMyStockList()
                        stock_amt = 0
                        for my_stock in MyKRStockList:
                            if my_stock['StockCode'] == AutoLimitData['StockCode']:
                                stock_amt = int(my_stock['StockAmt'])
                                print(my_stock['StockName'], stock_amt)
                                break

                        #일단 목표로 하는 수량에서 현재 보유수량을 빼줍니다.
                        #이는 종목의 주문이 1개일 때 유효합니다. 왜 그런지 그리고TargetAmt값이 뭔지는 KIS_Common의 AutoLimitDoAgain함수를 살펴보세요
                        GapAmt = abs(AutoLimitData['TargetAmt'] - stock_amt)
                                      
                        Is_In = False
                        Is_Except = False
                        try:

                            #주문리스트를 읽어 온다! 퇴직연금계좌 IRP계좌에서는 이 정보를 못가져와 예외가 발생합니다!!
                            OrderList = KisKR.GetOrderList(AutoLimitData['StockCode'])

                            print(len(OrderList) , " <--- Order OK!!!!!!")
                            
                            #주문 번호를 이용해 해당 주문을 찾습니다!!!
                            for OrderInfo in OrderList:
                                if OrderInfo['OrderNum'] == AutoLimitData['OrderNum'] and float(OrderInfo["OrderNum2"]) == float(AutoLimitData['OrderNum2']):

                                    #현재 주문이 취소된 상태이다!
                                    if OrderInfo["OrderSatus"] == "Close" or AutoLimitData['IsCancel'] == 'Y':
                                        #그런데 미체결 수량이 있다!
                                        if OrderInfo["OrderAmt"] != OrderInfo["OrderResultAmt"]:
                                            #그 수량 만큼 지정가 주문을 나중에 걸어줘야 되니 미체결 수량을 구합니다!!!
                                            GapAmt = abs(OrderInfo["OrderResultAmt"] - OrderInfo["OrderAmt"])

                                            print("GapAmt", GapAmt , " OrderInfo['OrderResultAmt'] ", OrderInfo["OrderResultAmt"] )
                                            
                                            #최초 주문들어갈 때 주문 수량이 음수였다면 매도 주문이니 음수로 바꿔줍니다
                                            if AutoLimitData['OrderAmt'] < 0:
                                                GapAmt *= -1

                                            Is_In = True

                                        #미체결 수량이 없다면 완료처리 합니다!!!
                                        else:
                                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                            #미체결 수량이 없다면 완료!!!
                                            AutoLimitData['IsDone'] = 'Y'
                                            with open(botOrderPath, 'w') as outfile:
                                                json.dump(AutoOrderList, outfile)
                                    break

                        except Exception as e:
                            #예외 발생!
                            Is_Except = True
                            print("Exception", e)

                        #예외가 발생했다면 아마 퇴직연금 계좌일 거에요
                        if Is_Except == True or Is_In == False:
                            
                            #이 경우는 위에서 구한 GapAmt = abs(AutoLimitData['TargetAmt'] - stock_amt) <- 이거 기준으로 처리를 합니다.

                            #목표 수량과 현재 주식 잔고가 같지 않다면 미체결 수량이 있다고 판단!
                            if AutoLimitData['TargetAmt'] != stock_amt:
                                
                                #최초 주문이 0보다 작은 매도 주문이었다면 -1로!
                                if AutoLimitData['OrderAmt'] < 0:
                                    GapAmt *= -1

                            #목표수량과 현재 주식잔고가 같다면 완료된 주문으로 판단!!!
                            else:
                                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                #미체결 수량이 없다면 완료!!!
                                AutoLimitData['IsDone'] = 'Y'
                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)


                        #유효한 주문이 들어간지 체크합니다.
                        OrderOk = "OK"
                        #주문번호가 0이라는 이야기는 돈이 모자라서 KIS_Common의 AutoLimitDoAgain함수의 매수주문 자체가 실패한 경우입니다 
                        if int(AutoLimitData['OrderNum2']) == 0:
                            #그럴때는 주문이 유효하지 않은 상태니 취소상태를 Y로 바꿔줍니다.
                            AutoLimitData['IsCancel'] = 'Y'
                            #주문도 정상이 아니니 NO가 됩니다
                            OrderOk = "NO"

                        str_msg = AutoLimitData["Id"] + KisKR.GetStockName(AutoLimitData['StockCode']) + " 현재주식잔고: " +  str(stock_amt) + " 주문수량:" +  str(AutoLimitData["OrderAmt"]) + " 남은주문수량:" + str(GapAmt) + " 주문들어갔는지:" + str(OrderOk)
                       
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        print(str_msg)
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


                        #미체결 수량이 0이 아니다 즉 매수나 매도를 해야될 필요가 있는 경우입니다
                        if GapAmt != 0:
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Fail<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                            
                            #주문 취소 상태이거나 매시간 주문을 갱신해줘야 하는 DAY_END류의 옵션일 경우 이안으로 들어오게 합니다
                            if AutoLimitData['IsCancel'] == 'Y' or AutoLimitData['StockType'] == "DAY_END" or AutoLimitData['StockType'] == "DAY_END_TRY_ETF":


                                print(">>>>>>>>>>>>>>>>>>>>> GOGO ORDER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                                #line_alert.SendMessage("재주문!! " + str_msg)

                                #원 주문 정보를 저장해 둡니다. 왜냐면 혹시나 주문 수정 주문이 취소가 되었을때 주문번호가 0이되어 주문이 취소상태가 되는데
                                #원주문은 유효한 상태니 이를 막고자한 처리 입니다.
                                #이는 아래 변수를 트래킹 해보시면 이해하실 수 있습니다.
                                ORI_OrderNum = AutoLimitData["OrderNum"]
                                ORI_OrderNum2 = AutoLimitData["OrderNum2"]   
                                ORI_OrderTime = AutoLimitData["OrderTime"]   

                                #수정 주문 인지 여부를 체크합니다!
                                #이는 혹시나 예외처리가 발생해 주문을 취소상태로 만들건지 여부로 위 원주문정보를 받아오는 부분과 맥락을 함께 합니다.
                                IS_MODIFY_ORDER = False


                                try:
                                    OrderData = None


                                    #TARGET_FIX : 
                                    # 첫 주문한 지정가격이 절대 변하지 않는다. 체결되기 전까지 매일 매일 재주문!!!
                                    if AutoLimitData['StockType'] == "TARGET_FIX":
                                        #사야된다
                                        if GapAmt > 0:
                                            OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                            
                                        #팔아야 된다!
                                        else:
                                            OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])

                                    #DAY_END : 
                                    #지정가로 주문을 넣지만 하루안에 주문을 끝낸다.  장중에 매시간마다 해당 주문을 체크해서 현재가로 지정가 주문을 변경 (체결 확률 업! ) 
                                    #마지막 장 끝나기 전 시간에도 수량이 남아있다면 이때는 시장가로 마무리 !
                                    elif AutoLimitData['StockType'] == "DAY_END":

                                        #현재 주문이 취소 상태라면 날이 바뀐 케이스다 or 돈이 모잘라서 매수 주문이 아직 안들어간 첫 케이스
                                        #이때는 그냥 현재가로 지정가 주문을 넣어준다!!
                                        if AutoLimitData['IsCancel'] == 'Y':

                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']))
            
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']))
                                    
                                        #주문이 유효한 상태라면 주문을 정정해준다
                                        else:
                                            
                                            #수정 주문일 테니 이걸 True로 바꿔줍니다.
                                            IS_MODIFY_ORDER = True

                                            #매수는 오후 3시 매도는 오후 2시 매도가 미리 끝나도록 유도한다!
                                            TargetHour = 6
                                            if GapAmt < 0:
                                                TargetHour = 5

                                            print("-NowHour----", NowHour, "  TargetHour ", TargetHour)
                                            #현재 시간이 타겟 시간과 일치하면 시장가로 마무리할 시간입니다!
                                            if NowHour == TargetHour:


                                                #사야된다
                                                if GapAmt > 0:

                                                    #일단 현재 주문 취소를 하고
                                                    CancelOK = False
                                                    try:

                                                        OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                                       
                                                        print("Cancel OK!",OrderData["OrderNum2"] ) #이부분으로 예외를 발생시킵니다 주문이 정상이라면 예외가 발생되지 않습니다.

                                                        CancelOK = True
                                                    except Exception as e:
                                                        print("Cancel Failed")
                                                        CancelOK = False
                                                    
                                                    #시장가 주문을 넣어준다
                                                    if CancelOK == True:
                                                        OrderData = KisKR.MakeBuyMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))


                                                #팔아야 된다!
                                                else:

                                                    #일단 현재 주문 취소를 하고
                                                    CancelOK = False
                                                    try:
                                                        OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                                        print("Cancel OK!",OrderData["OrderNum2"] )  #이부분으로 예외를 발생시킵니다 주문이 정상이라면 예외가 발생되지 않습니다.

                                                        CancelOK = True
                                                    except Exception as e:
                                                        print("Cancel Failed")
                                                        CancelOK = False
                                                    
                                                    #시장가 주문을 넣어준다
                                                    if CancelOK == True:
                                                        OrderData = KisKR.MakeSellMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))
       


                                            #그밖의 경우는 현재가로 주문 정정!
                                            else:
                                                if GapAmt > 0:
                                                    OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"MODIFY","LIMIT","BUY")
                                                else:
                                                    OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"MODIFY","LIMIT","SELL")

                                    #DAY_END_TRY_ETF:
                                    #DAY_END랑 비슷하지만 ETF의 NAV와 괴리율을 고려해서 하루안에 끝내거나 다음 날로 넘김 (클래스 설명 참조)
                                    elif AutoLimitData['StockType'] == "DAY_END_TRY_ETF":

                                        print("GAPAMT : ", GapAmt)

                                        Nav = KisKR.GetETF_Nav(AutoLimitData['StockCode'])
                                        CurrentPrice = KisKR.GetCurrentPrice(AutoLimitData['StockCode'])

                                        FarRate = ((CurrentPrice-Nav) / Nav) * 100.0

                                        #최근 괴리율 절대값 평균
                                        AvgGap = KisKR.GetETFGapAvg(AutoLimitData['StockCode'])

                                        print("ETF NAV: " , Nav," 현재가:", CurrentPrice, " 괴리율:",FarRate , " 괴리율 절대값 평균:", AvgGap)

                                        
                                        #일단 기본은 현재가로 설정합니다!!!
                                        FinalPrice = CurrentPrice

                                        #현재 주문이 취소 상태라면 날이 바뀐 케이스다 or 돈이 모잘라서 매수 주문이 아직 안들어간 첫 케이스
                                        if AutoLimitData['IsCancel'] == 'Y':
                                            print(">#>#>#>#>##>#>#>#>#>##>#>#>#> CANCEL ORDER ", GapAmt)
                                            #사야된다
                                            if GapAmt > 0:

                                                #괴리율이 음수여서 유리할 때나 매수에 불리한 1% 이상일때는 NAV가격으로 주문하는 타이트한 로직이지만 아래 if문을 사용합니다(저는)
                                                #if FarRate <= 0 or (FarRate >= 1.0):


                                                #괴리율이 음수여서 유리할 때나 괴리율평균절대값의 150%보다 큰상황일때  NAV가격으로 주문!
                                                if FarRate <= 0 or (AvgGap * 1.5) < abs(FarRate):
                                                    FinalPrice = Nav
                                                #나머지 상황에선 현재가로 주문!!! 

                                                OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),FinalPrice,False,"YES")
                                                pprint.pprint(OrderData)
            
                                            #팔아야 된다!
                                            else:
                                                #괴리율이 양수여서 유리할 때나 매도에 불리한 -1% 이하일때는 NAV가격으로 주문하는 타이트한 로직이지만 아래 if문을 사용합니다(저는)
                                                #if FarRate >= 0 or (FarRate <= -1.0):


                                                #괴리율이 양수여서 유리할 때나 괴리율평균절대값의 150%보다 큰상황일때  NAV가격으로 주문!
                                                if FarRate >= 0 or (AvgGap * 1.5) < abs(FarRate):
                                                    FinalPrice = Nav
                                                #나머지 상황에선 현재가로 주문!!!

                                                OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),FinalPrice)
                                                pprint.pprint(OrderData)
                                    
                                        #주문이 유효한 상태라면 주문을 정정해준다
                                        else:
                                            IS_MODIFY_ORDER = True

                                            #매수는 오후 3시 매도는 오후 2시 매도가 미리 끝나도록 유도한다!
                                            TargetHour = 6
                                            if GapAmt < 0:
                                                TargetHour = 5

                                            print("-NowHour----", NowHour, "  TargetHour ", TargetHour)

                                            #현재 시간이 타겟 시간과 일치하면 시장가로 마무리할 시간입니다!
                                            if NowHour == TargetHour:
                                                
                                                print(">#>#>#>#>##>#>#>#>#>##>#>#>#> LAST MODIFY")
                                                #사야된다
                                                if GapAmt > 0:

                                                    # 120일 괴리율 절대값 평균의 150%수치보다 현재 괴리율이 작다면 시장가로 매수하게 주문수정
                                                    #if (AvgGap * 1.5) > abs(FarRate):           

                                                        #일단 현재 주문 취소를 하고
                                                        CancelOK = False
                                                        try:

                                                            OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                                            print("Cancel OK!",OrderData["OrderNum2"] )  #이부분으로 예외를 발생시킵니다 주문이 정상이라면 예외가 발생되지 않습니다.

                                                            CancelOK = True
                                                        except Exception as e:
                                                            print("Cancel Failed")
                                                            CancelOK = False
                                                        
                                                        #시장가 주문을 넣어준다
                                                        if CancelOK == True:
                                                            OrderData = KisKR.MakeBuyMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))



                                                    #불리한 경우라면 NAV로 주문수정하고 체결안되면 다음날로...
                                                    #else:
                                                    #    OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),Nav,"MODIFY","LIMIT","BUY")

                                                #팔아야 된다!
                                                else:

                                                    #120일 괴리율 절대값 평균의 150%수치보다 현재 괴리율이 작다면 시장가로 매도하게 주문수정
                                                   # if (AvgGap * 1.5) > abs(FarRate):
                                                        #일단 현재 주문 취소를 하고
                                                        CancelOK = False
                                                        try:
                                                            OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                                            print("Cancel OK!",OrderData["OrderNum2"] )  #이부분으로 예외를 발생시킵니다 주문이 정상이라면 예외가 발생되지 않습니다.

                                                            CancelOK = True
                                                        except Exception as e:
                                                            print("Cancel Failed")
                                                            CancelOK = False
                                                        
                                                        #시장가  주문을 넣어준다
                                                        if CancelOK == True:
                                                            OrderData = KisKR.MakeSellMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))
                                                    #불리한 경우라면 NAV로 주문수정하고 체결안되면 다음날로...
                                                   # else:
                                                    #    OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),Nav,"MODIFY","LIMIT","SELL")


                                            #그밖의 경우는 주문 정정!
                                            else:
                                                print(">#>#>#>#>##>#>#>#>#>##>#>#>#> NORMAL MODIFY")

                                                #사야된다
                                                if GapAmt > 0:
                                                    #괴리율이 음수여서 유리할 때나 괴리율평균절대값의 150%보다 큰상황일때  NAV가격으로 주문!
                                                    if FarRate <= 0 or (AvgGap * 1.5) < abs(FarRate):      #or (FarRate >= 1.0): #매수에 불리한 1% 이상일때는
                                                        FinalPrice = Nav

                                                    OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),FinalPrice,"MODIFY","LIMIT","BUY")

                                                #팔아야 된다!
                                                else:
                                                    #괴리율이 양수여서 유리할 때나 괴리율평균절대값의 150%보다 큰상황일때  NAV가격으로 주문!
                                                    if FarRate >= 0 or (AvgGap * 1.5) < abs(FarRate):     #or (FarRate <= -1.0): #매도에 불리한 -1% 이하일때는 NAV가격으로 주문!         
                                                        FinalPrice = Nav

                                                    OrderData = KisKR.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum'],AutoLimitData['OrderNum2'],abs(GapAmt),FinalPrice,"MODIFY","LIMIT","SELL")

                                    #NORMAL : 
                                    #지정된 카운팅에 해당하는 날 전에는 계속 타겟 가격으로 주문을 넣다가 
                                    #카운팅 날짜 부터는 현재가 그 다음날에는 지정가로 일 단위로 주문을 넣는 루즈한 로직
                                    else:

                                        #매도와 매수날짜 기준을 다르게 해서 매도가 먼저 끝나게 처리합니다!
                                        MAX_LIMIT_DATE = BUY_LIMIT_DATE
                                        if GapAmt < 0:
                                            MAX_LIMIT_DATE = SELL_LIMIT_DATE

                                        #이 로직에 대한 설명은 챕터6-2를 참고하세요!
                                        if MAX_LIMIT_DATE <= AutoLimitData['TryCnt']:

                                            if MAX_LIMIT_DATE + 1 <= AutoLimitData['TryCnt']:

                                                #사야된다
                                                if GapAmt > 0:

                                                    OrderData = KisKR.MakeBuyMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))
                                                #팔아야 된다!
                                                else:
                                                    OrderData = KisKR.MakeSellMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))

                                            else:



                                                #사야된다
                                                if GapAmt > 0:
                                                    OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']))
                
                                                #팔아야 된다!
                                                else:
                                                    OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']))

                                        else:
                                            
                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                                
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                            
                                    
                                    
                                    AutoLimitData['OrderNum'] = OrderData["OrderNum"]
                                    AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]   
                                    AutoLimitData['OrderTime'] = OrderData["OrderTime"]   

                                    #실제 주문이 들어갔을 경우에만!
                                    if int(AutoLimitData['OrderNum2']) != 0:
                                        #그리고 이전 주문이 정상적으로 들어간 경우에만 카운팅!!!
                                        if OrderOk == "OK":
                                            AutoLimitData['TryCnt'] += 1
                                            
                                        AutoLimitData['IsCancel'] = 'N'  


                                except Exception as e:
                                    print("Fail..", e)
                                    #line_alert.SendMessage("주문 실패" + str(e))
                                    #주문이 실패했다

                                    #그런데 수정주문이었다면 원주문은 괜찮은 상태니 여기서 처리를 해줍니다.
                                    if IS_MODIFY_ORDER == True:
                                        
                                        AutoLimitData['OrderNum'] = ORI_OrderNum
                                        AutoLimitData['OrderNum2'] = ORI_OrderNum2
                                        AutoLimitData['OrderTime'] = ORI_OrderTime 

                                    else:

                                        AutoLimitData['OrderNum'] = 0
                                        AutoLimitData['OrderNum2'] = 0
                                        AutoLimitData['OrderTime'] = Common.GetNowDateStr(AutoLimitData['Area'])  + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec) 




                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)
                    
                    
                    
                    #장이 닫혔다면 한국의 모든 주문은 취소되었을 테니 취소 처리를 해줍니다
                    else:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Cancel<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        #장이 안열렸으면 취소처리!
                        AutoLimitData['IsCancel'] = 'Y'
                        with open(botOrderPath, 'w') as outfile:
                            json.dump(AutoOrderList, outfile)
                #US일 경우
                else:
                    #장이 열린 경우에만 필요한 처리를 할 수 있어요
                    if IsUSMarketOpen == True:
                        print("")

                        #미체결 수량이 들어갈 변수!
                        GapAmt = 0

                        #내 주식 잔고 리스트를 읽어서 현재 보유 수량 정보를 stock_amt에 넣어요!
                        MyUSStockList = KisUS.GetMyStockList()
                        stock_amt = 0
                        for my_stock in MyUSStockList:
                            if my_stock['StockCode'] == AutoLimitData['StockCode']:
                                stock_amt = int(my_stock['StockAmt'])
                                break            

                        #일단 목표로 하는 수량에서 현재 보유수량을 빼줍니다.
                        #이는 종목의 주문이 1개일 때 유효합니다. 왜 그런지 그리고TargetAmt값이 뭔지는 KIS_Common의 AutoLimitDoAgain함수를 살펴보세요
                        GapAmt = abs(AutoLimitData['TargetAmt'] - stock_amt)            
                        
                        Is_In = False
                        Is_Except = False
                        try:
                            #주문리스트를 읽어 온다! 모의계좌에서는 미국주식 야간일 때 이 정보를 못가져와 예외가 발생합니다!!
                            OrderList = KisUS.GetOrderList(AutoLimitData['StockCode'])

                            print(len(OrderList) , " <--- Order OK!!!!!!")
                            

                            for OrderInfo in OrderList:
                                if OrderInfo['OrderNum'] == AutoLimitData['OrderNum'] and float(OrderInfo["OrderNum2"]) == float(AutoLimitData['OrderNum2']):
                                    pprint.pprint(OrderInfo)
                                    #현재 주문이 취소된 상태이다!
                                    if OrderInfo["OrderSatus"] == "Close" or AutoLimitData['IsCancel'] == 'Y':
                                        #그런데 미체결 수량이 있다!
                                        if OrderInfo["OrderAmt"] != OrderInfo["OrderResultAmt"]:
                                            #그 수량 만큼 지정가 주문을 걸어준다!
                                            GapAmt = abs(OrderInfo["OrderResultAmt"] - OrderInfo["OrderAmt"])
                                            
                                            #매도 주문의 경우는 음수로 만들어 줍니다
                                            if AutoLimitData['OrderAmt'] < 0:
                                                GapAmt *= -1

                                            Is_In = True
                                        else:
                                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                            #미체결 수량이 없다면 완료!!!
                                            AutoLimitData['IsDone'] = 'Y'
                                            with open(botOrderPath, 'w') as outfile:
                                                json.dump(AutoOrderList, outfile)
                                    break

                        except Exception as e:
                            Is_Except = True
                            print("Exception ORDER!", e)


                        #에외가 발생했다면 아마 모의계좌 야간인 상황입니다. 
                        if Is_Except == True or Is_In == False:

                            #어쩔수 없이 목표수량이랑 현재 수량이 다르다면 미체결로 같다면 체결완료 된 것으로 처리를 합니다!!
                            if AutoLimitData['TargetAmt'] != stock_amt:
                                
                                #최초 주문이 0보다 작은 매도 주문이었다면 -1로!
                                if AutoLimitData['OrderAmt'] < 0:
                                    GapAmt *= -1

                            #체결 완료 처리!!
                            else:
                                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                #미체결 수량이 없다면 완료!!!
                                AutoLimitData['IsDone'] = 'Y'
                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)

                        #유효한 주문이 들어간지 체크합니다.
                        OrderOk = "OK"
                        #주문번호가 0이라는 이야기는 돈이 모자라서 KIS_Common의 AutoLimitDoAgain함수의 매수주문 자체가 실패한 경우입니다 
                        if int(AutoLimitData['OrderNum2']) == 0:
                            #그럴때는 주문이 유효하지 않은 상태니 취소상태를 Y로 바꿔줍니다.
                            AutoLimitData['IsCancel'] = 'Y'
                            #주문도 정상이 아니니 NO가 됩니다
                            OrderOk = "NO"

                            
                        str_msg = AutoLimitData["Id"] +  AutoLimitData['StockCode'] + " 현재주식잔고: " +  str(stock_amt) + " 주문수량:" +  str(AutoLimitData["OrderAmt"]) + " 남은주문수량:" + str(GapAmt) + " 주문들어갔는지:" + str(OrderOk)
                        
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        print(str_msg)
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

                        #미체결 수량이 0이 아니다 즉 매수나 매도를 해야될 필요가 있는 경우입니다
                        if GapAmt != 0:
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Fail<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                            
                            #주문 취소 상태이거나 매시간 주문을 갱신해줘야 하는 DAY_END 옵션일 경우 이안으로 들어오게 합니다
                            if AutoLimitData['IsCancel'] == 'Y' or AutoLimitData['StockType'] == "DAY_END" :

                                print(">>>>>>>>>>>>>>>>>>>>> GOGO ORDER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                                #line_alert.SendMessage("재주문!! " + str_msg)
                                    
                                #원 주문 정보를 넣습니다
                                ORI_OrderNum = AutoLimitData["OrderNum"]
                                ORI_OrderNum2 = AutoLimitData["OrderNum2"]   
                                ORI_OrderTime = AutoLimitData["OrderTime"]   

                                #수정 주문 인지 여부
                                IS_MODIFY_ORDER = False


                                try:

                                    OrderData = None


                                    #TARGET_FIX : 
                                    # 첫 주문한 지정가격이 절대 변하지 않는다. 체결되기 전까지 매일 매일 재주문!!!
                                    if AutoLimitData['StockType'] == "TARGET_FIX":
                                        #사야된다
                                        if GapAmt > 0:
                                            OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                            
                                        #팔아야 된다!
                                        else:
                                            OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])

                                    #DAY_END : 
                                    #지정가로 주문을 넣지만 하루안에 주문을 끝낸다.  장중에 매시간마다 해당 주문을 체크해서 현재가로 지정가 주문을 변경 (체결 확률 업! ) 
                                    #마지막 장 끝나기 전 시간에도 수량이 남아있다면 이때는 시장가로 마무리 !
                                    elif AutoLimitData['StockType'] == "DAY_END":

                                        #현재 주문이 취소 상태라면 날이 바뀐 케이스다 or 돈이 모잘라서 매수 주문이 아직 안들어간 첫 케이스
                                        #이때는 그냥 현재가로 지정가 주문을 넣어준다!!
                                        if AutoLimitData['IsCancel'] == 'Y':

                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']))
            
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']))
                                    
                                        #주문이 유효한 상태라면 주문을 정정해준다
                                        else:
                                           
                                            IS_MODIFY_ORDER = True
                                            

                                            #매수는 새벽 4시 매도는 새벽 3시로 매도가 미리 끝나도록 유도한다!
                                            TargetHour = 19
                                            if GapAmt < 0:
                                                TargetHour = 18


                                            if NowHour == TargetHour:

                                                #일단 현재 주문 취소를 하고
                                                CancelOK = False
                                                try:
                                                    OrderData = KisUS.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum2'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                                    print("Cancel OK!",OrderData["OrderNum2"] )

                                                    CancelOK = True
                                                except Exception as e:
                                                    
                                                    #모의랑 실계좌랑 다르게 동작하는 듯 해서 위 취소 주문이 실패하면 아래 취소 주문으로 1번 더 시도한다!
                                                    try:
                                                        OrderData = KisUS.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum2'],abs(AutoLimitData['OrderAmt']),KisUS.GetCurrentPrice(AutoLimitData['StockCode']),"CANCEL")
                                                        print("Cancel OK!",OrderData["OrderNum2"] )
                                                        
                                                        CancelOK = True
                                                    except Exception as e:
                                                        print("Cancel Failed")
                                                        CancelOK = False
                                                    
                                                #사야된다
                                                if GapAmt > 0:
                                                    #시장가 지향 주문을 넣어준다
                                                    if CancelOK == True:
                                                        OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode'])*1.1)

                                                #팔아야 된다!
                                                else:
                                                    #시장가 지향 주문을 넣어준다
                                                    if CancelOK == True:
                                                        OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode'])*0.9)
       


                                            #그밖의 경우는 현재가로 주문 정정!
                                            else:
                                                try:
                                                    OrderData = KisUS.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum2'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']),"MODIFY")
                                                    print("Modify OK!",OrderData["OrderNum2"] )
                                                except Exception as e:
                                                    print("Modify Failed")
                                                    if OrderData == "APBK1359": # {"rt_cd":"7","msg_cd":"APBK1359","msg1":"정정취소수량이 주문수량보다 많습니다"}
                                                        OrderData = KisUS.CancelModifyOrder(AutoLimitData['StockCode'],AutoLimitData['OrderNum2'],abs(AutoLimitData['OrderAmt']),KisUS.GetCurrentPrice(AutoLimitData['StockCode']),"MODIFY")
                                                
                                    #NORMAL : 
                                    #지정된 카운팅에 해당하는 날 전에는 계속 타겟 가격으로 주문을 넣다가 
                                    #카운팅 날짜 부터는 현재가 그 다음날에는 지정가로 일 단위로 주문을 넣는 루즈한 로직
                                    else:

                                        MAX_LIMIT_DATE = BUY_LIMIT_DATE
                                        if GapAmt < 0:
                                            MAX_LIMIT_DATE = SELL_LIMIT_DATE


                                        if MAX_LIMIT_DATE <= AutoLimitData['TryCnt']:

                                            if MAX_LIMIT_DATE + 1 <= AutoLimitData['TryCnt']:
                                                #사야된다
                                                if GapAmt > 0:
                                                    OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode'])*1.1)
                
                                                #팔아야 된다!
                                                else:
                                                    OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode'])*0.9)
                                            else:

                                                #사야된다
                                                if GapAmt > 0:
                                                    OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']))
                
                                                #팔아야 된다!
                                                else:
                                                    OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']))

                                        else:

                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                                
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                                
                                    AutoLimitData['OrderNum'] = OrderData["OrderNum"]
                                    AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]   
                                    AutoLimitData['OrderTime'] = OrderData["OrderTime"]   

                                    #실제 주문이 들어갔을 경우에만!
                                    if int(AutoLimitData['OrderNum2']) != 0:
                                        #그리고 이전 주문이 정상적으로 들어간 경우에만 카운팅!!!
                                        if OrderOk == "OK":
                                            AutoLimitData['TryCnt'] += 1

                                        AutoLimitData['IsCancel'] = 'N'  


                                    
                                except Exception as e:
                                    print("Fail..", e)
                                    #line_alert.SendMessage("주문 실패" + str(e))
                                    if IS_MODIFY_ORDER == True:
                                        
                                        AutoLimitData['OrderNum'] = ORI_OrderNum
                                        AutoLimitData['OrderNum2'] = ORI_OrderNum2
                                        AutoLimitData['OrderTime'] = ORI_OrderTime 
                                        
                                    else:

                                        AutoLimitData['OrderNum'] = 0
                                        AutoLimitData['OrderNum2'] = 0
                                        AutoLimitData['OrderTime'] = Common.GetNowDateStr(AutoLimitData['Area'])  + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec) 



                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)

                    #장이 닫혔다면 미국의 모든 주문은 취소되었을 테니 취소 처리를 해줍니다
                    else:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Cancel<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        #장이 안열렸으면 취소처리!
                        AutoLimitData['IsCancel'] = 'Y'
                        with open(botOrderPath, 'w') as outfile:
                            json.dump(AutoOrderList, outfile)

           
            #완료가 된 주문이라면 취소가 된 주문이기도 하니 그 처리를 해줍니다!
            if AutoLimitData['IsDone'] == 'Y':
                AutoLimitData['IsCancel'] = 'Y'

                #파일에 저장!
                with open(botOrderPath, 'w') as outfile:
                    json.dump(AutoOrderList, outfile)

        except Exception as e:
            print("Exception by First")




    ############### 주문 중 오래된 필요 없는 것들을 파일에서 지워주는 로직 입니다 ######################################
    #10일이나 지난 주문은 무조건 삭제처리한다.. 보통 완료처리 되거나 취소처리 된 상태! (주문은 1일동안만 유효하므로..)
    AutoOrderList = list()

    try:
        with open(botOrderPath, 'r') as json_file:
            AutoOrderList = json.load(json_file)

    except Exception as e:
        print("Exception by First")

    print("---DELETE Logic Start---")
    for AutoLimitData in AutoOrderList:
        #print("---")
       # print(int(AutoLimitData['DelDate']), int(Common.GetNowDateStr(AutoLimitData['Area'],"NONE")))
        if int(AutoLimitData['DelDate']) < int(Common.GetNowDateStr(AutoLimitData['Area'],"NONE")):
            AutoOrderList.remove(AutoLimitData)


    time.sleep(random.random()*0.01)

    with open(botOrderPath, 'w') as outfile:
        json.dump(AutoOrderList, outfile)

    print("---DELETE Logic End---")


print("                                                             ")
print("                                                             ")
print("                                                             ")
print("                                                             ")
print("                                                             ")
print("                                                             ")
print("                                                             ")

print("------------------------------------------------------------")
print("----------------------RESULT--------------------------------")
print("------------------------------------------------------------")


#단순하게 현재  상태를 프린트 해주는 기능입니다!!!!!!
for botOrderPath in BotOrderPathList:

    print("##################################")
    print("-------------->" , botOrderPath)
    print("##################################")

    AutoOrderList = list()

    try:
        with open(botOrderPath, 'r') as json_file:
            AutoOrderList = json.load(json_file)

    except Exception as e:
        print("Exception by First")


    for AutoLimitData in AutoOrderList:

        try:

            Common.SetChangeMode(AutoLimitData['NowDist']) 

            print("                                  ")
            pprint.pprint(AutoLimitData)

            if AutoLimitData['Area'] == "KR":
                print(KisKR.GetStockName(AutoLimitData['StockCode']))
            print("---->", AutoLimitData['StockCode'], ' IsCancel', AutoLimitData['IsCancel'],' IsDone' , AutoLimitData['IsDone'] )
            
            print("                                  ")

        except Exception as e:
            print("Exception", e)


print("------------------------------------------------------------")
print("------------------------------------------------------------")
print("------------------------------------------------------------")
