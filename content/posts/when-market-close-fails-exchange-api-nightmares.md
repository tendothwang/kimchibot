---
title: "When Market Close Fails: Exchange API Nightmares at 3 AM"
date: 2026-04-10T17:00:00
draft: false
tags: ["debugging", "binance", "api", "trading-bot", "crash-recovery", "ccxt"]
categories: ["Engineering"]
summary: "My bot tried to close a position. The exchange said no. Three times. Here's what happens when market close fails and how to survive it."
---

## What happens when a market close order fails?

You'd think closing a position is simple. Place a market order, done. But on Binance Futures, market close orders can fail:

- **`-2021` error** — Order would immediately trigger (a timing race condition)
- **`-4131` PERCENT_PRICE** — Price moved too far too fast, order rejected
- **Network timeout** — The request never reached Binance
- **Exchange maintenance** — Binance goes down for 30 seconds (always at the worst time)

When a close order fails, you have an **unmanaged position**. No trailing stop. No exit plan. Just an open trade bleeding money while your bot throws errors into the void.

## The AGT incident: -121U from a failed market close

This actually happened. Here's the timeline:

1. Bot detects exit signal on AGT SHORT position
2. Places market close order
3. Binance returns `-4131 PERCENT_PRICE` — price moved too far, order rejected
4. **Bot treats the failure as success** (the original bug: returning `__MARKET_CLOSED__` on failure)
5. Bot removes the position from its state
6. Position is still open on the exchange — **completely unmanaged**
7. AGT price moves against the position
8. Unrealized loss reaches **-121U** before I manually intervene
9. I manually close 30% at a loss of -37.2U
10. Remaining position recovered via `sync_with_exchange` on bot restart

## Why did the bot think the close succeeded?

The bug was in the error handling:

```python
# THE BUG — failure looks like success
try:
    exchange.create_order(symbol, 'market', close_side, amount, 
                          params={'reduceOnly': True})
except Exception:
    return '__MARKET_CLOSED__'  # Wrong! This is a failure!
```

The function returned `__MARKET_CLOSED__` in both success and failure cases. The caller assumed the position was closed and stopped monitoring it.

## How did I fix it?

### 1. Three-attempt retry with delay

```python
def close_position_market(exchange, symbol, side, amount):
    close_side = 'sell' if side == 'long' else 'buy'
    
    for attempt in range(3):
        try:
            order = exchange.create_order(
                symbol, 'market', close_side, amount,
                params={'reduceOnly': True}
            )
            return order  # Success
        except Exception as e:
            log.warning(f"Market close attempt {attempt+1} failed: {e}")
            time.sleep(1.5)
    
    # All 3 attempts failed
    return '__MARKET_CLOSE_FAILED__'
```

### 2. Explicit failure state

When all 3 attempts fail, the bot now returns `__MARKET_CLOSE_FAILED__` — a distinct value from `__MARKET_CLOSED__`. The caller knows the position is **still open**.

### 3. SL re-placement loop

Failed-close positions are kept in the bot's state with `sl_order_id = ''`. The main loop detects this and tries to place a new stop loss every cycle:

```python
# In main loop
for symbol, pos in positions.items():
    if pos.sl_order_id == '':
        # Position has no SL — emergency re-placement
        try:
            sl_order = place_stop_loss(exchange, symbol, pos)
            pos.sl_order_id = sl_order['id']
            log.info(f"Emergency SL placed for {symbol}")
        except Exception as e:
            log.error(f"SL re-placement failed for {symbol}: {e}")
```

This means even if the close failed, the position gets a stop loss as soon as the exchange accepts orders again.

### 4. Exchange sync on restart

If the bot crashes or restarts, `sync_with_exchange` compares exchange positions against the state file. Any position on the exchange that's not in the state file gets recovered with `sl_price = 0` (triggering immediate SL placement).

## What other close failures can happen?

| Error | Cause | Solution |
|-------|-------|----------|
| `-2021` | Order would trigger immediately | Retry after 1.5 seconds |
| `-4131` PERCENT_PRICE | Price moved too far too fast | Retry — price calms down |
| `-2022` ReduceOnly rejected | Position already closed | Treat as success — ignore |
| Network timeout | Connection dropped | Retry with backoff |
| `-1015` Too many orders | Rate limited | Wait 10 seconds, retry |

The key insight: **most close failures are temporary**. The exchange is busy, the price is volatile, the network hiccupped. A retry 1.5 seconds later usually succeeds.

The dangerous case is when all 3 retries fail. That means something is seriously wrong — exchange downtime, API changes, or a problem with the specific trading pair.

## How do you protect against unmanaged positions?

Defense in depth:

1. **Exchange-side STOP_LIMIT** — Placed when the position opens. Survives bot crashes and close failures.
2. **3-attempt market close** — Most failures are temporary.
3. **`__MARKET_CLOSE_FAILED__` state** — Explicit tracking of positions that couldn't be closed.
4. **SL re-placement loop** — If the close failed, at least get a stop loss on it.
5. **Exchange sync on restart** — Catch anything that fell through the cracks.

No single layer is perfect. Together, they've prevented any unmanaged position from lasting more than one scan cycle since the fix.

---

*The exchange doesn't care about your exit strategy. It cares about whether your order is valid right now, this millisecond. Build for the millisecond it isn't.*

**Related:**
- [Orphan Orders](/posts/orphan-orders-the-bug-that-opens-positions-you-didnt-ask-for/) — Another exchange API nightmare
- [What Happens When Your Bot Crashes at 3 AM](/posts/what-happens-when-your-bot-crashes-at-3am/) — Full crash recovery system
- [STOP_MARKET vs STOP_LIMIT](/posts/stop-market-vs-stop-limit-why-market-stops-are-stealing-your-money/) — Why exchange-side stops matter
