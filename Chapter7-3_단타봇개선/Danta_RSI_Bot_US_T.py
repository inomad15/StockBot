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
import KIS_Common as Common
import KIS_API_Helper_US as KisUS
import json
import pandas as pd
import pprint
import line_alert

Common.SetChangeMode("VIRTUAL")



BOT_NAME = Common.GetNowDist() + "_DantaRSIBot"




#계좌 잔고를 가지고 온다!
Balance = KisUS.GetBalance()


#해당 단타전략으로 최대 몇개의 종목을 매수할 건지
MaxStockCnt = 5


print("--------------내 보유 잔고---------------------")

pprint.pprint(Balance)

print("--------------------------------------------")
#총 평가금액에서 해당 봇에게 할당할 총 금액비율 1.0 = 100%  0.5 = 50%
InvestRate = 0.01 # 1%로 설정! 모의계좌니깐..

#기준이 되는 내 총 평가금액에서 투자비중을 곱해서 나온 포트폴리오에 할당된 돈!!
TotalMoney = float(Balance['TotalMoney']) * InvestRate

#각 종목당 투자할 금액!
StockMoney = TotalMoney / MaxStockCnt
print("TotalMoney:", str(format(round(TotalMoney), ',')))
print("StockMoney:", str(format(round(StockMoney), ',')))

#종목에 할당된 금액을 쪼개서 1(첫진입) : 2(두번째진입) 이렇게 진입한다!
FirstMoney = StockMoney / 3.0  #첫 진입시 매수 금액!
SecondMoney = FirstMoney * 2.0  #두번째 진입시 매수 금액!

print("FirstMoney:", str(format(round(FirstMoney), ',')))
print("SecondMoney:", str(format(round(SecondMoney), ',')))



#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#########################-트레일링스탑 적용-#######################
TraillingStopRate = 0.01 #1%기준으로 트레일링 스탑!


RevenueRate = 0.015 #익절 1.5%
CutRate = 0.01 #손절 1%
    
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
############# 해당 단타 전략으로 매수한 종목 리스트 ####################
DantaDataList = list()
#파일 경로입니다.
bot_file_path = "/var/autotrade/UsStock_" + BOT_NAME + ".json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(bot_file_path, 'r') as json_file:
        DantaDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")
################################################################
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#

# 오늘 신규로 골라진 종목을 매수(or 체크)했는지 여부!
CheckNewStock = dict()
#파일 경로입니다.
check_file_path = "/var/autotrade/UsStock_" + BOT_NAME + "_CheckNew.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(check_file_path, 'r') as json_file:
        CheckNewStock = json.load(json_file)

except Exception as e:
    print("First Save!!")
    CheckNewStock['IsCheck'] = 'N'
    with open(check_file_path, 'w') as outfile:
        json.dump(CheckNewStock, outfile)
    
    
################################################################
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#

#마켓이 열렸는지 여부~!
IsMarketOpen = KisUS.IsMarketOpen()


print("--------------내 보유 주식---------------------")
#그리고 현재 이 계좌에서 보유한 주식 리스트를 가지고 옵니다!
MyStockList = KisUS.GetMyStockList()
pprint.pprint(MyStockList)
print("--------------------------------------------")
    

#장이 열렸을 때
if IsMarketOpen == True:
    
    
    #전략에 의해 매수된 종목들 제어하기!
    for DantaInfo in DantaDataList:

        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
        #########################-트레일링스탑 적용-#######################
        #영상엔 없지만 기존의 봇에 트레일링 스탑을 적용하려면 
        #'TrallingPrice' , 'IsTralling' 이 값이 데이터가 없을 테므로 에러가 납니다
        #따라서 이전 봇이 매수한 종목 정리하고 봇이 생성한 파일도 지워 초기화 하고 시작해야 되지만
        #그냥 트레일링 스탑만 동작하게 데이터를 추가하고 싶은 분들을 위해 그냥 데이터를 추가해주면 해결 됩니다 
        if DantaInfo.get('TrallingPrice') == None:
            DantaInfo['TrallingPrice'] = 0
            DantaInfo['IsTralling'] = 'N'
            

        stock_code = DantaInfo['StockCode']
        
        stock_name = ""
        stock_amt = 0 #수량
        stock_avg_price = 0 #평단
        stock_eval_totalmoney = 0 #총평가금액!
        stock_revenue_rate = 0 #종목 수익률
        stock_revenue_money = 0 #종목 수익금


        #내가 보유한 주식 리스트에서 매수된 잔고 정보를 가져온다
        for my_stock in MyStockList:
            if my_stock['StockCode'] == stock_code:
                stock_name = my_stock['StockName']
                stock_amt = int(my_stock['StockAmt'])
                stock_avg_price = float(my_stock['StockAvgPrice'])
                stock_eval_totalmoney = float(my_stock['StockNowMoney'])
                stock_revenue_rate = float(my_stock['StockRevenueRate'])
                stock_revenue_money = float(my_stock['StockRevenueMoney'])

                break
                
        
        #아직 트레이딩이 종료 안되었다! - 즉 조건에 의해 매수되었고 아직 익절 손절이 안되었다!!
        if DantaInfo['IsDone'] == 'N':
            
            CurrentPrice = KisUS.GetCurrentPrice(stock_code) #현재가를 가지고 온다


                
            #잔고가 있다면..아직 익절이나 손절이 되지 않은 상황!!
            if stock_amt > 0:
                print("--- Check ---")
                print(stock_name, " " , stock_code)
                print("CurrentPrice:", CurrentPrice)
                print("CutPrice:", DantaInfo['CutPrice'])
                print("RevenuePrice:", DantaInfo['RevenuePrice'])
                
                #그런데 현재 주식 평단과 진입가가 다르다?
                #익절 기준 금액을 수정해준다!
                if stock_avg_price != DantaInfo['EntryPrice']:
                    
                    DantaInfo['EntryPrice'] = stock_avg_price
                    
                    #익절 가격을 구합니다!
                    DantaInfo['RevenuePrice'] = stock_avg_price * (1.0 + RevenueRate)
                    

                    with open(bot_file_path, 'w') as outfile:
                        json.dump(DantaDataList, outfile)
                        
                    line_alert.SendMessage(stock_name + "최초집입가격이랑 평단이 달라져서 익절 기준 가격을 수정했어요!") 
                    
                    
                    
                #손절은 2회차 매수까지 끝났을 때만 한다!
                if DantaInfo['Round'] != 1 and CurrentPrice <= DantaInfo['CutPrice']:
                    
                    
                    #현재가보다 아래에 매도 주문을 넣음으로써 시장가로 매도효과!
                    pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,stock_amt,CurrentPrice*0.9))

                    
                    DantaInfo['IsDone'] = 'Y'
                    
                    
                    #파일에 저장
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(DantaDataList, outfile)
                        
                    line_alert.SendMessage(stock_name + "손절 처리! " + str(stock_revenue_money) + "(" + str(stock_revenue_rate) + "%)") 
                    
                    
                #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
                #########################-트레일링스탑 적용-#######################
                #익절 가격보다 현재가가 크다면!!! 트레일링 스탑이 아직 시작 안 되었다면 
                if CurrentPrice >= DantaInfo['RevenuePrice'] and DantaInfo['IsTralling'] == 'N':


                    DantaInfo['TrallingPrice'] = CurrentPrice
                    #트레일링 스탑이 시작된걸로 저장합니다
                    DantaInfo['IsTralling'] = 'Y'
                    #파일에 저장
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(DantaDataList, outfile)


                    line_alert.SendMessage(stock_name + " (" + stock_code + ") 익절가에 도달! 트레일링 스탑 시작합니다! " + str(stock_revenue_money)+ "(" + str(stock_revenue_rate) + ")") 

                #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
                #########################-트레일링스탑 적용-#######################
                #트레일링 스탑이 시작되었다면 이전에 저장된 값 대비 트레일링 스탑 비중만큼 떨어졌다면 스탑!
                #아니라면 고점 갱신해줍니다!!
                if DantaInfo['IsTralling'] == 'Y':

                    #스탑할 가격을 구합니다.
                    StopPrice = DantaInfo['TrallingPrice'] * (1.0 - TraillingStopRate)

                    #스탑할 가격보다 작아졌다면
                    if CurrentPrice <= StopPrice:

                        #현재가보다 아래에 매도 주문을 넣음으로써 시장가로 매도효과!
                        pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,stock_amt,CurrentPrice*0.9))

                        
                        #트레이딩 완료 처리
                        DantaInfo['IsDone'] = 'Y'

                        #파일에 저장
                        with open(bot_file_path, 'w') as outfile:
                            json.dump(DantaDataList, outfile)
                        
                        line_alert.SendMessage(stock_name + "트레일링 스탑 완료 처리! " + str(stock_revenue_money)+ "(" + str(stock_revenue_rate) + ")") 


                    #현재가가 이전에 저장된 가격보다 높아졌다면 고점 갱신!!!
                    if DantaInfo['TrallingPrice'] < CurrentPrice:

                        DantaInfo['TrallingPrice'] = CurrentPrice

                        #파일에 저장
                        with open(bot_file_path, 'w') as outfile:
                            json.dump(DantaDataList, outfile)



      
                #1차진입 밖에 안했고 2차 진입을 위해서 RSI지표가 30에서 빠져나왔는지 체크해야 한다!!!
                if DantaInfo['IsR2Check'] == 'N' and DantaInfo['Round'] == 1:
                    
                    df = Common.GetOhlcv("US",stock_code,50) 
                    
                    RSI_Before2 = Common.GetRSI(df,14,-3)
                    RSI_Before = Common.GetRSI(df,14,-2)
                    
                    print("RSI CHECK ->", RSI_Before2, " -> ", RSI_Before)
                    
                    #어제 RSI가 30에서 빠져나왔다! 그럼 매수닷!!!
                    if RSI_Before2 <= 30 and RSI_Before >= 30:
                        
                        BuyAmt = int(SecondMoney / CurrentPrice) #2차 금액으로 매수에 들어간다!
                    
                        if BuyAmt < 1:
                            BuyAmt = 1
                        
                        #시장가 주문을 넣는다!
                        #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수!
                        pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,BuyAmt,CurrentPrice*1.1))

                        #그리고 주문 체결된 가격을 리턴 받는다  현재가로 체결되었다고 가정하자!!!
                        OrderDonePrice = CurrentPrice

                        #손절 가격을 구합니다
                        CutPrice = OrderDonePrice * (1.0 - CutRate)
                        
                        DantaInfo['EntryPrice'] = OrderDonePrice #진입 가격
                        DantaInfo['CutPrice'] = CutPrice #손절 가격이 여기서 확정!!!
                        #라운드 증가 1 -> 2  이런식..
                        DantaInfo['Round'] += 1
                        #파일에 저장
                        with open(bot_file_path, 'w') as outfile:
                            json.dump(DantaDataList, outfile)
                            
                        line_alert.SendMessage(stock_code + " 2차 진입했어요!!! 손절가격 확정! ") 
                        
                    DantaInfo['IsR2Check'] = 'Y'
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(DantaDataList, outfile)
                        
                        
            '''
            #영상과는 다르게 수정해습니다 이 부분은 없어도 동작합니다.      
            #잔고가 없다면 일단 트레이딩 완료처리를 하자!
            else:
                
                #트레이딩 완료 처리
                DantaInfo['IsDone'] = 'Y'

                #파일에 저장
                with open(bot_file_path, 'w') as outfile:
                    json.dump(DantaDataList, outfile)
                    
                line_alert.SendMessage(stock_code  + "트레이딩 종료????") 
            '''

        #트레이딩이 종료 되었다?
        else:
            
            '''
            #영상과는 다르게 수정해습니다 이 부분은 없어도 동작합니다.  
            #미국 지정가의 경우 가능성이 있음!
            if DantaInfo['IsDone'] == 'Y':
                #트레이딩이 끝났는데 잔고가 남아 있다??!!!!!!?! 지연체결이 된 셈!
                if stock_amt > 0:
                    DantaInfo['IsDone'] = 'N' #다시 N으로 바꿔서 익절 손절을 할 수 있게 한다!
                    #파일에 저장
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(DantaDataList, outfile)
                        
                    line_alert.SendMessage(stock_code + " 뒤늦게 매수되었나봐요! 잔고가 있어요 그럼 체크!!! ") 
            '''        
            print("")
                    

    #현재 전략에 의해 매수된 종목의 개수가 MaxStockCnt보다 적고 아직 이 안의 로직이 오늘 실행 안되었다면!
    #새로운 종목을 찾는다!!
    if len(DantaDataList) < MaxStockCnt and CheckNewStock['IsCheck'] == 'N':
            

        ###########################################################################
        ###########################################################################
        ###########################################################################
        ########################### 종목 선정 파트 ####################################
        #트레이딩 데이터를 읽는다!
        UsTradingDataList = list()
        #파일 경로입니다.
        us_file_path = "/var/autotrade/UsTradingDataList.json"

        try:
            #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
            with open(us_file_path, 'r') as json_file:
                UsTradingDataList = json.load(json_file)

        except Exception as e:
            print("Exception by First")
            
            

        df = pd.DataFrame(UsTradingDataList)

        #RSI가 아래에서 위로 꺾였을 때 그리고 중앙에 있는 RSI가 30이하 일때
        df = df[df.StockRSI_2 >= df.StockRSI_1].copy()
        df = df[df.StockRSI_1 <= df.StockRSI_0].copy()
        df = df[df.StockRSI_1 <= 30].copy()
        
        df = df[df.StockRSI_1 != 0].copy() #거래정지 되었던 종목 거르기!
        

        #RSI가 작은 순으로 정렬
        df = df.sort_values(by="StockRSI_1")
        pprint.pprint(df)


        #최종 투자 대상으로 선정된 종목이 들어갈 리스트!
        FinalInvestStockList = list()




        #미국 퀀트 시스템 개발할때 미국 시총이나 재무지표가 들어 있는 파일
        UsStockDataList = list()
        #파일 경로입니다.
        StockData_file_path = "/var/autotrade/UsStockDataList.json"

        try:
            #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
            with open(StockData_file_path, 'r') as json_file:
                UsStockDataList = json.load(json_file)

        except Exception as e:
            print("Exception by First")



        df_sd = pd.DataFrame(UsStockDataList)



        NowCnt = 0

        for idx, row in df.iterrows():
            
            if NowCnt < (MaxStockCnt - len(DantaDataList)):

                print("--------------",row['StockCode'],"--------------")

                
                for idx2, row2 in df_sd.iterrows():
                    
                    if row['StockCode'] == row2['StockCode']:
                        #pprint.pprint(row2)
                                    
                        
                        
                        if float(row2['StockOperatingMargin']) > 0 and float(row2['StockPER']) >= 1.0 and row2['StockPBR'] >= 0.2:
                            #시총 500억 이상!    금융주 제외
                            if row2['StockMarketCap'] >= 50000000 and row2['StockDistName'] != "Financial Services" :                  
                                IsOk = False
                                #현재가!
                                try:
                                    #현재가를 가져올수 있는지 체크 
                                    CurrentPrice = KisUS.GetCurrentPrice(row['StockCode'])
                                    
                                    CurrentPrice = float(CurrentPrice)*1.0
                                    
                                    #거래량이 있는지 
                                    ohlcv = Common.GetOhlcv("US",row['StockCode'],10)
                                    
                                    if int(ohlcv['volume'].iloc[-2]) == 0:
                                        IsOk = False
                                    else: 
                                        if CurrentPrice < FirstMoney: 
                                            IsOk = True

                                except Exception as e:
                                    IsOk = False
                                    print("Exception by First")

                                if IsOk == True:
                                    print(row['StockCode'])
                                    print("거래대금: ", row['StockMoney_0'])
                                    print("전날대비 거래대금: ", row['StockMoneyRate'])
                                    print("등락률 : ", round(row['StockRate'],2))

                                    print("시총: ", row2['StockMarketCap'])
                                    print("현재가 : ", row2['StockNowPrice'])
                                    print("영업이익률 : ", row2['StockOperatingMargin'])
                                    print("EPS(주당 순이익) : ", row2['StockEPS'])
                                    print("PER(현재가 / 주당 순자산) : ", row2['StockPER'])
                                    print("PBR(현재가 / 주당 순자산) : ", row2['StockPBR'])
                                    print("ROE : ", row2['StockROE'])
                                    print("ROA : ", row2['StockROA'])
                                    print("EV/EBITDA : ", row2['StockEV_EBITDA'])
                                    #두개의 데이터를 병합해서 추가한다!!
                                    FinalInvestStockList.append(dict(row.to_dict(), **row2.to_dict()))
                                
                                    NowCnt += 1
                            
                            
                        break
                
                

                print("-----------------------------------")

            else:
                break
        print("##############################################################")
        print("##############################################################")
        print("################## 최종 투자 대상!!  ###########################")
        print("################--",len(FinalInvestStockList),"--###########################")

        for Stock_Info in FinalInvestStockList:
            
            print(Stock_Info['StockName'])
            print("Code:", Stock_Info['StockCode'])
            print("거래대금: ", Stock_Info['StockMoney_0'])
            print("전날대비 거래대금: ", Stock_Info['StockMoneyRate'])
            print("등락률 : ", round(Stock_Info['StockRate'],2))
            print("시총: ", Stock_Info['StockMarketCap'])
            print("현재가 : ", Stock_Info['StockNowPrice'])
            print("영업이익률 : ", Stock_Info['StockOperatingMargin'])
            print("EPS(주당 순이익) : ", Stock_Info['StockEPS'])
            print("PER(현재가 / 주당 순자산) : ", Stock_Info['StockPER'])
            print("PBR(현재가 / 주당 순자산) : ", Stock_Info['StockPBR'])
            print("ROE(EPS / BPS), ROA, GP/A 등 : ", Stock_Info['StockROE'])
            
            print("------------------------------------------")





        ###########################################################################
        ###########################################################################
        ###########################################################################


        #최종 선정된 종목들을 순회한다.
        for Stock_Info in FinalInvestStockList:
            
            #이미 해당 봇에 의해 매수된 종목이라면..
            AlreadyHas = False
            for DantaInfo in DantaDataList:
        
                if Stock_Info['StockCode'] == DantaInfo['StockCode']:
                    AlreadyHas = True #True로 세팅!
                    break
                
            #내가 보유한 주식 리스트에서 매수된 잔고 정보를 가져온다
            for my_stock in MyStockList:
                if Stock_Info['StockCode'] == my_stock['StockCode']:
                    stock_amt = int(my_stock['StockAmt'])
                    
                    if stock_amt > 0:
                        AlreadyHas = True #마찬가지로 이미 매수되어 잔고가 있다면!
                        
                    break
                
            #즉 이미 매수된 종목이라면 스킵한다!
            if AlreadyHas == True:
                continue
            
            
            #최대 매수 가능한 종목 개수 안에서만 매매할 수 있다!
            if len(DantaDataList) < MaxStockCnt:
                
                #장이 열렸을 때
                if IsMarketOpen == True:
                        
                    
                    stock_code = Stock_Info['StockCode']
                    
                    line_alert.SendMessage(stock_code + " RSI 단타 트레이딩 시작합니다!!! ") 
                    
                    #현재가를 구해 현재 첫 매수금액으로 할당된 돈으로 얼마큼 살 수 있는지 수량을 구해서
                    CurrentPrice = KisUS.GetCurrentPrice(stock_code)
                    BuyAmt = int(FirstMoney / CurrentPrice)
                    
                    if BuyAmt < 1:
                        BuyAmt = 1
                    
                    
                    #시장가 주문을 넣는다!
                    #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수!
                    pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,BuyAmt,CurrentPrice*1.1))

                    #그리고 주문 체결된 가격을 리턴 받는다  현재가로 체결되었다고 가정하자!!!
                    OrderDonePrice = CurrentPrice
                    
                    #익절 가격을 구합니다!
                    RevenuePrice = OrderDonePrice * (1.0 + RevenueRate)
                    
     
                    
                    
                    #아래처럼 데이터를 구성해서 파일로 저장한다!!!
                    DantaDataDict = dict()
                    
                    DantaDataDict['StockCode'] = stock_code #종목코드
                    DantaDataDict['EntryPrice'] = OrderDonePrice #진입가격

                    DantaDataDict['RevenuePrice'] = RevenuePrice #익절 가격
                    DantaDataDict['CutPrice'] = 0 #손절 가격!
                    
                    DantaDataDict['Round'] = 1 #첫번째 진입이라는 표시! ROUND1
                    DantaDataDict['IsR2Check'] = 'N' #라운드2 즉 2차진입 여부를 오늘 체크했는지 플래그!
                    DantaDataDict['IsDone'] = 'N' #트레이딩 완료 여부! 
                    
                    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
                    #########################-트레일링스탑 적용-#######################
                    DantaDataDict['TrallingPrice'] = RevenuePrice #의미 없지만 일단 익절가로 세팅
                    DantaDataDict['IsTralling'] = 'N' #트레일링 시작 여부

                    #실제로 해당 봇 전략으로 매매하는 종목으로 등록!!
                    DantaDataList.append(DantaDataDict)
                    #파일에 저장
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(DantaDataList, outfile)
                        
                        
                    line_alert.SendMessage(stock_code + " RSI 단타 트레이딩 시작주문 완료! \n" + str(DantaDataDict)) 
                    
                else:
                    print("Test...")
                    
        #체크를 진행했기에 Y로!!
        CheckNewStock['IsCheck'] = 'Y'
        with open(check_file_path, 'w') as outfile:
            json.dump(CheckNewStock, outfile)

#장이 닫혔을때!               
else:
    print("Close Market! " , len(DantaDataList))
    
    #장이 끝났으니깐 신규 종목 체크 여부를 N으로 바꿔준다 (다음날을 위해)
    if CheckNewStock['IsCheck'] == 'Y':
        CheckNewStock['IsCheck'] = 'N'
        with open(check_file_path, 'w') as outfile:
            json.dump(CheckNewStock, outfile)
            
            
    #전략에 의해 매수된 종목들 체크하기 
    for DantaInfo in DantaDataList:
        
        stock_code = DantaInfo['StockCode']
        
        #트레이딩이 끝난건 리스트에서 아예 지워준다!
        if DantaInfo['IsDone'] == 'Y':
            

            stock_amt = 0 #수량

            #내가 보유한 주식 리스트에서 매수된 잔고 정보를 가져온다
            for my_stock in MyStockList:
                if my_stock['StockCode'] == stock_code:
                    stock_amt = int(my_stock['StockAmt'])
                    break
                
            #잔고 수량이 0인 거   
            if stock_amt == 0:
                                
                line_alert.SendMessage(stock_code + "트레이딩 완전 종료! 끝!\n" + str(DantaInfo)) 
                
                DantaDataList.remove(DantaInfo) #리스트 파일에서 삭제!!!!!
                #파일에 저장
                with open(bot_file_path, 'w') as outfile:
                    json.dump(DantaDataList, outfile)
                    
                    
        #아직 유효하다 
        else:
            
            #2차 진입을 위한 체크 플래그를 N으로 바꿔줘서 다음날 다시 체크할 수 있게 한다
            DantaInfo['IsR2Check'] = 'N'
            #파일에 저장
            with open(bot_file_path, 'w') as outfile:
                json.dump(DantaDataList, outfile)

            

print("-------Now Status ------")
pprint.pprint(DantaDataList)