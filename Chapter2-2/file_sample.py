import json


StockList = list()

#파일 경로입니다.
stock_list_file_path = "/var/autobot/StockList.json"
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(stock_list_file_path, 'r') as json_file:
        StockList = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First")





#이런식으로 값을 추가하고 파일에 저장해서 사용할 수 있습니다.
####################################################################
StockList.append("005930")
StockList.append("000660")
        
with open(stock_list_file_path, 'w') as outfile:
    json.dump(StockList, outfile)
####################################################################




#이런식으로 제거 할수도 있습니다. 이후 StockList를 참고하면 005930 이거밖에 없겠네요
####################################################################
StockList.remove("000660")

with open(stock_list_file_path, 'w') as outfile:
    json.dump(StockList, outfile)
####################################################################




#딕셔너리는 키와 값으로 이루어져 있어 유용하게 쓰일 수 있습니다.
StockDict = dict()

#파일 경로입니다.
stock_dict_file_path = "/var/autobot/StockDict.json"
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(stock_dict_file_path, 'r') as json_file:
        StockDict = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First")




####################################################################
#이런 식으로 딕셔너리
StockDict["005930"] = 58900
StockDict["000660"] = 92000

with open(stock_dict_file_path, 'w') as outfile:
    json.dump(StockDict, outfile)
####################################################################



####################################################################
#키가 없다면 초기 값을 아래처럼 지정해 둘 수도 있습니다
if StockDict.get("005930") == None:
    StockDict["005930"] = 50000

    with open(stock_dict_file_path, 'w') as outfile:
        json.dump(StockDict, outfile)
####################################################################

