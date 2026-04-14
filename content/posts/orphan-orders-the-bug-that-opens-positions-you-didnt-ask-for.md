---
title: "Orphan Orders: The Bug That Opens Positions You Didn't Ask For"
date: 2026-04-10T14:00:00
draft: false
tags: ["debugging", "binance", "algo-orders", "trading-bot", "stop-loss", "ccxt", "bot-autopsy"]
categories: ["Story"]
series: ["Bot Autopsy"]
summary: "My bot left a stop loss order on the exchange after closing a position. Hours later, it triggered and opened an unintended trade. Here's what caused it and how I fixed it."
---

## What is an orphan order in crypto trading?

An orphan order is a stop loss (or take profit) order that gets left behind on the exchange after the position it was protecting has already been closed.

It sits there, invisible, waiting. When the price hits its trigger, it opens a **new position you never intended**.

This happened to me. Here's the full story.

## How did the orphan order happen?

The sequence:

1. Bot opens a SHORT position on ENJ
2. Places a STOP_LIMIT order as stop loss (algoId = `1000001302050842`)
3. Binance algo API has a hiccup — the bot doesn't get a valid response
4. Bot thinks the SL wasn't placed, so it places a **second** SL (new algoId)
5. Now there are **two** SL orders on the exchange for one position
6. Bot closes the position normally via trailing stop
7. Bot cancels the SL — but only the **second** one (the last ID it saved)
8. First SL (algoId `1000001302050842`) is still live on the exchange
9. Price later hits the orphaned SL trigger
10. **Unintended position opens**

## Why didn't the cleanup catch it?

My bot had a `_cancel_all_open_orders` function that was supposed to clean up all orders for a symbol after closing a position. It calls `fapiPrivateGetOpenAlgoOrders` to find any remaining algo orders.

The problem: **the algo order query also failed**, and the error handler was:

```python
except:
    pass  # This was the bug
```

Silent failure. The query failed, the orphan survived, and nobody knew until it triggered.

## How did I fix it?

Three changes:

### 1. Retry algo order queries

```python
# Before: single attempt, silent failure
try:
    result = exchange.fapiPrivateGetOpenAlgoOrders()
except:
    pass

# After: retry with logging
for attempt in range(2):
    try:
        result = exchange.fapiPrivateGetOpenAlgoOrders()
        break
    except Exception as e:
        log.warning(f"Algo order query failed (attempt {attempt+1}): {e}")
        time.sleep(1)
```

### 2. Log every cancel failure

No more `except: pass`. Every failed cancel gets logged so I can investigate.

### 3. Simplified symbol matching

The algo order API returns raw symbols (`ENJUSDT`) while ccxt uses formatted symbols (`ENJ/USDT`). My matching logic was overcomplicated and sometimes missed matches. Simplified to direct raw symbol comparison.

## What are the warning signs of orphan orders?

Watch for these in your logs:

- **Unexpected positions** appearing without entry signals
- **ReduceOnly rejections** — an orphaned order triggering on a closed position
- **SL placement count** > position count — more stops than positions means duplicates exist
- **Algo API errors** followed by silence — the dangerous `except: pass` pattern

## How do you prevent orphan orders in trading bots?

1. **Never silently swallow API errors.** `except: pass` on exchange operations is a guaranteed future disaster.

2. **Retry critical operations.** Algo order queries and cancels deserve at least 2 attempts with a short delay.

3. **Cancel ALL orders for a symbol, not just the last ID.** Query `fapiPrivateGetOpenAlgoOrders`, filter by symbol, cancel everything.

4. **Periodic audit.** Every few minutes, compare your state file against actual exchange positions and open orders. Flag any mismatch.

5. **Use `reduceOnly` on all SL/TP orders.** This limits the damage — an orphaned `reduceOnly` order on a closed position gets rejected instead of opening a new trade. But don't rely on this alone; some edge cases bypass it.

## What did this bug cost?

In my case, the orphan was caught before it caused significant damage. But the AGT incident the day before — where a market close failed and left a position unmanaged — cost **-121U in unrealized losses** before I manually intervened.

These aren't strategy failures. They're **infrastructure failures**. The strategy was right. The execution had gaps.

---

*The scariest bugs in trading bots aren't the ones that lose money on bad trades. They're the ones that make trades you never asked for.*

**Related:**
- [Binance API Gotchas](/posts/binance-api-gotchas-that-will-waste-your-weekend/) — More exchange API traps
- [What Happens When Your Bot Crashes at 3 AM](/posts/what-happens-when-your-bot-crashes-at-3am/) — Crash recovery systems
- [Stop Loss Implementation](/posts/stop-loss-the-most-important-feature-you-will-get-wrong/) — STOP_LIMIT deep dive
