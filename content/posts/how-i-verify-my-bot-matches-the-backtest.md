---
title: "How I Verify My Bot Matches the Backtest (The Compare Tool)"
date: 2026-04-10T15:00:00
draft: false
tags: ["backtesting", "verification", "trading-bot", "python", "crypto", "live-trading"]
categories: ["Engineering"]
summary: "If your live bot doesn't match your backtest, your backtest is fiction. Here's the comparison tool I built and the bugs it caught."
---

## Why does live-backtest comparison matter?

Your backtest says +500U. Your live bot shows +200U. Where did the other 300 go?

If you can't answer that question with specific, trade-by-trade explanations, your backtest is useless. You're optimizing fiction.

I built a comparison tool that runs my backtest over the exact same period my live bot traded, then compares every single trade. It's the most important tool in my entire system.

## How does the comparison tool work?

```bash
python compare_live_bt.py "2026-03-10" "2026-03-12"
```

This does three things:

1. **Pulls live trade logs** from the bot's state and trade history
2. **Runs the backtest** over the same date range with matching parameters
3. **Compares** entry times, entry prices, exit reasons, and PnL for each trade

The output flags every discrepancy: missed entries, different exit reasons, PnL differences.

## What match rate should you expect?

When I first built the comparison tool, my match rate was terrible:

| Metric | First Run |
|--------|-----------|
| Entry signals | 78% |
| Entry prices | 92% |
| Exit reasons | 71% |
| PnL (±10%) | 65% |

After fixing every discrepancy I found, the numbers improved significantly. In a verification run with 18 live trades, **15 matched the backtest exactly (83%)**. The remaining 3 had minor SL/trailing timing differences.

## What bugs did the comparison tool catch?

### 1. The timezone bug (9 hours of missing trades)

The backtest used a naive datetime that the exchange interpreted as UTC. My local time is KST (UTC+9). The backtest was starting 9 hours late every day.

**How it showed up in the tool:** Morning trades existed in live logs but not in backtest results.

**Fix:** Convert `start_dt` to UTC before passing to the exchange API.

### 2. Trailing stop: tick vs candle close

My live bot checked trailing stops every 1 second via WebSocket. The backtest checked on 5-minute candle closes.

**How it showed up:** Live bot exits were systematically earlier than backtest exits. The live bot got stopped out on momentary dips that recovered within the same candle.

**Fix:** Changed the live bot to check trailing stops only at 5-minute candle closes, matching the backtest.

### 3. Resampled vs native candles

The backtest built 30-minute and 1-hour candles by resampling 5-minute data. The live bot fetched native candles from Binance. RSI values differed slightly.

**How it showed up:** Edge-case entries where RSI was close to the threshold (e.g., RSI 50.2 in backtest vs 49.8 in live).

**Fix:** Backtest now fetches native 30m/1h/4h candles directly from the exchange.

### 4. best_price tracking

Live bot tracked best_price using WebSocket tick extremes. Backtest used 1-minute candle high/low. Different values meant different trailing stop activation points.

**How it showed up:** Trailing stops activated at different times, leading to PnL differences of several USDT per trade.

**Fix:** Both now use 1-minute candle extremes.

## What are the key rules for live-backtest comparison?

Rules I follow every time I run a comparison:

1. **Warmup period** — The backtest automatically adds 7 warmup days before the analysis window. RSI and other indicators need historical data to stabilize.

2. **Match position sizing** — Use the live bot's actual `trade_usdt` in the backtest. You can calculate it from `state.json`: `trade_usdt = balance * 0.8 / 8`.

3. **Exclude carryover positions** — Only compare trades that entered during the analysis window. Positions from before the window have different contexts.

4. **Timezone consistency** — Entry times in my system are already in KST. Don't double-convert by adding +9 hours again.

5. **SL grace = 0** — My live bot uses STOP_LIMIT with no grace period. The backtest must match.

## How often should you run comparisons?

I run comparisons **after every parameter change** and **at least weekly** during normal operation.

The moment live results start diverging from backtest predictions without explanation, something is broken. Maybe a code change introduced a bug. Maybe the exchange API changed behavior. Maybe a new coin behaves differently than expected.

**The comparison tool is your early warning system.** If you don't have one, build one before you optimize anything else.

## Can your backtest ever perfectly match live trading?

No. Some differences are unavoidable:

- **SL fill timing** — STOP_LIMIT fills at the exact trigger on the exchange, but the backtest simulates this with 1-minute candle data
- **Order execution latency** — Real orders take 100-500ms to fill
- **Slippage on market orders** — Backtests use the candle close price; live fills vary slightly

The goal isn't 100% match. It's **understanding every discrepancy.** If you can explain why each trade differs, your backtest is trustworthy. If you can't, it isn't.

---

*An honest backtest that matches reality at 83% is worth infinitely more than a fantasy backtest showing +2000U.*

**Related:**
- [Backtest vs Reality: Where Dreams Die](/posts/backtest-vs-reality-where-dreams-die/) — The full gap analysis
- [The Timezone Bug](/posts/the-timezone-bug-that-cost-me-9-hours-of-trades/) — The 9-hour ghost
- [Dry Run: The Step Everyone Skips](/posts/dry-run-the-step-everyone-skips/) — Testing before going live
