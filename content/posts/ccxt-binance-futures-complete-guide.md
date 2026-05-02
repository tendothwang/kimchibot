---
title: "The ccxt Guide for Binance Futures I Wish I Had Earlier"
date: 2026-04-07T12:00:00
draft: false
tags: ["ccxt", "binance", "python", "futures", "tutorial", "api"]
categories: ["Guide"]
summary: "Everything you need to know about using ccxt with Binance Futures in Python. Connection, orders, positions, stop losses, and all the gotchas."
---

## Why ccxt?

ccxt is a Python library that provides a unified API for 100+ crypto exchanges. Write your bot once, run it on any exchange.

```bash
pip install ccxt
```

This guide covers **Binance USDT-M Futures** specifically — the most popular futures market for bot trading.

## Connection Setup

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True,
    },
    'enableRateLimit': True,
})

# MUST call this — prevents timestamp errors
exchange.load_time_difference()
```

### Key Options Explained

| Option | What It Does | Required? |
|--------|-------------|-----------|
| `defaultType: future` | Routes all calls to Futures API | Yes |
| `adjustForTimeDifference` | Syncs your clock with Binance | Yes |
| `enableRateLimit` | Auto-throttles API calls | Recommended |

## Fetching Market Data

### OHLCV Candles

```python
# Fetch 100 five-minute candles for BTC
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '5m', limit=100)

# Each candle: [timestamp, open, high, low, close, volume]
# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
df['ts'] = pd.to_datetime(df['ts'], unit='ms')
```

**Available timeframes:** `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`, `1w`

### Ticker (Current Price)

```python
ticker = exchange.fetch_ticker('BTC/USDT')
print(ticker['last'])    # Last price
print(ticker['bid'])     # Best bid
print(ticker['ask'])     # Best ask
print(ticker['volume'])  # 24h volume
```

### All Markets

```python
exchange.load_markets()
futures_pairs = [s for s in exchange.symbols if s.endswith('/USDT') and ':USDT' in s]
print(f"Available futures pairs: {len(futures_pairs)}")
```

## Account & Balance

```python
# Fetch futures balance
balance = exchange.fetch_balance()

# Your USDT balance
free_usdt = balance['USDT']['free']     # Available
used_usdt = balance['USDT']['used']     # In positions
total_usdt = balance['USDT']['total']   # Total

print(f"Balance: {total_usdt} USDT (Free: {free_usdt}, Used: {used_usdt})")
```

**Important:** Don't pass `{'type': 'future'}` to `fetch_balance()`. On some ccxt versions, this returns wrong data. Just call it plain.

## Setting Leverage

```python
# Set leverage BEFORE opening a position
exchange.set_leverage(3, 'BTC/USDT')

# Set margin mode (isolated is safer for bots)
exchange.set_margin_mode('isolated', 'BTC/USDT')
```

**Warning:** If you don't set leverage explicitly, Binance uses whatever was set last — possibly from manual trading in the web UI.

## Placing Orders

### Market Order (Immediate Fill)

```python
# Long (buy)
order = exchange.create_order('BTC/USDT', 'market', 'buy', 0.001)

# Short (sell)
order = exchange.create_order('BTC/USDT', 'market', 'sell', 0.001)
```

### Limit Order (Fill at Specific Price)

```python
# Buy limit at $84,000
order = exchange.create_order('BTC/USDT', 'limit', 'buy', 0.001, 84000)
```

### Stop Loss (STOP_MARKET)

```python
# Stop loss for a long position (sell when price drops to $82,000)
order = exchange.create_order(
    'BTC/USDT', 'STOP_MARKET', 'sell', 0.001,
    params={
        'stopPrice': 82000,
        'reduceOnly': True,
    }
)
```

### Stop Loss (STOP — Limit Order)

```python
# Limit stop loss — triggers at stopPrice, fills at price
order = exchange.create_order(
    'BTC/USDT', 'STOP', 'sell', 0.001, 81800,  # limit price
    params={
        'stopPrice': 82000,  # trigger price
        'reduceOnly': True,
    }
)
```

### Take Profit

```python
# Take profit for a long position at $90,000
order = exchange.create_order(
    'BTC/USDT', 'TAKE_PROFIT_MARKET', 'sell', 0.001,
    params={
        'stopPrice': 90000,
        'reduceOnly': True,
    }
)
```

## Position Management

### Check Open Positions

```python
positions = exchange.fetch_positions()

for pos in positions:
    if float(pos['contracts']) > 0:
        print(f"{pos['symbol']}: {pos['side']} | "
              f"Size: {pos['contracts']} | "
              f"Entry: {pos['entryPrice']} | "
              f"PnL: {pos['unrealizedPnl']}")
```

### Close a Position

```python
def close_position(symbol, side, amount):
    """Close position with a market order."""
    close_side = 'sell' if side == 'long' else 'buy'
    return exchange.create_order(
        symbol, 'market', close_side, amount,
        params={'reduceOnly': True}
    )
```

## Order Management

### Check Order Status

```python
order = exchange.fetch_order(order_id, 'BTC/USDT')
print(order['status'])   # 'open', 'closed', 'canceled'
print(order['filled'])   # Amount filled
print(order['average'])  # Average fill price
```

### Cancel an Order

```python
exchange.cancel_order(order_id, 'BTC/USDT')
```

### List Open Orders

```python
open_orders = exchange.fetch_open_orders('BTC/USDT')
for o in open_orders:
    print(f"{o['type']} {o['side']} {o['amount']} @ {o['price']}")
```

## The Algo Order Problem

**This is the #1 gotcha on Binance Futures.**

Any order with `stopPrice` (STOP, STOP_MARKET, TAKE_PROFIT, TAKE_PROFIT_MARKET) is treated as an **algorithmic/conditional order**. Standard order endpoints can't see them.

```python
# This WON'T find your stop loss order:
order = exchange.fetch_order(sl_order_id, 'BTC/USDT')  # ❌ Not found

# You need the algo order endpoints:
# Check status
result = exchange.fapiPrivateGetAlgoOrder({'algoId': sl_order_id})

# Cancel
result = exchange.fapiPrivateDeleteAlgoOrder({'algoId': sl_order_id})

# List all open algo orders
result = exchange.fapiPrivateGetOpenAlgoOrders()
```

## Price & Amount Precision

Every trading pair has different precision requirements. Sending too many decimals causes errors.

```python
# Get market info
market = exchange.market('BTC/USDT')

# Round to valid precision
amount = exchange.amount_to_precision('BTC/USDT', 0.00123456789)
price = exchange.price_to_precision('BTC/USDT', 84123.456789)

# Get minimum order size
min_amount = market['limits']['amount']['min']
min_cost = market['limits']['cost']['min']
```

## Error Handling

```python
try:
    order = exchange.create_order(...)
except ccxt.InsufficientFunds:
    print("Not enough balance")
except ccxt.InvalidOrder as e:
    if '-2022' in str(e):
        print("ReduceOnly rejected — position already closed")
    elif '-4411' in str(e):
        print("TradFi token — needs agreement signing")
    else:
        print(f"Invalid order: {e}")
except ccxt.NetworkError:
    print("Network timeout — retry")
except ccxt.ExchangeError as e:
    print(f"Exchange error: {e}")
```

### Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| -1021 | Timestamp out of range | Call `load_time_difference()` |
| -2019 | Margin insufficient | Reduce position size or add margin |
| -2022 | ReduceOnly rejected | Position already closed, ignore |
| -4411 | TradFi agreement needed | Exclude equity tokens |
| -1111 | Precision over maximum | Use `amount_to_precision()` |

## Rate Limits

Binance allows ~1200 requests per minute. With `enableRateLimit: True`, ccxt auto-throttles. But with multiple bots on the same IP, you can still hit limits.

**Tips:**
- Don't fetch data you don't need
- Cache market info (`load_markets()` once at startup)
- Stagger API calls if running multiple bots
- Use 5-10 second intervals between scan cycles

## Complete Example: Fetch, Analyze, Trade

```python
import ccxt
import pandas as pd
import ta
import time
import os

# Setup
exchange = ccxt.binance({
    'apiKey': os.environ['BINANCE_API_KEY'],
    'secret': os.environ['BINANCE_SECRET'],
    'options': {'defaultType': 'future', 'adjustForTimeDifference': True},
    'enableRateLimit': True,
})
exchange.load_time_difference()
exchange.set_leverage(3, 'ETH/USDT')

# Fetch and analyze
df = pd.DataFrame(
    exchange.fetch_ohlcv('ETH/USDT', '5m', limit=50),
    columns=['ts', 'open', 'high', 'low', 'close', 'volume']
)
df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

last = df.iloc[-1]
print(f"ETH Price: {last['close']}, RSI: {last['rsi']:.1f}")

# Check balance
balance = exchange.fetch_balance()
print(f"Available: {balance['USDT']['free']} USDT")

# Place a test order (UNCOMMENT WHEN READY)
# order = exchange.create_order('ETH/USDT', 'market', 'buy', 0.01)
# print(f"Order filled at {order['average']}")
```

---

## Further Reading

- [Building a complete trading bot](/posts/building-a-trend-following-bot-that-actually-works/) — Full strategy implementation
- [Stop loss implementation](/posts/stop-loss-the-most-important-feature-you-will-get-wrong/) — Exchange-side STOP_LIMIT
- [Binance API gotchas](/posts/binance-api-gotchas-that-will-waste-your-weekend/) — Edge cases and quirks

---

*ccxt makes Binance easy to connect to. Making money with it is the hard part.*
