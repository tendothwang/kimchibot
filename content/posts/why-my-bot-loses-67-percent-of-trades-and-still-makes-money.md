---
title: "Why My Bot Loses 67% of Trades and Still Makes Money"
date: 2026-04-12T17:00:00
draft: false
tags: ["risk-reward", "win-rate", "fvg", "trading-psychology", "trading-bot", "crypto"]
categories: ["Strategy"]
summary: "Two out of three trades are losses. My equity curve still goes up. Here's why win rate is the most overrated metric in trading."
---

## How can a bot that loses most trades be profitable?

When I tell people my FVG bot has a win rate around 33%, they assume it's broken. Losing two out of every three trades sounds terrible. It sounds like a strategy that needs fixing.

But the bot is profitable. Not because it wins often — because it wins **big**.

The secret is the risk-reward ratio. Every trade is structured as 1:3 — if the stop loss is 1 unit of risk, the take profit is 3 units of reward. When it loses, it loses small. When it wins, it wins 3x more.

## What does the math actually look like?

Take 100 trades with a 33% win rate and 1:3 risk-reward:

```
33 wins  × 3R = 99R gained
67 losses × 1R = 67R lost
Net: +32R profit
```

Even losing 67 out of 100 trades, the bot nets +32 units of risk. That's a **32% return on risk** over 100 trades.

Now compare that to a "high win rate" strategy at 70% win rate but 1:1 risk-reward:

```
70 wins  × 1R = 70R gained
30 losses × 1R = 30R lost
Net: +40R profit
```

The high win rate strategy wins more often and also makes more in this example. But here's the problem — maintaining 70% win rate in live trading is extremely hard. Slippage, spread, and execution delays eat into thin margins. A 70% backtest win rate often becomes 55% live.

At 55% with 1:1:
```
55 wins  × 1R = 55R
45 losses × 1R = 45R
Net: +10R
```

Meanwhile, my 33% win rate bot degrading to 28% live:
```
28 wins  × 3R = 84R
72 losses × 1R = 72R
Net: +12R
```

**The low win rate strategy is more robust to degradation.** It has more room to get worse and still make money. The breakeven win rate for 1:3 RR is just 25%.

## Why is low win rate psychologically brutal?

Here's what a typical week looks like:

- Monday: Loss, Loss, Loss, **Win**, Loss
- Tuesday: Loss, Loss, **Win**, Loss, Loss, Loss
- Wednesday: Loss, Loss, Loss, Loss, **Win**
- Thursday: Loss, Loss, Loss, Loss, Loss, Loss
- Friday: **Win**, Loss, Loss, **Win**, Loss

Thursday was six consecutive losses. Your instinct screams: *the strategy is broken. Turn it off. Something changed in the market.*

But Thursday was statistically normal. With a 33% win rate, a streak of six losses has a probability of:

```
0.67^6 = 9%
```

A 9% chance means it happens roughly once every 11 trading sequences. If your bot takes multiple trades a day, you'll see a 6-loss streak **every week or two**. It's not a bug — it's the expected behavior.

## What's worse than a losing streak?

Intervening during a losing streak. I've done this. The bot loses 5 in a row, I panic and turn it off. The next two trades — both wins — happen without me. Those wins would have been +6R each, enough to cover all 5 losses and then some.

The worst outcome isn't losing trades. It's **missing the winning trades** because you couldn't stomach the losing ones.

This is why the bot runs autonomously. It doesn't have emotions. It doesn't care about streaks. It takes every valid signal regardless of what happened on the last 10 trades.

## How do I know the win rate is real and not just bad luck?

My out-of-sample test covered 4 quarters of data the bot had never seen:

| Quarter | Win Rate | Result |
|---------|----------|--------|
| 2025 Q2 | 38% | Profitable |
| 2025 Q3 | 35% | Profitable |
| 2025 Q4 | 40% | Profitable |
| 2026 Q1 | 32% | Small loss |

The win rate stays consistently in the 32-40% range. It's not random — the strategy has a genuine statistical edge, even though it loses more often than it wins.

Three profitable quarters, one losing quarter. That's realistic for a mean-reversion strategy in crypto. If all four were profitable with smooth equity curves, I'd be worried about overfitting.

## Why does the FVG strategy naturally have low win rate?

Fair Value Gap trading is mean reversion: you bet that price will return to fill a gap. But gaps exist because of strong directional moves. Sometimes that direction continues, and the gap doesn't fill — your stop loss gets hit.

The design of the strategy creates the low win rate:

1. **Wide take profit (3x the risk)** — Price needs to travel far to hit TP. Many trades reverse partway and get stopped out.
2. **Tight stop loss (at FVG boundary)** — Small room for the trade to breathe. Any wick through the gap = loss.
3. **Mean reversion in a trending market** — When the broader trend is strong, FVGs form but don't fill.

Each of these factors reduces the win rate. But together, they also ensure that when a trade *does* work, it works big. The few trades that fill the gap and run to 3R make up for all the small stops.

## What happens if I try to improve the win rate?

I tested this. Tightening the take profit from 3R to 1.5R increased win rate dramatically — but total profit dropped. Here's why:

At 1.5R, more trades hit the target. Win rate improves. But each win is only half as large. You need a much higher win rate to compensate, and the breakeven shifts from 25% to 40%. Any market regime that drops win rate below 40% turns the strategy negative.

I also tested partial take profit — closing 30% of the position at +3% and letting the rest run. The 1-month backtest showed this reduced total profit because the partial close captured small gains but reduced the size of the big winners that carry the strategy.

**The 1:3 ratio isn't arbitrary. It's the minimum risk-reward where the strategy has enough room to absorb bad periods and still stay positive.**

## What's the real lesson about win rate?

Win rate is a vanity metric. It makes you *feel* good or bad, but it tells you almost nothing about whether a strategy is profitable.

The only number that matters is **expectancy**:

```
Expectancy = (Win Rate × Average Win) - (Loss Rate × Average Loss)
```

A 33% win rate with 3:1 winners:
```
(0.33 × 3) - (0.67 × 1) = 0.99 - 0.67 = +0.32R per trade
```

A 60% win rate with 0.8:1 winners:
```
(0.60 × 0.8) - (0.40 × 1) = 0.48 - 0.40 = +0.08R per trade
```

The "ugly" 33% strategy has 4x the expectancy of the "nice" 60% strategy.

---

*Everyone wants a high win rate. The market rewards high expectancy. They're not the same thing.*

**Related:**
- [Risk-Reward Ratio: The Only Number That Matters](/posts/risk-reward-ratio-the-only-number-that-matters/) — Deep dive into RR math
- [Fair Value Gaps: The Strategy That Changed Everything](/posts/fair-value-gaps-the-strategy-that-changed-everything/) — The FVG strategy explained
- [The Backtest Looked Amazing. It Was Lying.](/posts/the-backtest-looked-amazing-it-was-lying/) — Why backtest win rates mislead
- [One Year of Out-of-Sample Testing](/posts/one-year-of-out-of-sample-testing-did-the-fvg-bot-survive/) — OOS validation results
