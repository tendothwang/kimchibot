---
title: "Stop Loss: The Most Important Feature You'll Get Wrong"
date: 2026-04-02
draft: false
tags: ["stop-loss", "trading-bot", "binance", "slippage", "crypto"]
categories: ["Lessons"]
summary: "I went from market order SL to exchange-side STOP_LIMIT and it changed everything. Here's every mistake along the way."
---

## Why Stop Loss Is Everything

Your entry strategy doesn't matter if your exit is broken.

I spent weeks perfecting entry signals — candle patterns, volume ratios, RSI crossovers. Beautiful logic. Meanwhile, my stop loss was a simple market order that was silently destroying my returns through slippage.

## Version 1: Client-Side Market Order (Bad)

My first implementation:

```
Every 1 second:
  Check current price via WebSocket
  If loss > 2%:
    Place market sell order
```

**Problems:**
1. **Latency:** 200-500ms between price check and order execution. In a crash, price moves 0.5% in that window.
2. **Slippage:** Market order during high volatility = terrible fill price.
3. **Cascade effect:** Everyone's bots trigger at the same level → massive sell pressure → worse slippage for everyone.

Real example: SL set at -2.0%. Actual exit at -2.8%. That 0.8% difference on a $200 position with 3x leverage = $4.8 extra loss. Multiply by hundreds of trades.

## Version 2: Exchange-Side STOP_LIMIT (Good)

The fix was moving the stop loss to the exchange itself:

```python
exchange.create_order(
    symbol=symbol,
    type='STOP',
    side='sell',        # for longs
    amount=position_size,
    price=limit_price,   # limit price (where to fill)
    params={'stopPrice': trigger_price}  # trigger price
)
```

**Why this is better:**
- The exchange monitors the price, not your bot
- No network latency for the trigger
- Limit order means you control the fill price
- Your bot can crash and the SL still works

## The Gotchas Nobody Tells You

### 1. Binance Treats STOP Orders as "Algo Orders"

This took hours to figure out. On Binance Futures, any order with `stopPrice` is a **conditional/algo order**. Normal `fetch_order()` and `cancel_order()` don't work.

You need special API endpoints:
```python
# Check order status
exchange.fapiPrivateGetAlgoOrder(...)

# Cancel order  
exchange.fapiPrivateDeleteAlgoOrder(...)

# List open orders
exchange.fapiPrivateGetOpenAlgoOrders(...)
```

If you're using ccxt and wondering why your stop order "disappears" — this is why.

### 2. STOP_LIMIT Can Fail to Fill

The trigger fires, but the limit order sits unfilled because price blew right through it.

**My solution:** After the stop triggers, check if the limit order filled within a few seconds. If not, convert to a market order immediately.

```python
def check_sl_filled(order_id):
    order = exchange.fapiPrivateGetAlgoOrder(...)
    if order['status'] == 'TRIGGERED':
        # Limit order is live but might not fill
        if not filled_within_timeout:
            close_at_market()  # Emergency exit
```

### 3. Cancel Failures Are Real

Sometimes `cancel_order` fails. Network timeout, exchange hiccup, whatever. If you just ignore it:

- You exit your position via trailing stop
- The orphaned SL triggers later
- It opens a **new position** in the opposite direction
- You now have an unintended trade

**My fix:** Keep the SL order ID. Before any exit, try to cancel the SL. If cancel fails, retry. If still fails, keep the ID and try again after the exit.

## The Order of Operations Bug

I had the exit sequence wrong for months:

**Wrong order:**
1. Cancel SL order (takes 0.5-1 second)
2. Place market close order
3. → Price moves against you during step 1

**Correct order:**
1. Place market close order (exit first!)
2. Cancel SL order (it's fine if it triggers on a closed position)
3. Handle any ReduceOnly rejection gracefully

The SL is a conditional order — it only triggers at a specific price. Your market close is immediate. Always close first, clean up later.

## best_price vs Current Price

Another subtle bug: I was using the same price variable for two different things.

- **best_price:** The most favorable price reached (for trailing stop calculation)
- **current_price:** The actual current price (for exit decisions)

When a 1-minute candle has a long wick, the extreme value and the close are very different. Mixing them up meant my trailing stops weren't triggering when they should have.

**Fix:** Separate `cp_best` (extreme value, updates best_price) and `cp` (current close price, used for exit checks).

## What I'd Tell My Past Self

1. **Put the SL on the exchange from day 1.** Client-side monitoring is unreliable.
2. **Test the failure modes.** What happens when cancel fails? When the limit doesn't fill? When your bot crashes?
3. **The exit order matters.** Close first, then clean up.
4. **Separate your price variables.** One price for tracking, another for decisions.

The stop loss is the most boring part of a trading bot. It's also the part that will cost you the most money if you get it wrong.

---

*A good stop loss won't make you money. A bad stop loss will definitely lose you money.*
