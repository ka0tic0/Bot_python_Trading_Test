import time
from binance_f import RequestClient
from binance_f.exception import BinanceApiException
from binance_f.model import OrderSide, OrderType, TimeInForce
import talib
import numpy as np

# Initialize Binance API client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
symbol = 'BTCUSDT'
client = RequestClient(api_key=api_key, secret_key=api_secret)

# Function to retrieve the order book from Binance
def get_order_book():
    try:
        result = client.get_order_book(symbol=symbol, limit=5)
        return result
    except BinanceApiException as e:
        print(e.status_code)
        print(e.message)
        return None

# Function to analyze the order book and determine the best entry point
def analyze_order_book(order_book):
    bids = np.array([float(bid.price) for bid in order_book.bids])
    bid_volumes = np.array([float(bid.quantity) for bid in order_book.bids])
    asks = np.array([float(ask.price) for ask in order_book.asks])
    ask_volumes = np.array([float(ask.quantity) for ask in order_book.asks])
    
    # Analyze the order book and determine if there is a good entry point for a long or short position
    bid_concentration = bid_volumes.cumsum() / bid_volumes.sum()
    ask_concentration = ask_volumes.cumsum() / ask_volumes.sum()
    buy_volume = bid_volumes[bid_concentration < 0.1].sum()
    sell_volume = ask_volumes[ask_concentration < 0.1].sum()
    volume_ratio = buy_volume / sell_volume if sell_volume > 0 else None
    if volume_ratio is not None:
        if volume_ratio > 2:
            entry_type = 'long'
            entry_price = asks[ask_concentration < 0.1][-1]
            take_profit_price = entry_price * 1.02  # 2% take profit
        elif volume_ratio < 0.5:
            entry_type = 'short'
            entry_price = bids[bid_concentration < 0.1][-1]
            take_profit_price = entry_price * 0.98  # 2% take profit
        else:
            entry_type, entry_price, take_profit_price = None, None, None
    else:
        entry_type, entry_price, take_profit_price = None, None, None
    
    return entry_type, entry_price, take_profit_price

# Function to retrieve the 15-minute candlestick data from Binance
def get_candles():
    try:
        result = client.get_candlestick_data(symbol=symbol, interval='15m', limit=100)
        return result
    except BinanceApiException as e:
        print(e.status_code)
        print(e.message)
        return None

# Main loop to retrieve and analyze the order book every 15 minutes, and make the entry if possible
while True:
    # Retrieve and analyze the order book
    order_book = get_order_book()
    if order_book is not None:
        entry_type, entry_price, take_profit_price = analyze_order_book(order_book)
        
        # If there is a possible entry point, analyze the price action and make the entry
        if entry_price is not None and take_profit_price is not None:
            print('Possible entry:', entry_type, entry_price)
            print('Take profit:', take_profit_price)
    time.sleep(900)  # wait for 15 minutes before the next analysis
