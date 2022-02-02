import time
import pyupbit
import datetime
import numpy as np

access = "vjCipsOkzxJxWboOn81c67f1LkBQzwxm52yTdbx2"
secret = "Fm8HvotxFzTww6xZTwqqxYa2YEH57khTONQzjsb8"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_ror(ticker, k=0.5):
    df = pyupbit.get_ohlcv(ticker, count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_best_k(ticker):
    max_ror = 0
    best_k = 0.0

    try:
        for k in np.arange(0.1, 1.0, 0.1):
            ror = get_ror(ticker, k)
            print("%.1f %f" % (k, ror))
            if ror > max_ror:
                max_ror = ror
                best_k = k
    except Exception as e:
        print(e)
        best_k = 0.3

    print(ticker, "'s Best_k = ", best_k)
    return best_k


# 로그인
upbit = pyupbit.Upbit(access, secret)
bestk = get_best_k("KRW-BTC")
time.sleep(1)
bestk_for_ETH = get_best_k("KRW-ETH")
time.sleep(1)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        # 평균적을 00~06시 사이에 코인 가격이 상승하므로 그때 매도
        start_time = get_start_time("KRW-BTC") - datetime.timedelta(hours=3)
        end_time = start_time + datetime.timedelta(days=1)
        

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", bestk)
            current_price = get_current_price("KRW-BTC")

            ETH_target_price = get_target_price("KRW-ETH", bestk_for_ETH)
            ETH_current_price = get_current_price("KRW-ETH")
            
            # 목표가 도달하면 가상화폐 매수
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    print(now, "BTC buy at ", current_price)
            if ETH_target_price < ETH_current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-ETH", krw*0.9995)
                    print(now, "ETH buy at ", ETH_current_price)
            
            # 현재가가 목표가 대비 5% 이상 하락하며 던지기
            if current_price < (target_price*0.95):
                print(now, "BTC DROP")
                time.sleep(1)
                if btc > 0.00008:
                    upbit.sell_market_order("KRW-BTC", btc)
            if ETH_current_price < (ETH_target_price*0.95):
                print(now, "ETH DROP")
                time.sleep(1)
                if eth > 0.001:
                    upbit.sell_market_order("KRW-ETH", eth)

        else:
            btc = get_balance("BTC")
            eth = get_balance("ETH")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc)
                print(now, "Sell BTC at ", current_price)
            time.sleep(1)
            if eth > 0.001:
                upbit.sell_market_order("KRW-ETH", eth)
                print(now, "Sell ETH at ", ETH_current_price)
            time.sleep(1)
            bestk = get_best_k("KRW-BTC")
            time.sleep(1)
            bestk_for_ETH = get_best_k("KRW-ETH")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
