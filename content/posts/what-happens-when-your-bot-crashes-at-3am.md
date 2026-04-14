---
title: "What Happens When Your Bot Crashes at 3 AM"
date: 2026-03-22
draft: false
tags: ["reliability", "crash-recovery", "trading-bot", "python", "devops", "bot-autopsy"]
categories: ["Story"]
series: ["Bot Autopsy"]
summary: "Your bot will crash. At night. On a weekend. With open positions. Here's how to make sure it recovers gracefully."
---

## It Will Happen

Your bot will crash. Not if — when.

- Network timeout at 3 AM
- Exchange maintenance window you didn't know about
- Unhandled exception in an edge case
- Your VPS runs out of memory
- Python segfault (yes, really)

When it crashes, you might have **open positions with no stop loss monitoring**. This is where accounts blow up.

## The Recovery Problem

When your bot restarts, it needs to answer:

1. Do I have open positions?
2. What were the entry prices?
3. Are there stop loss orders on the exchange?
4. What state was the trailing stop in?

If it can't answer these questions, it's blind. It might open duplicate positions, or worse, leave existing positions unmanaged.

## My Recovery System

### Step 1: State File

Every position change is saved to `state.json`:

```json
{
  "positions": {
    "SIREN/USDT": {
      "side": "long",
      "entry_price": 0.0523,
      "size": 1000,
      "sl_price": 0.0512,
      "sl_order_id": "algo_123456",
      "best_price": 0.0545,
      "trade_usdt": 200,
      "entry_time": "2026-03-22T14:32:15"
    }
  }
}
```

This file is the bot's memory. Without it, a restart is a cold start.

### Step 2: Exchange Sync

State files can be wrong. Maybe the bot crashed between placing an order and updating the file. So on startup:

```python
def sync_with_exchange():
    # What does the exchange say we have?
    exchange_positions = exchange.fetch_positions()
    
    # What does our state file say?
    state_positions = load_state()
    
    # Reconcile
    for pos in exchange_positions:
        if pos not in state_positions:
            # Exchange has it, we don't know about it
            # → Recover from exchange data
            recover_position(pos)
        
    for pos in state_positions:
        if pos not in exchange_positions:
            # We think we have it, exchange doesn't
            # → Position was closed while we were down
            remove_from_state(pos)
```

### Step 3: SL Order Verification

For each recovered position, check if the stop loss order is still on the exchange:

- **SL exists and active:** Great, do nothing
- **SL exists but triggered:** Position might be closed, verify
- **SL missing:** Place a new one immediately

The scariest case is a position with no SL. This is an **unprotected position** — unlimited downside. The bot's first priority on restart is making sure every position has a stop loss.

### Step 4: Deep Recovery Edge Cases

What if the bot crashed right after opening a position but before placing the SL?

```python
# In pending_orders, we have the intended SL price
if position.sl_price == 0 and symbol in pending_orders:
    # Recover SL from pending order data
    position.sl_price = pending_orders[symbol].sl_price
    place_sl_order(position)
```

What if the position is already at -20% loss?

```python
if current_loss_pct > 20:
    # Don't place SL — it would trigger immediately
    # and cascade with slippage
    log("WARNING: Position deeply underwater, manual review needed")
    skip_sl_placement = True
```

## The Balance Check

Before any trading logic runs, verify you can actually fetch your balance:

```python
try:
    balance = exchange.fetch_balance()
except Exception as e:
    log(f"Balance fetch failed: {e}")
    # DO NOT scan for new signals
    # Only monitor existing positions
    skip_new_entries = True
```

If you can't check your balance, you don't know how much capital is available. Don't open new positions blind.

## Defensive Coding Patterns

### Every API Call Gets a Try/Except

```python
def safe_fetch(func, *args, retries=3, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except ccxt.NetworkError:
            time.sleep(2 ** attempt)
        except ccxt.ExchangeError as e:
            log(f"Exchange error: {e}")
            return None
    return None
```

### State Saves After Every Change

Not at the end of the loop. Not every minute. **After every state change.**

```python
def open_position(symbol, side, entry_price, size):
    # ... place orders ...
    state.positions[symbol] = position_data
    state.save()  # Immediately
```

If the bot crashes 1 second after opening a position, the state file has it.

### Graceful Shutdown

```python
import signal

def shutdown_handler(signum, frame):
    log("Shutdown signal received")
    state.save()
    release_lock()
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

CTRL+C and system kill signals trigger a clean save before exit.

## The Lesson

The difference between a toy bot and a production bot is crash recovery.

A toy bot works great when everything is normal. A production bot works great when everything is on fire.

**Assume your bot will crash with open positions. Build the recovery before you build the strategy.**

---

*Your bot's job isn't just to make money. It's to not lose money when things go wrong.*
