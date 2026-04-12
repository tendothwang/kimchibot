---
title: "The SL Ratio Filter: How I Ban Coins That Don't Respect FVGs"
date: 2026-04-12T18:00:00
draft: false
tags: ["fvg", "coin-selection", "stop-loss", "filter", "trading-bot", "crypto"]
categories: ["Strategy"]
summary: "Some coins hit your stop loss on every single FVG trade. I built a filter that bans them automatically. The results were dramatic."
---

## Why do some coins always hit the stop loss?

My FVG bot scans all Binance Futures pairs and picks the best ones based on recent backtest performance. But some coins kept appearing in the rotation and losing money every time.

The pattern was always the same:

1. A Fair Value Gap forms — big candle, clear gap
2. Price retraces into the gap zone
3. Instead of bouncing, price blows straight through the FVG and hits the stop loss
4. The bot enters again on the next FVG. Same result.

These coins don't respect Fair Value Gaps. The gap fills, but there's no reversal — price just keeps going. FVG as a concept doesn't work on every asset. Some coins are too chaotic, too thinly traded, or too momentum-driven for mean reversion to work.

## What is the SL ratio filter?

The SL ratio is simple: **what percentage of trades on this coin ended in a stop loss?**

```
SL Ratio = (number of SL trades) / (total trades) × 100
```

If a coin has an SL ratio above the threshold, the bot excludes it from trading. The coin scanner runs a backtest on each candidate coin, and any coin with too many stop losses gets banned.

## How did I find the right threshold?

I ran a rolling simulation across 8 days of data with different SL ratio cutoffs:

| Filter | Trades | PnL | Per Day |
|--------|--------|-----|---------|
| No filter | 437 | -156U | -19.5U |
| SL < 80% | 342 | +78U | +9.8U |
| SL < 70% | 287 | +125U | +15.6U |
| **SL < 60%** | **162** | **+287U** | **+36.0U** |
| SL < 50% | 109 | +164U | +20.6U |

Without any filter: **-156U loss** across 437 trades.

With SL < 60%: **+287U profit** from only 162 trades.

The filter didn't just reduce losses — it flipped the entire strategy from negative to positive. Most of the edge was coming from a subset of coins that actually respect FVGs. The rest were noise.

## Why not use 50%? It has fewer losses.

SL < 50% gives +164U — less than SL < 60%. Why?

Because 50% is too aggressive. It bans coins that have a normal FVG pattern (around 33-40% win rate means 60-67% SL rate). You want to keep coins that lose at a *normal* rate and ban only the ones that lose at an *abnormal* rate.

I chose **65%** as the final threshold — a compromise between the 60% optimum and the 70% safety margin. This avoids over-filtering while still catching the worst offenders.

## What does this look like in practice?

When the coin scanner runs every 6 hours, it:

1. Fetches the top 80 coins by 24h trading volume
2. Runs a 24-hour backtest on each coin
3. Checks the SL ratio of each coin
4. **Excludes any coin with SL ratio ≥ 65%**
5. Ranks the remaining coins by PnL
6. Selects the top 10

A coin that passed the volume filter and even had profitable individual trades can still get banned if its SL ratio is too high. The filter protects against coins that look good on paper but bleed in practice.

## What kind of coins get banned?

The coins that consistently fail the SL filter share common traits:

- **Low liquidity mid-caps** — wide spreads mean price can gap through your SL
- **Meme coins in sideways phases** — random walks that create false FVGs
- **Coins in consolidation** — tight ranges where FVGs form but don't mean anything
- **Recently listed coins** — not enough history for FVGs to be statistically meaningful

## Why is this filter more important than parameter tuning?

I spent weeks optimizing FVG parameters — gap size, candle body percentage, risk-reward ratio. Those changes improved performance by maybe 10-20%.

The SL ratio filter improved performance by **flipping the strategy from -156U to +287U in the same period**. That's not an incremental improvement — it's the difference between a losing strategy and a winning one.

The lesson: **which coins you trade matters more than how you trade them.** A perfect strategy on the wrong coin will lose money. A decent strategy on the right coin will make money.

## Can the SL ratio change over time?

Yes. A coin that respects FVGs this week might not next week. Market regime changes, liquidity shifts, and volatility cycles all affect whether FVGs work on a particular asset.

That's why the filter runs every scan cycle (every 6 hours). A coin that was banned yesterday can be allowed today if its recent SL ratio improved. And a coin that was profitable last week can get banned today if it started hitting stops.

The filter is dynamic, not a static blacklist.

---

*Don't ask "which coins should I trade?" Ask "which coins should I definitely NOT trade?" The answer saves more money.*

**Related:**
- [The Coin Scanner: How My Bot Picks 8 Coins Every 3 Hours](/posts/the-coin-scanner-how-my-bot-picks-8-coins-every-3-hours/) — The full scanning algorithm
- [Fair Value Gaps: The Strategy That Changed Everything](/posts/fair-value-gaps-the-strategy-that-changed-everything/) — The FVG strategy explained
- [One Year of Out-of-Sample Testing](/posts/one-year-of-out-of-sample-testing-did-the-fvg-bot-survive/) — Long-term validation results
