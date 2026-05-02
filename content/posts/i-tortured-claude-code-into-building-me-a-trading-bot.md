---
title: "I Built 6 Trading Bots With Claude Code — Here's What Happened"
date: 2026-04-07
draft: false
tags: ["claude-ai-trading-bot", "claude-trading-bot", "ai-trading-bot", "claude-code", "crypto-trading-bot", "python", "introduction"]
categories: ["Story"]
summary: "A developer from Korea built 6 crypto trading bots using Claude Code. 4 failed. Here's the honest story of building a Claude AI trading bot — and a guide so you can build one too."
---

## Who Am I?

I'm a developer from South Korea who got curious about whether AI coding tools could help me build a working crypto trading bot.

I can code. But shipping a trading bot is a completely different beast — it's not about clean code, it's about markets, statistics, and not fooling yourself with pretty backtests.

My weapon of choice: [Claude Code](https://claude.ai/claude-code). An AI that doesn't complain when you ask it to rewrite the same function 47 times.

**The goal of this blog:** Document everything so honestly that even a complete beginner could follow along and build their own bot. Every strategy, every failure, every line of reasoning — explained.

## The Idea Was Simple

Build a crypto trading bot. Let it trade on Binance Futures. Sit back. Profit.

Spoiler: the coding was the easy part. Everything else was hard.

## 6 Bots Built. 4 Killed.

Over the past few months, I built **6 different trading bots** with Claude Code. Here's the scoreboard:

### 1. Grid Bot - DEAD
The classic "buy low, sell high at preset levels" strategy. Sounds great in theory.

**What killed it:** Slippage ate the profits alive, and in a trending market? It just kept buying into the abyss. This wasn't a bug — it was a structural flaw. Grid bots are a lie in trending markets.

### 2. RSI Scalping Bot - SHELVED
A quick-trade bot based on RSI signals. It worked... okay.

**Why I shelved it:** The trend-following bot just performed better. Why keep the bronze medalist?

### 3. Trend Following Bot v4.0 - ALIVE AND RUNNING
This is the survivor. The one that made it through backtesting, dry runs, and is now trading real money on Binance Futures.

- 5-minute candle body + Volume Ratio signals
- CHOP filter to avoid sideways markets
- Trailing stop on 5m candle close (not tick-by-tick — learned that the hard way)
- 3x leverage, compounding 80% of balance

More on this beast in future posts.

### 4. Market Maker Bot - DEAD (NOT ENOUGH CAPITAL)
You need $100k+ to market-make effectively. I do not have $100k+. Next.

### 5. Lead-Lag Bot - DEAD
Tried to exploit price differences between correlated pairs. By the time I built it, the opportunity had evaporated. Crypto moves fast.

### 6. Momentum Bot - DEAD
Looked amazing in backtests. Suspiciously amazing.

**What killed it:** Overfitting. The backtest was basically memorizing the past, not predicting the future. This taught me one of the most important lessons in quant trading.

## What I Learned (The Hard Way)

A few principles that are now tattooed on my brain:

1. **Win rate doesn't matter as much as risk-reward ratio.** A 35% win rate with 1:1.5 risk-reward beats a 60% win rate with 1:0.5.

2. **If your backtest looks too good, it's lying to you.** Always check for overfitting. Out-of-sample testing is not optional.

3. **The gap between backtest and live trading is where dreams go to die.** Slippage, latency, exchange quirks — they all add up.

4. **Claude Code is incredibly powerful, but it doesn't know your strategy is stupid.** It'll build exactly what you ask for, beautifully. Even if what you asked for is garbage.

## What's Coming Next

This blog is the real, unfiltered journal of building trading bots with AI. I'll cover:

- **Strategy breakdowns** — how each bot works, with code
- **Backtest vs reality** — the numbers, honestly
- **The debugging nightmares** — PID lockfiles, timezone bugs, exchange API quirks
- **Live performance reports** — wins, losses, everything

No "3-minute bot" clickbait. No fake screenshots. Just the messy, frustrating, occasionally profitable truth.

---

*If you've ever wondered whether AI can actually build you a working trading bot — stick around. The answer is yes, but with a lot of asterisks.*
