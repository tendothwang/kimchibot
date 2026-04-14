---
title: "I Optimized My Bot Until It Was Perfect. Then Reality Hit"
date: 2026-03-21
draft: false
tags: ["optimization", "grid-search", "overfitting", "trading-bot", "backtesting"]
categories: ["Lessons"]
summary: "Grid search found parameters that turned -82U into +343U. Here's how I made sure it wasn't just overfitting."
---

## The Temptation

You have a strategy with 10 parameters. Each parameter has 5 possible values. That's 5^10 = ~10 million combinations.

Somewhere in those 10 million combinations is one that shows +5000% returns on your backtest data. It's also completely meaningless.

**The more parameters you optimize, the easier it is to overfit.**

## My Grid Search Process

### Step 1: Limit the Parameters

Don't optimize everything at once. Pick 2-3 parameters that matter most. For my trend-following bot:

- Stop Loss %: [1.0, 1.5, 2.0, 2.5, 3.0]
- Trail Activation %: [1.0, 1.5, 2.0, 2.5]
- Trail Stop %: [0.3, 0.5, 0.7]

That's 60 combinations. Manageable and interpretable.

### Step 2: Use Enough Data

- **Minimum:** 3 months of data
- **Better:** 6-12 months
- **Best:** Multiple years across different market conditions

Short backtest periods produce parameters that are tuned to that specific market phase. They'll break when the market changes.

### Step 3: Look for Plateaus, Not Peaks

The best parameter isn't the one with the highest PnL. It's the one surrounded by similarly good results.

```
SL 1.0% → +100U
SL 1.5% → +250U
SL 2.0% → +280U  ← Peak
SL 2.5% → +260U
SL 3.0% → +200U
```

SL 2.0% is on a **plateau**. Nearby values also work well. This parameter is robust.

```
SL 1.0% → -50U
SL 1.5% → +500U  ← Peak
SL 2.0% → -30U
SL 2.5% → -80U
SL 3.0% → -100U
```

SL 1.5% is a **spike**. Tiny changes destroy performance. This is overfitting.

**Choose parameters on plateaus, not spikes.**

### Step 4: Validate Out-of-Sample

Take your optimized parameters and test them on data you didn't optimize on. If they still work, you might have something real.

My v2.9 optimization result:

| Dataset | PnL | Trades | Win Rate |
|---------|-----|--------|----------|
| Training (3 months) | +343U | 1,800 | 72.3% |
| Validation (1 month) | +245U | 552 | 76.8% |

Validation performance was proportionally similar. Good sign.

## What I Actually Optimized

### Round 1: SL Level (Most Impact)

Old: SL 1.2%. Result: frequent stop outs, death by a thousand cuts.

Grid search showed SL 3.0% minimized SL triggers to just 2.6% of trades (250 out of 9,747). 

I chose **2.0%** — not the mathematical optimum, but a good balance between protection and breathing room.

### Round 2: Trailing Stop

Old: TA 1.5%, TS 0.5%. 

After grid search: **TA 2.0%, TS 0.5%**. The activation threshold needed to match the wider SL — otherwise trades get stopped before having a chance to activate trailing.

### Round 3: Volume Ratio Filter

Old: Long VR 0.9, Short VR 0.8. Too permissive — letting in low-volume noise.

After search: **Long VR 1.8, Short VR 1.5**. This cut total trades by ~60% but improved win rate from ~50% to ~57%.

**Fewer trades, better trades.**

## The Separation Principle

One crucial decision: **separate long and short parameters.**

Crypto markets are asymmetric:
- Rallies are gradual (stairs up)
- Crashes are sudden (elevator down)

Using the same SL for longs and shorts means one side is always wrong. Different parameters for each direction improved overall performance by ~15%.

## Mistakes I Made

### 1. Optimizing Too Many Parameters Together

My first grid search had 8 parameters × 5 values = 390,625 combinations. The "best" result was a fluke. When I tested it out-of-sample, it was negative.

**Rule: maximum 3 parameters at a time.**

### 2. Optimizing on Too Short a Period

I once optimized on 2 weeks of data. Found amazing parameters. They worked perfectly — for those 2 weeks. The next 2 weeks wiped out all gains.

**Rule: minimum 3 months, preferably 6+.**

### 3. Chasing the Highest PnL

The temptation is to always pick the parameter set with the highest backtest PnL. But if it's +500U with 90% of that coming from 3 trades, it's not robust.

**Rule: also check trimmed PnL (remove top/bottom 10% of trades).**

## The Meta-Rule

> If changing a parameter by 10% destroys your strategy, the strategy doesn't have edge — the parameter does.

Good strategies work across a range of reasonable parameters. Great strategies are almost insensitive to parameters. If your bot only works with SL exactly at 1.73%, you don't have a strategy. You have a coincidence.

---

*The goal of optimization isn't to find the perfect parameters. It's to confirm that your strategy works across imperfect ones.*
