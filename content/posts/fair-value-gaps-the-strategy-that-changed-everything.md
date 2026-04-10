---
title: "Fair Value Gaps: The Strategy That Changed Everything"
date: 2026-03-30
draft: false
tags: ["fvg", "fair-value-gap", "trading-bot", "crypto", "strategy"]
categories: ["Strategy"]
summary: "After trend-following, I built a completely different bot based on Fair Value Gaps. It passed a full year of out-of-sample testing."
---

## What is a Fair Value Gap in trading?

A Fair Value Gap (FVG) is a price imbalance visible on the chart. It happens when a candle moves so aggressively that it leaves a "gap" between the candle before and after it.

Think of it like a rubber band being stretched. The price moved too fast, and it wants to come back to fill that gap.

### The Three-Candle Pattern

```
Bullish FVG:
  C1: Normal candle
  C2: BIG bullish candle (the gap creator)
  C3: Normal candle — its LOW is above C1's HIGH

  The gap = space between C1's high and C3's low
  
Bearish FVG:
  C1: Normal candle  
  C2: BIG bearish candle (the gap creator)
  C3: Normal candle — its HIGH is below C1's LOW

  The gap = space between C1's low and C3's high
```

When price returns to this gap zone, it often bounces. That's the trade.

## How do you build a trading bot based on Fair Value Gaps?

1. **Detect FVG** on 5-minute candles
2. **Place limit order** at the FVG edge (entry price)
3. **Stop loss** at the opposite edge of the FVG
4. **Take profit** at 3x the risk (RR 3.0)

Simple. Clean. No indicators needed — just price action.

## What filters improve FVG trading bot performance?

Not every FVG is worth trading. After extensive testing, these filters survived:

### Gap Size: 1.5% - 4.0%
- Too small (< 1.5%): Noise. Fees eat the profit.
- Too large (> 4.0%): Usually panic moves that don't revert.

### Candle Body ≥ 2.0%
The C2 candle (gap creator) needs a substantial body. Small-bodied candles with long wicks create fake FVGs.

### C2 Body Overlap
The gap must overlap with C2's body (open-to-close range). Gaps that only exist in the wick zone are unreliable.

### MA20 Trend Filter
- Price above 1h MA20 → Only take longs
- Price below 1h MA20 → Only take shorts

Don't fight the trend, even with mean-reversion setups.

### SL Ratio < 65%
If more than 65% of historical trades on a coin hit stop loss, skip that coin. Some coins just don't respect FVGs.

## Which FVG filters look good but actually don't work?

This is equally important — what looked promising but failed:

| Filter | Result | Verdict |
|--------|--------|---------|
| Bollinger Band width < 2% | No edge over 2 weeks | Rejected |
| Entry delay (wait 1-3 candles) | PnL decreased with each candle of delay | Rejected |
| Large C2 body cap (> 3%) | Filtered out profitable trades too | Rejected |
| CE (50%) entry | Worse than edge entry at all RR levels | Rejected |

**Every one of these "made sense" logically.** Bollinger Bands for choppy markets, delayed entry for confirmation — they all sound reasonable.

Data said otherwise. This is why you test everything.

## Does the FVG strategy survive out-of-sample testing?

Here's where most strategies die. I tested across **4 quarters, 10 coins**:

| Quarter | Trades | Win Rate | PnL |
|---------|--------|----------|-----|
| 2025 Q2 | ~380 | 38% | +271U |
| 2025 Q3 | ~350 | 35% | +38U |
| 2025 Q4 | ~400 | 40% | +273U |
| 2026 Q1a | ~300 | 32% | -36U |

3 out of 4 quarters profitable. The losing quarter was a sideways market — a known weakness.

**Total: +548U over 1 year on data the strategy never trained on.**

This isn't overfitting. This is edge.

## How does the FVG bot perform in live trading?

After the out-of-sample validation, I deployed it live:

- 24h PnL-based coin scanning every 6 hours
- 10 coins running simultaneously  
- $200 per trade, 3x leverage
- Real slippage, real fees, real market conditions

The live-backtest match rate after fixing all the bugs: **100% entry price match**, minor SL timing differences only.

## Should you use FVG or trend following for crypto trading bots?

I now run both bots simultaneously. They complement each other:

| Aspect | Trend Following | FVG |
|--------|----------------|-----|
| Market type | Trending | Any (with trend filter) |
| Entry style | Breakout | Mean reversion |
| Hold time | ~2.6 hours | ~1-4 hours |
| Win rate | ~57% | ~33% |
| Risk-reward | ~1:1.2 | 1:3 |

**Different strategies, different edges.** When one struggles, the other often thrives.

---

*The best portfolio isn't one strategy optimized to death — it's multiple strategies that disagree with each other.*
