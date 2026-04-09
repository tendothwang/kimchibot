---
title: "WebSocket vs REST API: I Deleted 150 Lines and Nothing Broke"
date: 2026-03-31
draft: false
tags: ["websocket", "rest-api", "binance", "trading-bot", "python"]
categories: ["Engineering"]
summary: "I spent weeks building a WebSocket price feed. Then I realized I didn't need it at all."
---

## The Obvious Choice

Every trading bot tutorial tells you the same thing: **use WebSocket for real-time prices.**

And it makes sense. WebSocket gives you price updates every second. REST API requires you to poll. Real-time is always better than polling, right?

I built a full `WebSocketManager` class. ~150 lines of code. Async connections, automatic reconnection, price buffering, extreme value tracking.

Then I deleted all of it.

## What WebSocket Was Doing

My WebSocket connection served three purposes:

1. **Extreme value tracking** — Catching the highest/lowest price every second for trailing stop calculations
2. **Real-time price** — Current price for exit decisions
3. **Candle close detection** — Knowing exactly when a 5-minute candle closed

All three seemed critical. None of them were.

## Why I Didn't Need It

### 1. Extreme Values: 1-Minute Candles Are Better

My backtest uses 1-minute candle high/low for extreme values. My live bot was using WebSocket tick-by-tick extremes.

**They gave different numbers.**

WebSocket catches micro-spikes that don't even show up on 1-minute candles. This meant my live bot's trailing stop activated at different points than the backtest predicted.

The fix wasn't to make the backtest use ticks — it was to make the live bot use 1-minute candles too. One REST call every minute: `fetch_ohlcv(symbol, '1m', limit=6)`.

**Simpler. More reliable. Matches the backtest exactly.**

### 2. Real-Time Price: STOP_LIMIT Makes It Unnecessary

My original bot checked the price every second to detect stop loss hits. But after switching to exchange-side STOP_LIMIT orders, the exchange monitors the price for me.

The SL triggers server-side. My bot doesn't need to watch the price anymore.

### 3. Candle Close Detection: The Clock Works Fine

I had a clever system that detected when a new candle arrived via WebSocket. 

Turns out, `datetime.now().minute % 5 == 0` works just as well. 5-minute candles close every 5 minutes. The clock is right there.

## What I Replaced It With

```python
SCAN_INTERVAL = 10  # seconds

while True:
    for symbol in active_coins:
        check_and_exit(symbol)
    
    if is_new_5m_candle():
        scan_for_entries()
    
    time.sleep(SCAN_INTERVAL)
```

10-second REST polling. That's it.

## The Benefits of Deletion

### Fewer Failure Modes
WebSocket connections drop. They need reconnection logic. They have authentication timeouts. They consume memory with buffered data.

REST polling either works or raises an exception. Simple.

### Easier Debugging
With WebSocket, I was debugging async race conditions, stale data in buffers, and connection state management.

With REST, the data is always fresh — you asked for it just now.

### Lower Complexity
150 lines deleted. Three imports removed (`websockets`, `asyncio`, `deque`). One fewer class to maintain.

**The best code is code that doesn't exist.**

## When You DO Need WebSocket

WebSocket is genuinely necessary when:
- You're market-making and need sub-100ms price updates
- You're doing high-frequency trading
- You need order book depth in real-time
- Your strategy depends on tick-by-tick price action

My bot trades on 5-minute candles. Checking the price every 10 seconds is more than enough. I was over-engineering a solution for a problem I didn't have.

## The Lesson

**Don't add complexity because it seems professional.** Add it because you need it.

I built WebSocket because "real trading bots use WebSocket." I deleted it because my actual strategy didn't benefit from it. The bot got simpler, more reliable, and easier to match with backtests.

Sometimes the best engineering decision is to delete the thing you spent a week building.

---

*Lines of code deleted: 150. Bugs fixed by deletion: at least 3. Regrets: 0.*
