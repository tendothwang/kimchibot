---
title: "Surge Detection: Catching Explosive Moves Without Giving It All Back"
date: 2026-03-23
draft: false
tags: ["surge", "trailing-stop", "trading-bot", "crypto", "strategy"]
categories: ["Strategy"]
summary: "When a trade moves +4% in the first 5 minutes, you need special handling. Here's my surge detection system."
---

## The Problem

You enter a trade. Within minutes, it's up 4%. Your normal trailing stop (2% activation, 0.5% trail) hasn't even activated yet.

Then the price reverses. Your 4% winner becomes a 1% winner. Or worse, a loser.

**Explosive moves need explosive risk management.**

## What Is a Surge?

A surge is when price moves aggressively in your favor immediately after entry — before the first 5-minute candle even closes.

In crypto, this happens more often than you'd think. A coin gaps up 5% in 2 minutes on a whale buy, then retraces half of it.

The question is: **how do you keep most of that profit?**

## My Two-Phase System

### Phase 1: The First 5 Minutes (Pre-Candle Close)

If profit reaches +4% before the first 5-minute candle closes:

- **Activate tight trailing stop:** 0.5% behind best price
- **Check on 1-minute candle closes** (not tick-by-tick)

Why 1-minute instead of 5-minute? Because in a surge, 5 minutes is an eternity. The move could completely reverse. 1-minute gives you a balance between capturing the move and not getting stopped by noise.

### Phase 2: After First 5-Minute Close

Once the first 5-minute candle closes, switch to normal trailing:

- Standard trailing activation (2.0%)
- Standard trail stop (0.5%)
- Back to 5-minute candle close checks

The logic: if the surge survived the first 5-minute candle, it might have legs. Give it room to run with normal parameters.

## Why Not Just Use a Tight Trail From the Start?

I tested this in backtests. Tight trailing from entry catches surges but also **prematurely exits normal trades** that dip slightly before continuing. The two-phase approach only activates tight trailing when there's evidence of a genuine surge (+4% before first 5m close).

In my backtests, the two-phase system consistently outperformed both "no surge detection" and "tight trail from entry" across different coins and time periods.

## The Parameter Decisions

### Surge Threshold: 4%

Why not 3%? Too many false surges — normal volatility hits 3% regularly.

Why not 5%? Too few triggers — you miss most real surges.

**4% was the sweet spot** in backtesting across multiple coin sets and time periods.

### Trail Stop: 0.5%

This is wider than you might expect for a "tight" trail. The reason: I check on candle closes, not ticks.

A 1-minute candle can have a 1% wick that recovers. If my trail is 0.3%, that wick stops me out even though the candle closes green.

**0.5% on candle close** is equivalent to roughly **0.2% on tick-by-tick**. It gives the same protection without the noise.

### Why Candle Close, Not Ticks?

This was one of my most important discoveries. My live bot originally checked trailing stops every second via WebSocket. The backtest checked on candle closes.

The live bot was getting stopped out on momentary dips. The backtest was riding through them.

**Candle close = "where did the price settle?" not "where did it spike for 1 second?"**

For surge detection specifically, 1-minute candle closes give you the right resolution without the noise of tick data.

## How It Looks in Practice

Here's the general flow of a surge trade:

```
Entry: Long on a volatile altcoin

+1 min: +2% — Normal, no surge yet
+2 min: +3.8% — Getting there...
+3 min: +5% — SURGE DETECTED! Tight trail activated (0.5% behind best)
+4 min: +4.8% — Trail holds
+5 min (5m close): Phase 2 starts. Switch to normal 5m trailing.

If price keeps running → normal trailing captures more.
If price reverses → tight trail already locked in most of the surge profit.
```

Without surge detection, the normal trailing stop (2% activation) would activate late and capture less of these explosive moves.

## Edge Cases

### Double Surge
Sometimes a coin surges, consolidates, then surges again. Phase 2 handles this naturally — the normal trailing stop gives enough room for a second leg.

### Surge Then Crash
The worst case: coin spikes 5%, you activate the tight trail, then it crashes right through your trail level. You exit at +4.5% instead of the theoretical +5%.

This is fine. You kept most of the move. The alternative (no surge detection) would have you riding it all the way back down.

### Surge on Entry Candle
If the surge happens on the same candle as entry, the 1-minute SL check still applies. You won't get trapped holding through a flash crash.

---

*Surges are gifts. The question isn't whether to take profit — it's how much profit to let slip away before you do.*
