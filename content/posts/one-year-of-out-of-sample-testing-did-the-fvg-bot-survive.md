---
title: "One Year of Out-of-Sample Testing: Did the FVG Bot Survive?"
date: 2026-04-10T18:00:00
draft: false
tags: ["fvg", "backtesting", "out-of-sample", "trading-bot", "crypto", "validation"]
categories: ["Strategy"]
summary: "I tested my Fair Value Gap bot on 4 quarters of data it had never seen. 3 out of 4 were profitable. Here are the exact numbers."
---

## Why is out-of-sample testing the most important step?

Every strategy looks good on the data it was trained on. That's the whole point of optimization — you find parameters that work on historical data.

The question is: **does it work on data it has never seen?**

My momentum bot answered "no." It showed incredible backtest returns, then lost money immediately in live trading. Classic overfitting.

My FVG bot needed to pass this test before I'd trust it with real money.

## How did I structure the out-of-sample test?

I tested across **4 quarters, 10 coins**, using the exact parameters from the live bot:

- FVG gap size: 1.5% - 4.0%
- C2 candle body: ≥ 2.0%
- Risk-reward: 1:3 (fixed TP at 3x the risk)
- SL at FVG boundary + 0.2% buffer
- MA20 trend filter
- SL ratio < 65% coin filter
- Fee rate: 0.07% round trip (maker 0.02% + taker 0.05%)

**None of these parameters were optimized on the test data.** They were set during development on a separate training period.

## What were the results?

| Quarter | Trades | Win Rate | PnL |
|---------|--------|----------|-----|
| 2025 Q2 | ~380 | 38% | **+271U** |
| 2025 Q3 | ~350 | 35% | **+38U** |
| 2025 Q4 | ~400 | 40% | **+273U** |
| 2026 Q1 | ~300 | 32% | **-36U** |

**Total: 1,506 trades, ~40% win rate, +548U over 12 months.**

Three profitable quarters, one losing quarter.

## What does the losing quarter tell us?

Q1 2026 was a sideways market. Price oscillated without clear direction, which means:

- FVGs formed but didn't fill cleanly — price entered the gap zone and kept going
- The trend filter (MA20) gave mixed signals — constantly flipping between bullish and bearish
- More trades hit the stop loss before reaching the 3:1 take profit

This is a **known weakness** of the FVG strategy. Mean reversion relies on price returning to fill gaps. In strong-trend markets, gaps get filled. In choppy sideways markets, they often don't.

**One losing quarter out of four is realistic.** If all four were profitable with smooth equity curves, I'd be suspicious of overfitting.

## How does a 33% win rate make money?

This is the question everyone asks. The answer is risk-reward:

- **Average win:** 3x the risk (by design — fixed 1:3 RR)
- **Average loss:** 1x the risk

Over 100 trades with 33% win rate:
```
33 wins × 3R = 99R
67 losses × 1R = 67R
Net: +32R
```

Even losing two-thirds of all trades, the bot is profitable because winners are 3x larger than losers.

This is psychologically brutal. You watch the bot lose 5, 6, 7 trades in a row. Your instinct screams "turn it off." But the math says hold.

## What changed after the OOS test?

The OOS test validated two things:

1. **The edge is real.** +548U over 1 year on unseen data isn't luck. It's a genuine statistical edge in how markets fill Fair Value Gaps.

2. **The parameters are robust.** The same parameters that worked on training data also worked on 4 separate quarters. No spike optimization — a genuine plateau.

After this validation, I deployed the FVG bot live with real money. The live-backtest entry price match rate: **100%**. Minor differences only in SL timing.

## How does the FVG bot compare to the trend following bot?

I run both simultaneously. They complement each other:

| Aspect | Trend Following | FVG |
|--------|----------------|-----|
| Market type | Strong trends | Any (with trend filter) |
| Entry style | Momentum breakout | Mean reversion to gap |
| Win rate | ~57% | ~33% |
| Risk-reward | ~1:1.2 | 1:3 |
| Weakness | Sideways/choppy markets | Strong trends without retracement |

When one bot struggles, the other often thrives. This isn't accidental — I specifically chose a mean-reversion strategy to complement my trend-following strategy.

## What filters improved the OOS results?

After the initial OOS validation, I tested additional filters using post-hoc analysis (not re-optimization):

| Filter | Effect |
|--------|--------|
| Gap 1.5-4.0% (was 0.5-2.0%) | Eliminated small noisy gaps, reduced trade count 62%, improved WR from 26% to 36% |
| Body ≥ 2.0% (was 0.7%) | Filtered out wicks-only FVGs, improved signal quality |
| C2 body overlap check | Ensured gap exists within the candle body, not just wicks |
| SL ratio < 65% per coin | Excluded coins that historically don't respect FVGs |

The gap/body filter change was dramatic: 7-day performance went from -15U (666 trades, 26% WR) to +660U (254 trades, 36% WR). Fewer trades, much better trades.

The 1-year OOS with these filters: **1,506 trades, 40% WR, +1,608U** (including fees).

## What's the honest takeaway?

The FVG bot works. The OOS test proves it has a real edge, not just curve-fitted parameters.

But it's not a money printer:
- One losing quarter out of four
- 67% of trades are losses
- Requires discipline to let winners run to 3R
- Performance varies significantly by market regime

**The value of OOS testing isn't proving your strategy is great. It's proving it isn't garbage.** If it survives a year of unseen data, you have something worth trading. If it doesn't, you saved yourself real money by finding out with fake money.

---

*The backtest tells you what could happen. The out-of-sample test tells you what probably will happen. Only live trading tells you what actually happened.*

**Related:**
- [Fair Value Gaps: The Strategy That Changed Everything](/posts/fair-value-gaps-the-strategy-that-changed-everything/) — The FVG strategy explained
- [How to Avoid Overfitting](/posts/how-to-avoid-overfitting-in-trading-bots/) — The checklist I use
- [The Backtest Looked Amazing. It Was Lying.](/posts/the-backtest-looked-amazing-it-was-lying/) — What happens without OOS testing
- [Why I Run Two Bots, Not One](/posts/why-i-run-two-bots-not-one/) — The portfolio approach
