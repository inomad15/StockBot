import pybithumb
import datetime
import pytz
import pandas as pd
import ccxt
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

from cryptography.fernet import Fernet

#암호화 복호화 클래스
class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Bithumb_ApiKey = simpleEnDecrypt.decrypt(my_key.bithumb_apikey)
Bithumb_Secret = simpleEnDecrypt.decrypt(my_key.bithumb_secret)

# Bithumb API 연결 설정
bithumb = ccxt.bithumb({
    'apiKey': Bithumb_ApiKey,
    'secret': Bithumb_Secret,
})

mybithumb = pybithumb.Bithumb(Bithumb_ApiKey, Bithumb_Secret)

# 종목, 차트기간 설정
ticker = 'BTC/KRW'                                                                       ###########################
timeframe = '5m'                                                                         ###########################
since = bithumb.parse8601('2022-01-01T00:00:00Z')
limit = 50000

# 시간 데이터를 한국 시간대로 변환하는 함수
def convert_to_kst(time):
    kst = pytz.timezone('Asia/Seoul')
    return time.astimezone(kst)
  
current_time = convert_to_kst(datetime.datetime.now())


# 이동평균선 계산함수 : (분봉/일봉 정보, 기간, 날짜)
def get_ma(btc_data,period,st):
    close = btc_data["close"]
    ma = close.rolling(period).mean()
    return float(ma.iloc[st])
        
# MACD 계산 함수
def get_macd(btc_data,st):
    macd_short, macd_long, macd_signal=12,26,9

    btc_data["MACD_short"]=btc_data["close"].ewm(span=macd_short).mean()
    btc_data["MACD_long"]=btc_data["close"].ewm(span=macd_long).mean()
    btc_data["MACD"]=btc_data["MACD_short"] - btc_data["MACD_long"]
    btc_data["MACD_signal"]=btc_data["MACD"].ewm(span=macd_signal).mean() 

    return btc_data["MACD"].iloc[st], btc_data["MACD_signal"].iloc[st]

# RSI 계산 함수
def get_rsi(btc_data, period, st):
    btc_data["close"] = btc_data["close"]
    delta = btc_data["close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    RS = _gain / _loss
    return float(pd.Series(100 - (100 / (1 + RS)), name="RSI").iloc[st])

# 스토캐스틱 계산 함수
def get_sto(btc_data,period,st):

    stoch = dict()

    ndays_high = btc_data['high'].rolling(window=period, min_periods=1).max()
    ndays_low = btc_data['low'].rolling(window=period, min_periods=1).min()
    fast_k = (btc_data['close'] - ndays_low)/(ndays_high - ndays_low)*100
    slow_d = fast_k.rolling(window=3, min_periods=1).mean()

    stoch['fast_k'] = fast_k.iloc[st]
    stoch['slow_d'] = slow_d.iloc[st]

    return fast_k.iloc[st], slow_d.iloc[st]


# OHLCV 데이터를 가져오는 함수
def fetch_ohlcv(ticker, timeframe, since, limit):
    ohlcv = bithumb.fetch_ohlcv(ticker, timeframe, since, limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# 데이터 준비하기 ##############################################################################

df = fetch_ohlcv(ticker, timeframe, since, limit)
btc_data = df

'''
# btc_data의 컬럼 확인 (디버깅 목적)
print(btc_data.columns)
'''

# 이동평균 계산
ma5_before3 = get_ma(btc_data,5,-4)
ma5_before2 = get_ma(btc_data,5,-3)
ma5_now = get_ma(btc_data,5,-2)
ma20 = get_ma(btc_data,20,-2)
ma30 = get_ma(btc_data, 30, -2)

# MACD 계산
macd_before3, macd_s_before3 = get_macd(btc_data, -4)
macd_before2, macd_s_before2 = get_macd(btc_data, -3)
macd_now, macd_s_now = get_macd(btc_data, -2)

# 스토캐스틱 계산
fast_k_before3, slow_d_before3 = get_sto(btc_data, 14, -4)
fast_k_before2, slow_d_before2 = get_sto(btc_data, 14, -3)
fast_k_now, slow_d_now = get_sto(btc_data, 14, -2)

k_line = fast_k_now
d_line = slow_d_now

btc_data['rsi'] = get_rsi(btc_data, 14, -2)

# RSI 계산
rsi_before3 = get_rsi(btc_data, 14, -4)
rsi_before2 = get_rsi(btc_data, 14, -3)
rsi_now = get_rsi(btc_data, 14, -2)

##############################################################################################

# 매매신호 함수
def generate_trading_signals(btc_data, macd_now, macd_before2, macd_before3, macd_s_now):
    # MACD와 RSI 계산
    macd_now, macd_s_now = get_macd(btc_data, -2)
    rsi_now = get_rsi(btc_data, 14, -2)
    btc_data['rsi'] = rsi_now
    
    # 스토캐스틱 계산
    k_line, d_line = get_sto(btc_data, 14, -2)
    btc_data['k_line'] = k_line
    btc_data['d_line'] = d_line

    # 매매 신호 생성
    signals = pd.DataFrame(index=btc_data.index)
    signals['signal'] = 0.0
    signals.loc[(macd_now < macd_s_now) & (macd_before3 > macd_before2) & (macd_before2 < macd_now), 'signal'] = 1.0  # 매수 신호     #####################
    signals.loc[(macd_now > macd_s_now) & (macd_before3 < macd_before2) & (macd_before2 > macd_now), 'signal'] = -1.0  # 매도 신호    #####################
    signals['positions'] = signals['signal'].diff()
    return signals

signals = generate_trading_signals(btc_data, macd_now, macd_before2, macd_before3, macd_s_now)

###################################################################################################
mybalance = mybithumb.get_balance("BTC")
balance = bithumb.fetch_balance()
base_currency = ticker.split('/')[0]  # 예: BTC/KRW에서 BTC를 얻음
base_currency_balance = balance[base_currency]
total_buy_quantity = base_currency_balance['free']
won = balance["KRW"]
print("---------------------------------------------------------------------")
print(mybalance)
print("---------------------------------------------------------------------")
print(f"주문가능원화 : {won['free']:.0f}")
print(base_currency, " 보유수량 : ",total_buy_quantity)
print("---------------------------------------------------------------------")
print(btc_data['close'].tail())
print("---------------------------------------------------------------------")
order_price = btc_data['close'].iloc[-1]
print("order price :", order_price)
###################################################################################################

# 실제 거래를 위한 함수
def execute_real_trade(btc_data, signals):
    current_time = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    order_price = btc_data['close'].iloc[-1]
    last_signal = signals['signal'].iloc[-2]
    

    if last_signal == 1:  # 매수 신호가 발생한 경우
            # 잔고 확인 로직 추가
            if won["free"] > (order_price * 0.005) * 1.0004:  # 매수 가능한 잔고가 있는지 확인
                print(f"매수 신호 (KST): 시간 {current_time}, 가격 {order_price}")
            # 매수 주문 로직
                buy_quantity = 0.005  # 매수 수량 (예시 값)#####################################################
               
                bithumb.create_market_buy_order(ticker, buy_quantity)     
                
            else:
                print("매수 가능한 잔고가 부족합니다.")
 
        
    elif last_signal == -1:  # 매도 신호가 발생한 경우
        if total_buy_quantity > 0:    
            print(f"매도 신호 (KST): 시간 {current_time}, 가격 {order_price}")
            sell_quantity = 0.005  # 매도 수량 (예시 값)#####################################################
            # 주문량 계산 (전량 매도 또는 0.004 BTC 중 작은 값)
            order_quantity = min(total_buy_quantity, sell_quantity)      ###############################
                              
            bithumb.create_market_sell_order(ticker, order_quantity)
                    
        else:
            print("매도할 잔액이 없습니다.")
    else:
        print("매매가 이루어지지 않았습니다.")

    return current_time


# execute_real_trade 함수 호출
execute_real_trade(btc_data, signals)


# 최신 시장 데이터와 신호를 가져옵니다
print("-----------------------------------------------------------------------------------------------------")

print(f"시간 (KST): {current_time}, 종가: {btc_data['close'].iloc[-2]:.0f}, MACD: {btc_data['MACD'].iloc[-2]:.0f}, MACD 신호: {btc_data['MACD_signal'].iloc[-2]:.0f}, k_line: {btc_data['k_line'].iloc[-2]:.0f}, d_line: {btc_data['d_line'].iloc[-2]:.0f}, RSI: {btc_data['rsi'].iloc[-2]:.0f}")
print(f"macd : {macd_before3:.0f} -> {macd_before2:.0f} -> {macd_now:.0f}")
print(f"macd_signal : {macd_s_now:.0f}")
print("-----------------------------------------------------------------------------------------------------")

print(ticker, "현재잔고 :", base_currency_balance)

