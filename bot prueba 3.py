from binance.client import Client
import pandas as pd
import numpy as np

# Inicializar la API key y secret
api_key = 'aI0wfyJi8Eow9jLpkTb0dm6hoEwTv9qBaQ0T1xCnkRis5DtExaaCSAfhQ9gvtdRs'
api_secret = 'kSn8dUqeaYTvf6qCHNouc6QFzmUKjoGDEqrAb2lng11QwX4sTb2j1KotzS8DjUqv'

# Inicializar el cliente de Binance
client = Client(api_key, api_secret)

# Símbolo del futuro perpetuo
symbol = 'DYDXUSDT'

# Timeframe del libro de órdenes
timeframe = '15m'

# Límite de filas a obtener del libro de órdenes
limit = 1000

# Obtener el libro de órdenes
depth = client.futures_order_book(symbol=symbol, limit=limit)

# Convertir los datos en un DataFrame de pandas
depth_df = pd.DataFrame(depth['bids'] + depth['asks'], columns=['price', 'quantity'])

# Convertir los precios y cantidades a números
depth_df['price'] = pd.to_numeric(depth_df['price'])
depth_df['quantity'] = pd.to_numeric(depth_df['quantity'])

# Calcular el precio promedio
average_price = depth_df['price'].mean()

# Calcular la posición del trader (en este caso, short)
position = 'short'

# Calcular la posición de cada orden en el libro de órdenes
if position == 'long':
    depth_df['position'] = np.where(depth_df['price'] >= average_price, 'long', 'short')
else:
    depth_df['position'] = np.where(depth_df['price'] <= average_price, 'short', 'long')

# Calcular la cantidad total de contratos en el libro de órdenes
total_quantity = depth_df['quantity'].sum()

# Calcular la cantidad de contratos en la posición del trader
position_quantity = depth_df[depth_df['position'] == position]['quantity'].sum()

# Calcular la concentración de volumen en la posición del trader
concentration = position_quantity / total_quantity

# Imprimir la concentración de volumen
print(f"La concentración de volumen de {position} es: {concentration:.2%}")

# Calcular el VWAP (Volume-Weighted Average Price)
bids = depth['bids']
asks = depth['asks']
orders = bids + asks
orders_df = pd.DataFrame(orders, columns=['price', 'quantity'])
orders_df['price'] = pd.to_numeric(orders_df['price'])
orders_df['quantity'] = pd.to_numeric(orders_df['quantity'])
vwap = (orders_df['price'] * orders_df['quantity']).sum() / orders_df['quantity'].sum()

# Imprimir el VWAP
print(f"El VWAP es: {vwap:.2f}")

# Obtener el precio actual del símbolo
current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])

# Calcular la entrada de la posición corta
if current_price < vwap and concentration >= 0.5:
    entry_price = current_price
    take_profit_price = entry_price * 0.98  # TP del 2%
    print(f"La entrada de la posición corta es {entry_price:.2f} y el take profit es {take_profit_price:.2f}")
else:
    print("No hay señal de entrada corta")
