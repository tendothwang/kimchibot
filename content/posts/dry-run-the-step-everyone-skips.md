---
title: "Dry Run: The Step Everyone Skips"
date: 2026-03-20
draft: false
tags: ["dry-run", "paper-trading", "testing", "trading-bot", "crypto"]
categories: ["Guide"]
summary: "Between backtest and live trading, there's a step most people skip. It's the step that catches the bugs that matter most."
---

## The Gap Nobody Talks About

The typical trading bot journey:

1. Build strategy ✓
2. Backtest it ✓
3. Deploy with real money ← **HERE BE DRAGONS**

What's missing? **The dry run.**

A dry run is your bot running in real-time, with real market data, making real decisions — but not placing real orders. Paper trading, but automated.

## Why Backtests Aren't Enough

Your backtest runs on historical data. It has perfect information:
- Every candle is complete
- Every price is final
- There's no latency
- There's no partial fill
- The exchange never returns an error

Real markets are messier. The dry run catches the mess.

### What I Found in Dry Runs

1. **5-minute candle data lag** — My bot fetched candles right at the close, but the exchange API hadn't updated yet. The bot was making decisions on stale data.

2. **Rate limiting** — With 8 coins, scanning every 5 minutes, plus position monitoring — the API calls added up faster than expected.

3. **Order of operations** — My backtest checked SL then trailing. My live code checked trailing then SL. Different results on the same data.

4. **RSI warmup** — I was fetching 20 candles for RSI calculation. RSI needs ~40 candles to stabilize. My first few signals were based on garbage RSI values.

## How to Run a Dry Run

The simplest approach:

```python
DRY_RUN = True

def place_order(symbol, side, amount, price):
    if DRY_RUN:
        log(f"[DRY] Would {side} {amount} {symbol} at {price}")
        return {'id': 'dry_' + str(time.time()), 'status': 'filled'}
    else:
        return exchange.create_order(...)
```

Everything else runs exactly the same:
- Data fetching: real
- Signal calculation: real
- Position tracking: simulated
- Order placement: logged but not executed

## The Comparison Tool

After running the dry bot for a few days, compare its decisions against the backtest for the same period:

```bash
python compare_live_bt.py "2026-03-15" "2026-03-18"
```

This shows:
- **Entry matches:** Did the dry bot and backtest enter the same trades?
- **Entry price:** Would the entry price have been the same?
- **Exit reason:** SL, trailing, time-based — do they agree?
- **PnL:** How close are the numbers?

### My First Comparison Result

| Metric | Match Rate |
|--------|-----------|
| Entry signals | 78% |
| Entry prices | 92% |
| Exit reasons | 71% |
| PnL (±10%) | 65% |

**65% PnL match. Terrible.** But this was before fixing the timezone bug, the candle resampling issue, and the trailing stop tick-vs-close problem.

### After Fixing Everything

| Metric | Match Rate |
|--------|-----------|
| Entry signals | 98% |
| Entry prices | 100% |
| Exit reasons | 94% |
| PnL (±10%) | 83% |

**83% PnL match.** The remaining 17% is genuine market slippage and SL timing — things that can't be simulated.

## How Long to Dry Run

**Minimum:** 1 week. This catches most timing and data bugs.

**Better:** 2-4 weeks. This covers different market conditions and edge cases like exchange maintenance windows.

**When to stop:** When your live-backtest match rate stabilizes above 80% and you understand every discrepancy.

## The Psychological Benefit

Dry running also prepares you psychologically:

- You see real drawdowns happening in real-time
- You experience 5 stop losses in a row
- You watch a trade go +3% and then reverse to -1%
- You feel the urge to manually intervene

If you can't handle watching the dry bot lose, you definitely can't handle it with real money.

**The dry run isn't just a technical test. It's a stress test for you.**

## The Final Checklist

Before going from dry run to live:

- [ ] Match rate above 80% for 1+ week
- [ ] All known discrepancies explained and documented
- [ ] Edge cases tested (restart recovery, network failure)
- [ ] Psychological readiness (survived watching drawdowns)
- [ ] Start with **minimum position size** for the first live week

The extra week of dry running has never cost me money. Skipping it has.

---

*A dry run is boring. Losing money because you skipped it is exciting in all the wrong ways.*
