import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *

# Enter your Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Instantiate a client object
client = Client(api_key, api_secret)

# Define the symbol and time interval
symbol = 'DYDXUSDT'
interval = '15m'

# Get the klines for the symbol and interval
klines = client.futures_klines(symbol=symbol, interval=interval)

# Create a DataFrame for the klines
columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
df = pd.DataFrame(klines, columns=columns)
df = df.astype(float)

# Set the DataFrame index to the timestamp
df.set_index('timestamp', inplace=True)
df.index = pd.to_datetime(df.index, unit='ms')

# Calculate the VWAP for the klines
df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

# Get the order book for the symbol
order_book = client.futures_order_book(symbol=symbol, limit=1000)

# Create DataFrames for the bids and asks
bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'qty'])
asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'qty'])

# Convert the DataFrames to float
bids_df = bids_df.astype(float)
asks_df = asks_df.astype(float)

# Calculate the support and resistance levels
support_levels = np.array(bids_df['price'])
resistance_levels = np.array(asks_df['price'])

# Plot the VWAP and support/resistance levels
fig, ax = plt.subplots(figsize=(12, 8))
ax.plot(df.index, df['vwap'], label='VWAP')
ax.plot(df.index, np.full(len(df.index), support_levels.max()), label='Resistance', linestyle='--')
ax.plot(df.index, np.full(len(df.index), support_levels.min()), label='Support', linestyle='--')
plt.title(f'{symbol} {interval} Support/Resistance Levels')
plt.legend()
plt.show()
