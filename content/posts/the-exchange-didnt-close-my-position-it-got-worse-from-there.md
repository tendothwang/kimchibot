---
title: "The Exchange Didn't Close My Position. It Got Worse From There"
date: 2026-04-15T17:00:00
draft: false
tags: ["debugging", "binance", "api", "crash-recovery", "trading-bot", "bot-autopsy"]
categories: ["Story"]
series: ["Bot Autopsy"]
summary: "My bot tried to close a SHORT position. Binance rejected the order. The bot thought it succeeded. The position bled -121U before I woke up."
---

## What's the worst thing that can happen to a trading bot?

It's not a losing trade. Losing trades are normal — my FVG bot loses 67% of its trades and still makes money.

The worst thing is an **unmanaged position** — a trade that's open on the exchange but invisible to your bot. No stop loss. No take profit. No monitoring. Just an open position silently bleeding money while your bot has already moved on.

This happened to me. Here's the full story.

## The AGT incident

It was a normal night. The bot was running, taking trades, closing positions. Then it tried to close a SHORT position on AGT.

The sequence:

1. Bot detects exit signal on AGT SHORT
2. Bot sends market close order to Binance
3. Binance rejects the order — error `-4131 PERCENT_PRICE` (price moved too far too fast)
4. **Bot treats the rejection as success**
5. Bot removes AGT from its internal state
6. AGT position is still open on Binance — completely unmanaged
7. No stop loss. No monitoring. Nothing.

By the time I woke up and checked, the unrealized loss on AGT was **-121U**.

## Why did the bot think the close succeeded?

The bug was embarrassingly simple:

```python
# THE BUG
try:
    exchange.create_order(symbol, 'market', close_side, amount,
                          params={'reduceOnly': True})
except Exception:
    return '__MARKET_CLOSED__'  # This runs on FAILURE too!
```

The function returned `__MARKET_CLOSED__` in both success and failure cases. The `except` block caught the Binance error and returned the same value as a successful close. The calling code saw "market closed" and happily deleted the position from its state.

One line. One missing distinction between success and failure. -121U.

## What made it worse?

The position had no stop loss. When the bot "closed" the position (but didn't), it also cancelled the associated stop loss order. So now there was:

- An open SHORT position on Binance
- No stop loss protecting it
- No bot monitoring it
- No human aware of it

Price moved against the position for hours. By morning, the damage was done.

## How did I fix it?

### Fix 1: Three-attempt retry

Market close failures are usually temporary — the exchange is busy, price is volatile, there's a network hiccup. A retry 1.5 seconds later usually works.

```python
for attempt in range(3):
    try:
        order = exchange.create_order(
            symbol, 'market', close_side, amount,
            params={'reduceOnly': True}
        )
        return order  # Success — return the order
    except Exception as e:
        log.warning(f"Close attempt {attempt+1} failed: {e}")
        time.sleep(1.5)

return '__MARKET_CLOSE_FAILED__'  # Explicit failure
```

### Fix 2: Explicit failure state

`__MARKET_CLOSE_FAILED__` is now a distinct value from `__MARKET_CLOSED__`. When the caller sees this, it knows the position is **still open** and keeps it in the bot's state.

### Fix 3: Emergency stop loss loop

Failed-close positions are kept in state with an empty stop loss ID. The main loop detects this every cycle and tries to place a new stop loss:

```python
for symbol, pos in positions.items():
    if pos.sl_order_id == '':
        # No stop loss — emergency placement
        try:
            sl_order = place_stop_loss(exchange, symbol, pos)
            pos.sl_order_id = sl_order['id']
        except Exception:
            pass  # Will retry next cycle
```

Even if the close failed, the position gets protected with a stop loss as soon as the exchange accepts orders again.

### Fix 4: Exchange sync on restart

If the bot crashes or restarts, it compares exchange positions against its state file. Any position on the exchange that's not in the state file gets recovered immediately.

## Defense in depth

No single fix is enough. The full defense stack:

| Layer | What it does | Protects against |
|-------|-------------|-----------------|
| Exchange-side STOP_LIMIT | Placed when position opens | Bot crash, code bugs |
| 3-attempt market close | Retries temporary failures | Network issues, exchange busy |
| `__MARKET_CLOSE_FAILED__` | Tracks failed closes explicitly | Silent failures |
| SL re-placement loop | Adds stop loss to unprotected positions | Any missed SL |
| Exchange sync on restart | Catches orphaned positions | Bot restart, state corruption |

Since implementing all five layers, no unmanaged position has lasted more than one scan cycle.

## The lesson that cost -121U

The bug wasn't complicated. It wasn't a race condition or a subtle timing issue. It was the most basic possible error: **not distinguishing between success and failure.**

Every exchange API call can fail. Every single one. And when a close order fails, the consequence isn't "order didn't execute" — it's "you now have an unprotected position that nobody is watching."

The expensive lesson: **never assume an API call succeeded.** Check the return value. Handle the failure explicitly. And have multiple layers of defense for when your first layer fails.

Because it will fail. At 3 AM. On a volatile coin. When you're asleep.

---

*The exchange doesn't care about your exit plan. It cares about whether your order is valid right now, this millisecond. Build for the millisecond it isn't.*

**Related:**
- [When Market Close Fails: Exchange API Nightmares at 3 AM](/posts/when-market-close-fails-exchange-api-nightmares/) — Technical deep dive on close failures
- [My Bot Opened a Trade I Never Asked For](/posts/orphan-orders-the-bug-that-opens-positions-you-didnt-ask-for/) — Another exchange API nightmare
- [What Happens When Your Bot Crashes at 3 AM](/posts/what-happens-when-your-bot-crashes-at-3am/) — Full crash recovery system
