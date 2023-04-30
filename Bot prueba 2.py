from binance.client import Client
import pandas as pd
import numpy as np

api_key = 'aI0wfyJi8Eow9jLpkTb0dm6hoEwTv9qBaQ0T1xCnkRis5DtExaaCSAfhQ9gvtdRs'
api_secret = 'kSn8dUqeaYTvf6qCHNouc6QFzmUKjoGDEqrAb2lng11QwX4sTb2j1KotzS8DjUqv'

client = Client(api_key, api_secret)

symbol = 'DYDXUSDT'
timeframe = '15m'
limit = 1000

depth = client.futures_order_book(symbol=symbol, limit=limit)
depth_df = pd.DataFrame(depth['bids']+depth['asks'], columns=['price', 'quantity'])
depth_df['price'] = pd.to_numeric(depth_df['price'])
depth_df['quantity'] = pd.to_numeric(depth_df['quantity'])
position = 'long'   or 'short'

if position == 'long':
    depth_df['position'] = np.where(depth_df['price'] >= depth_df['price'].mean(), 'long', 'short')
else:
    depth_df['position'] = np.where(depth_df['price'] <= depth_df['price'].mean(), 'short', 'long')

total_quantity = depth_df['quantity'].sum()
position_quantity = depth_df[depth_df['position'] == position]['quantity'].sum()
concentration = position_quantity / total_quantity

print(f"La concentración de volumen de {position} es: {concentration:.2%}")

bids = depth['bids']
asks = depth['asks']

# Concatenamos los datos de las órdenes de compra y venta
orders = bids + asks

# Convertimos los datos en un DataFrame de pandas
orders_df = pd.DataFrame(orders, columns=['price', 'quantity'])

# Convertimos los datos a números
orders_df['price'] = pd.to_numeric(orders_df['price'])
orders_df['quantity'] = pd.to_numeric(orders_df['quantity'])

# Calculamos el VWAP
vwap = (orders_df['price'] * orders_df['quantity']).sum() / orders_df['quantity'].sum()
print(f"El VWAP es: {vwap:.2f}")
current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])

if current_price > vwap:
    print("Abrir posición larga")
else:
    print("Abrir posición corta")

