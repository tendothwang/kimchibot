---
title: "Binance API Gotchas That Will Waste Your Weekend"
date: 2026-03-26
draft: false
tags: ["binance", "api", "ccxt", "python", "trading-bot"]
categories: ["Engineering"]
summary: "A collection of Binance Futures API quirks that aren't in the documentation. Each one cost me hours."
---

## 1. Time Synchronization Will Break Everything

Your first API call will probably fail with:

```
Timestamp for this request was 1000ms ahead of the server's time
```

Binance requires your request timestamp to be within 1 second of their server time. Your computer's clock drifts. Their server's clock drifts.

**Fix:**

```python
exchange = ccxt.binance({
    'options': {
        'adjustForTimeDifference': True
    }
})
exchange.load_time_difference()
```

And **resync every hour**. I learned this after random failures at 3 AM when nobody was around to restart the bot.

## 2. fetch_balance() — Don't Pass Parameters

On Binance Futures, the "correct" way to fetch your USDT balance:

```python
# WRONG — returns empty or wrong data
balance = exchange.fetch_balance({'type': 'future'})

# RIGHT — just call it plain
balance = exchange.fetch_balance()
```

The `type` parameter behaves differently across exchange versions. Without parameters, ccxt handles the routing correctly for futures.

I spent half a day debugging "why is my balance always zero" because of this.

## 3. STOP Orders Are "Algo Orders"

This is the biggest gotcha. On Binance Futures, any order with a `stopPrice` is treated as a **conditional/algorithmic order**. This means:

- `exchange.fetch_order(id)` → **Can't find it**
- `exchange.cancel_order(id)` → **Fails silently**

You need special API endpoints:

```python
# Check status
exchange.fapiPrivateGetAlgoOrder({'algoId': order_id})

# Cancel
exchange.fapiPrivateDeleteAlgoOrder({'algoId': order_id})

# List open orders
exchange.fapiPrivateGetOpenAlgoOrders()
```

This is barely documented. I only found it by reading ccxt source code and Binance API changelogs.

## 4. ReduceOnly Rejection After Position Close

Race condition: your trailing stop closes a position via market order, then your exchange-side SL triggers on the same position. The SL order gets rejected with:

```
-2022: ReduceOnly order is getting rejected
```

This is actually fine — it means the position is already closed. But if your bot doesn't handle this error gracefully, it'll spam retry loops for 30 seconds.

**Fix:** Catch `-2022` errors and treat them as "position already closed, move on."

## 5. TradFi Tokens Need Agreement Signing

If your bot tries to trade TSLA/USDT, NVDA/USDT, or other equity-backed tokens:

```
-4411: Please sign TradFi-Perps agreement contract fapi
```

You need to sign a legal agreement on the Binance website first. But better yet, just auto-exclude them:

```python
for symbol, market in exchange.markets.items():
    if market.get('info', {}).get('underlyingType') != 'COIN':
        exclude_list.append(symbol)
```

This catches equities, commodities, indices, and pre-market tokens — about 24 pairs that will cause problems.

## 6. Candle Data Timing

When you call `fetch_ohlcv()` right after a 5-minute candle closes, the API might return stale data. The new candle takes 1-3 seconds to appear.

**Wrong approach:**
```python
time.sleep(2)  # Hope for the best
data = exchange.fetch_ohlcv(symbol, '5m', limit=1)
```

**Right approach:**
```python
for attempt in range(5):
    data = exchange.fetch_ohlcv(symbol, '5m', limit=2)
    latest_ts = data[-1][0]
    expected_ts = current_5m_boundary()
    if latest_ts >= expected_ts:
        break
    time.sleep(1)
```

Verify the timestamp. Don't trust sleep timers.

## 7. Order Dust

After closing a position, you sometimes have tiny leftover amounts (0.001 of a coin) that are too small to trade. These show up as phantom positions in your balance.

The API says you have a position. You can't close it because it's below minimum order size. Your bot thinks it's still in a trade.

**Fix:** Check position size against the market's minimum order quantity before treating it as an active position.

## 8. Rate Limits Are Per-IP, Not Per-Key

If you're running multiple bots from the same server, they share rate limits. I found this out when my trend-following bot and FVG bot started getting `429 Too Many Requests` errors simultaneously.

**Fix:** Stagger your API calls. Use `enableRateLimit: True` in ccxt, and add small delays between bot instances.

## 9. Resampled vs Native Candles

This is subtle. If you build 1-hour candles by combining 5-minute candles:

```python
# Resampled — NOT the same as exchange native
df_1h = df_5m.resample('1h').agg({
    'open': 'first', 'high': 'max', 
    'low': 'min', 'close': 'last'
})
```

The RSI calculated from these resampled candles will be **slightly different** from RSI calculated on native 1-hour candles from the exchange.

The difference is tiny — maybe 0.5 RSI points. But when your entry condition is "RSI > 50," that 0.5 can flip the signal.

**Fix:** Always fetch native candles for the timeframe you need. Don't resample.

## The Meta-Lesson

Binance's API is powerful but full of edge cases. The documentation covers the happy path. The unhappy paths — the ones that hit at 3 AM on a Sunday — aren't documented anywhere.

**Build defensively. Log everything. Handle every error code. And test with real (small) money before scaling up.**

---

*The API documentation tells you how it should work. Production tells you how it actually works.*
