---
title: "Why I Run Two Bots, Not One"
date: 2026-03-25
draft: false
tags: ["portfolio", "diversification", "trading-bot", "crypto", "strategy"]
categories: ["Strategy"]
summary: "One bot follows trends. The other trades mean reversion. Together, they cover each other's weaknesses."
---

## The Problem With One Strategy

Every trading strategy has a weakness:

- **Trend following** dies in sideways markets. No trend = no signal = no trades. Or worse, false breakouts that trigger entries and immediately reverse.

- **Mean reversion (FVG)** struggles when trends are strong. Price creates a gap and just keeps going — never coming back to fill it.

No single strategy works in all market conditions. Period.

## The Solution: Strategy Diversification

I run two bots simultaneously:

### Bot 1: Trend Following v4.0
- **When it thrives:** Strong directional moves, high volatility
- **When it struggles:** Choppy, sideways markets
- **Win rate:** ~57%
- **Risk-reward:** ~1:1.2

### Bot 2: FVG (Fair Value Gap)
- **When it thrives:** Any market with clear price imbalances
- **When it struggles:** Strong trends that don't retrace
- **Win rate:** ~33%
- **Risk-reward:** 1:3

## How They Complement Each Other

Think of it like a seesaw:

```
Strong Trend:    TF Bot ████████  |  FVG Bot ██
Mild Trend:      TF Bot █████     |  FVG Bot █████
Sideways:        TF Bot ██        |  FVG Bot ████████
```

When one bot is having a bad day, the other is often having a good day.

### Real Example

March 2026, Week 3:
- Monday-Tuesday: Strong uptrend. TF bot caught multiple entries. FVG bot got stopped out on gap trades that never filled.
- Wednesday-Thursday: Market consolidated. TF bot sat idle (CHOP filter blocked entries). FVG bot caught mean-reversion bounces in the range.
- Friday: Sharp selloff. TF bot caught the short. FVG bot caught the bounce at the FVG level.

**Combined PnL was smoother than either bot alone.**

## Why Not Three Bots? Or Five?

I killed 4 other bots for good reasons:

| Bot | Why It Died |
|-----|------------|
| Grid Bot | Structural failure in trending markets |
| RSI Scalping | Outperformed by trend following |
| Market Maker | Requires $100k+ capital |
| Lead-Lag | Opportunity window already closed |
| Momentum | Overfitting — beautiful backtest, terrible live |

More bots ≠ better diversification. Each bot needs:
- A genuine edge (proven out-of-sample)
- Different market conditions where it works
- Enough capital to size positions properly

Two bots with real edges beat five bots where three are mediocre.

## Capital Allocation

My current split:

| Bot | Capital | Leverage | Coins | Per-Trade Size |
|-----|---------|----------|-------|---------------|
| Trend Following | 80% of balance | 3x | 8 coins | Balance × 0.8 ÷ 8 |
| FVG | Fixed per trade | 3x | 10 coins | $200 |

The trend-following bot uses percentage-based sizing (compound growth). The FVG bot uses fixed sizing (newer, still building confidence).

## The Key Insight

Diversification in trading isn't about trading more coins or more timeframes. It's about having strategies that **disagree with each other**.

If both your strategies go long in the same conditions and short in the same conditions, you don't have diversification. You have two copies of the same bet.

A trend-follower and a mean-reverter naturally disagree. When one says "price is going up, get in," the other says "price went up too fast, it's coming back." This tension is the whole point.

## When To Add a Third Bot

I'll add another strategy when I find one that:
1. Has a different market regime preference
2. Passes out-of-sample testing
3. Has backtest-live parity
4. Doesn't correlate with my existing bots

Until then, two is enough. **Quality over quantity.**

---

*The goal isn't to make money every day. It's to make money every month. Two uncorrelated bots make that much more likely.*
