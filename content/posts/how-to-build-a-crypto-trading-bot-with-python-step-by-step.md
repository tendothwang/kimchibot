---
title: "How to Build a Crypto Trading Bot with Python: Step-by-Step Guide"
date: 2026-04-08
draft: false
tags: ["python", "tutorial", "trading-bot", "crypto", "binance", "ccxt", "beginner"]
categories: ["Guide"]
summary: "A complete beginner's guide to building a crypto trading bot with Python and ccxt. From zero to a working bot on Binance Futures."
---

## What You'll Build

By the end of this guide, you'll have a working crypto trading bot that:
- Connects to Binance Futures
- Fetches real-time price data
- Detects entry signals based on technical indicators
- Places orders automatically
- Manages stop losses and take profits

**Prerequisites:** Basic Python knowledge. That's it.

## Step 1: Set Up Your Environment

```bash
pip install ccxt pandas ta
```

- **ccxt** — Connects to 100+ crypto exchanges with one API
- **pandas** — Data manipulation
- **ta** — Technical indicators (RSI, MACD, etc.)

## Step 2: Connect to Binance

First, create a Binance account and generate API keys (under API Management).

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
    'options': {
        'defaultType': 'future',           # Futures trading
        'adjustForTimeDifference': True,    # Sync clocks
    },
    'enableRateLimit': True,
})

# IMPORTANT: Load time difference to avoid timestamp errors
exchange.load_time_difference()
```

**Security warning:** Never hardcode API keys in your script. Use environment variables:

```python
import os

exchange = ccxt.binance({
    'apiKey': os.environ['BINANCE_API_KEY'],
    'secret': os.environ['BINANCE_SECRET'],
    # ...
})
```

## Step 3: Fetch Price Data

```python
import pandas as pd

def get_candles(symbol, timeframe='5m', limit=100):
    """Fetch OHLCV candles from Binance."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Example
df = get_candles('BTC/USDT', '5m', 100)
print(df.tail())
```

Output:
```
              timestamp     open     high      low    close     volume
95  2026-04-08 12:35:00  84521.0  84589.0  84498.0  84562.0  1523.456
96  2026-04-08 12:40:00  84562.0  84601.0  84531.0  84577.0  1102.789
97  2026-04-08 12:45:00  84577.0  84612.0  84555.0  84598.0   987.654
98  2026-04-08 12:50:00  84598.0  84634.0  84570.0  84615.0  1345.012
99  2026-04-08 12:55:00  84615.0  84678.0  84601.0  84667.0  1876.543
```

## Step 4: Calculate Indicators

```python
import ta

def add_indicators(df):
    """Add technical indicators to the dataframe."""
    # RSI - Relative Strength Index
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    
    # Volume Ratio - current volume vs 20-period average
    df['vol_avg'] = df['volume'].rolling(20).mean()
    df['vol_ratio'] = df['volume'] / df['vol_avg']
    
    # Candle body size as percentage
    df['body_pct'] = abs(df['close'] - df['open']) / df['open'] * 100
    
    return df

df = add_indicators(df)
```

## Step 5: Define Entry Signals

Here's a simple trend-following signal:

```python
def check_signal(df):
    """Check if we should enter a trade."""
    last = df.iloc[-1]      # Current candle
    prev = df.iloc[-2]      # Previous candle
    
    # Long signal conditions
    long_signal = (
        last['body_pct'] >= 0.5          # Strong candle
        and last['close'] > last['open']  # Bullish
        and last['vol_ratio'] >= 1.5      # Above-average volume
        and last['rsi'] > 50              # Upward momentum
        and last['rsi'] < 70              # Not overbought
    )
    
    # Short signal conditions
    short_signal = (
        last['body_pct'] >= 0.5          # Strong candle
        and last['close'] < last['open']  # Bearish
        and last['vol_ratio'] >= 1.5      # Above-average volume
        and last['rsi'] < 50              # Downward momentum
        and last['rsi'] > 30              # Not oversold
    )
    
    if long_signal:
        return 'long'
    elif short_signal:
        return 'short'
    return None
```

## Step 6: Place Orders

```python
def open_position(symbol, side, usdt_amount, leverage=3):
    """Open a futures position."""
    # Set leverage
    exchange.set_leverage(leverage, symbol)
    
    # Get current price
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    
    # Calculate position size
    amount = (usdt_amount * leverage) / price
    
    # Place market order
    order_side = 'buy' if side == 'long' else 'sell'
    order = exchange.create_order(
        symbol=symbol,
        type='market',
        side=order_side,
        amount=amount,
    )
    
    print(f"Opened {side} {symbol} | Size: {amount:.4f} | Price: {price}")
    return order

def close_position(symbol, side, amount):
    """Close a futures position."""
    order_side = 'sell' if side == 'long' else 'buy'
    order = exchange.create_order(
        symbol=symbol,
        type='market',
        side=order_side,
        amount=amount,
        params={'reduceOnly': True}
    )
    print(f"Closed {side} {symbol}")
    return order
```

## Step 7: Add Stop Loss

**Critical:** Always use exchange-side stop losses, not client-side monitoring.

```python
def place_stop_loss(symbol, side, entry_price, sl_pct=0.02):
    """Place a stop loss order on the exchange."""
    if side == 'long':
        stop_price = entry_price * (1 - sl_pct)
        order_side = 'sell'
    else:
        stop_price = entry_price * (1 + sl_pct)
        order_side = 'buy'
    
    # Round to valid price precision
    stop_price = float(exchange.price_to_precision(symbol, stop_price))
    
    order = exchange.create_order(
        symbol=symbol,
        type='STOP_MARKET',
        side=order_side,
        amount=position_size,
        params={
            'stopPrice': stop_price,
            'reduceOnly': True,
        }
    )
    
    print(f"SL placed at {stop_price} ({sl_pct*100}% from entry)")
    return order
```

## Step 8: The Main Loop

Putting it all together:

```python
import time

SYMBOL = 'BTC/USDT'
TRADE_USDT = 100      # $100 per trade
LEVERAGE = 3
SL_PCT = 0.02         # 2% stop loss
SCAN_INTERVAL = 300   # 5 minutes

position = None

while True:
    try:
        # Fetch fresh data
        df = get_candles(SYMBOL, '5m', limit=50)
        df = add_indicators(df)
        
        if position is None:
            # Check for entry signal
            signal = check_signal(df)
            
            if signal:
                order = open_position(SYMBOL, signal, TRADE_USDT, LEVERAGE)
                entry_price = float(order['average'])
                
                sl_order = place_stop_loss(
                    SYMBOL, signal, entry_price, SL_PCT
                )
                
                position = {
                    'side': signal,
                    'entry_price': entry_price,
                    'sl_order_id': sl_order['id'],
                }
                print(f"Position opened: {position}")
        
        else:
            # Monitor existing position
            current_price = df.iloc[-1]['close']
            
            if position['side'] == 'long':
                pnl_pct = (current_price - position['entry_price']) / position['entry_price']
            else:
                pnl_pct = (position['entry_price'] - current_price) / position['entry_price']
            
            print(f"Position PnL: {pnl_pct*100:.2f}%")
            
            # Take profit at 3%
            if pnl_pct >= 0.03:
                close_position(SYMBOL, position['side'], order['amount'])
                position = None
                print("Take profit hit!")
        
        time.sleep(SCAN_INTERVAL)
    
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
        time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
```

## Step 9: What This Bot Is Missing

This tutorial gives you a **working foundation**. But a production bot needs more:

| Feature | Why It Matters |
|---------|---------------|
| **Trailing stop** | Lock in profits as price moves in your favor |
| **Position sizing** | Risk management based on account balance |
| **Multiple coins** | Diversification and more opportunities |
| **State persistence** | Survive restarts without losing track of positions |
| **Logging** | Debug issues when you're not watching |
| **PID lockfile** | Prevent duplicate bot instances |
| **Backtest** | Verify your strategy works before risking real money |

I've built all of these. Check the rest of this blog for deep dives on each topic.

## Step 10: Test Safely

**DO NOT run this with real money immediately.**

1. **Backtest first** — Test on historical data
2. **Testnet** — Binance has a futures testnet at testnet.binancefuture.com
3. **Dry run** — Run the bot with logging but no real orders
4. **Small size** — Start with the minimum trade amount ($5-10)

The biggest risk isn't a bad strategy — it's a bug in your code placing an order you didn't intend.

## Common Pitfalls

### 1. Timestamp Errors
```
Timestamp for this request was 1000ms ahead of the server's time
```
**Fix:** Use `adjustForTimeDifference: True` and call `load_time_difference()`.

### 2. Insufficient Balance
Make sure you have USDT in your **Futures** wallet, not your Spot wallet. Transfer first.

### 3. Leverage Not Set
If you don't call `set_leverage()`, Binance uses whatever leverage was set last (possibly 20x from when you were clicking around the UI).

### 4. Rounding Errors
Every trading pair has different precision requirements. Always use:
```python
amount = exchange.amount_to_precision(symbol, amount)
price = exchange.price_to_precision(symbol, price)
```

---

## Next Steps

This is just the beginning. To build a bot that actually makes money consistently, you'll need to:

1. **[Build a proper backtest](/posts/backtest-vs-reality-where-dreams-die/)** — Don't trust your strategy without testing it
2. **[Understand risk-reward](/posts/risk-reward-ratio-the-only-number-that-matters/)** — Win rate doesn't matter as much as you think
3. **[Handle stop losses properly](/posts/stop-loss-the-most-important-feature-you-will-get-wrong/)** — The most important feature in your bot
4. **[Avoid overfitting](/posts/the-backtest-looked-amazing-it-was-lying/)** — The trap every new bot builder falls into

Happy building. And remember — **backtest before you trade real money.**

---

*This guide gets you from zero to a working bot. The other 50 posts on this blog are about going from a working bot to a profitable one.*
