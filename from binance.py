import requests
import json
import time

# Binance API endpoint for the order book
binance_url = 'https://api.binance.com/api/v1/depth'

# Parameters for the request
symbol = 'DYDXUSDT'  # symbol to analyze
limit = 100        # number of orders to retrieve (max: 100)
profit_ratio = 2.0  # take profit as a multiple of the entry price

# Function to retrieve the order book from Binance API
def get_order_book():
    params = {'symbol': symbol, 'limit': limit}
    response = requests.get(binance_url, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None

# Function to analyze the order book and find possible long and short entries
def analyze_order_book(order_book):
    bids = order_book['bids']  # array of bid orders (price, quantity)
    asks = order_book['asks']  # array of ask orders (price, quantity)
    
    # Calculate the total volume and concentration for each price level
    bid_volumes = [sum([float(order[1]) for order in bids[:i+1]]) for i in range(len(bids))]
    bid_concentration = [bid_volumes[i]/bid_volumes[-1] for i in range(len(bids))]
    ask_volumes = [sum([float(order[1]) for order in asks[:i+1]]) for i in range(len(asks))]
    ask_concentration = [ask_volumes[i]/ask_volumes[-1] for i in range(len(asks))]
    
    # Find the price levels with the highest bid and ask volumes and concentration
    max_bid_volume = max(bid_volumes)
    max_ask_volume = max(ask_volumes)
    max_bid_concentration = max(bid_concentration)
    max_ask_concentration = max(ask_concentration)
    max_bid_index = bid_volumes.index(max_bid_volume)
    max_ask_index = ask_volumes.index(max_ask_volume)
    max_bid_price = float(bids[max_bid_index][0])
    max_ask_price = float(asks[max_ask_index][0])
    
    # Determine the entry points based on the bid-ask spread and volume imbalances
    spread = max_ask_price - max_bid_price
    if max_bid_volume > max_ask_volume and max_bid_concentration > 0.5:
        entry_price = max_bid_price + spread/2
        entry_type = 'long'
    elif max_ask_volume > max_bid_volume and max_ask_concentration > 0.5:
        entry_price = max_ask_price - spread/2
        entry_type = 'short'
    else:
        entry_price = None
        entry_type = None
        
    # Determine the take profit level
    if entry_type == 'long':
        take_profit_price = entry_price * profit_ratio
    elif entry_type == 'short':
        take_profit_price = entry_price / profit_ratio
    else:
        take_profit_price = None
        
    return entry_type, entry_price, take_profit_price

# Main loop to retrieve and analyze the order book every 15 minutes
while True:
    order_book = get_order_book()
    if order_book is not None:
        entry_type, entry_price, take_profit_price = analyze_order_book(order_book)
        if entry_price is not None and take_profit_price is not None:
            print('Possible entry:', entry_type, entry_price)
            print('Take profit:', take_profit_price)
    time.sleep(900)  # wait for 15 minutes before the next analysis