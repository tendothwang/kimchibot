---
title: "Backtest vs Reality: Where Dreams Go to Die"
date: 2026-04-04
draft: false
tags: ["backtesting", "live-trading", "slippage", "trading-bot", "crypto"]
categories: ["Lessons"]
summary: "My bot showed +500U in backtests. Live trading showed +200U. Here's every gap I found and how I closed them."
---

## The Gap

You build a bot. You backtest it. It shows beautiful numbers. You go live.

Then reality hits.

Your backtest says +500U. Your live bot shows +200U. Where did the other 300 go?

I spent weeks hunting down every source of discrepancy between my backtest and live bot. Here's the complete list of everything that was wrong.

## 1. Slippage: The Silent Killer

**Backtest assumption:** Orders fill at the exact price you want.

**Reality:** They don't.

When you place a market order, the price moves between your decision and execution. In crypto, this is typically 0.02-0.1%, but during volatile moments it can be much worse.

**How I fixed it:** I switched from market orders to limit orders for entries. The bot places a limit order, waits 5 seconds, and if it's not filled, falls back to a market order. This alone saved ~0.05% per trade.

## 2. Trailing Stop: Tick vs Candle Close

This one cost me weeks to figure out.

**The bug:** My live bot checked trailing stops every 1 second using WebSocket ticks. My backtest checked them on 5-minute candle closes.

**The effect:** The live bot would trigger trailing stops on momentary price dips that recovered within the same candle. The backtest never saw these dips because it only looked at the close price.

**Example:** Price drops 0.8% for 3 seconds, then recovers. Live bot: stopped out. Backtest: still in the trade, goes on to make +15U profit.

**How I fixed it:** Changed the live bot to only check trailing stops at 5-minute candle closes, matching the backtest exactly. This was the single biggest improvement in live-backtest consistency.

## 3. Timezone Bugs

**The bug:** My backtest used UTC. My live bot used local time (KST, UTC+9). I was comparing apples to oranges for the first two weeks.

**The effect:** The first 9 hours of every backtest period had zero entries because the time window was offset.

**How I fixed it:** Standardized everything to KST. Added `KST_OFFSET = +9h` to all timestamp labels. Now both systems speak the same language.

## 4. Candle Resampling vs Native Data

**The bug:** My backtest built 30-minute and 1-hour candles by resampling 5-minute data. My live bot fetched native 30m/1h candles from Binance.

**The effect:** Resampled RSI values were slightly different from native candle RSI values. This caused different entry/exit signals in edge cases.

**How I fixed it:** Switched the backtest to fetch native 30m/1h/4h candles directly from the exchange. RSI values now match exactly.

## 5. The Best Price Problem

**The bug:** My live bot tracked "best price" (highest for longs, lowest for shorts) using WebSocket extreme values. My backtest used 1-minute candle high/low.

**The effect:** WebSocket catches price spikes that don't show up in 1-minute candles. This meant different trailing stop activation points.

**One trade example:** Live bot best_price = $0.1597 (WS spike). Backtest best_price = $0.1593 (1m high). Trail stop triggered at different times. PnL difference: 23U.

**How I fixed it:** Removed WebSocket entirely. Both live bot and backtest now use 1-minute candle extremes for best_price tracking.

## The Result

After fixing all these issues, I ran a comparison:

**Before fixes:** ~50% of trades matched between backtest and live.

**After fixes:** 15 out of 18 trades matched (83%). The remaining 3 had minor SL/trailing timing differences of 0.06-0.4U.

## The Verification Process

Now I run this comparison regularly:

```bash
python compare_live_bt.py "2026-03-10" "2026-03-12"
```

This script:
- Pulls live trade logs
- Runs the same period through the backtest
- Compares entry prices, exit reasons, and PnL
- Flags any discrepancies

**If your backtest doesn't match your live bot, your backtest is fiction.** Fix the gaps before you trust any optimization results.

## Key Takeaways

1. **Build a comparison tool early.** Don't wait until you've lost money to discover discrepancies.

2. **Match everything exactly.** Same data source, same timeframe, same price type (close vs tick), same timezone.

3. **The live bot is always right.** When there's a discrepancy, the backtest is wrong, not the live bot. Reality doesn't have bugs — your simulation does.

4. **0.1% matters.** In trading, small systematic errors compound into large losses over thousands of trades.

---

*An honest backtest that shows +200U is worth more than a fantasy backtest showing +2000U.*
