---
title: "Stop Trading Random Coins. Here's How My Bot Picks Winners"
date: 2026-04-01
draft: false
tags: ["coin-selection", "volatility", "backtesting", "trading-bot", "crypto"]
categories: ["Strategy"]
summary: "My bot doesn't trade the same coins forever. Every 3 hours, it picks the best ones automatically. Here's the algorithm."
---

## The Problem With Fixed Coin Lists

When I started, I hardcoded 5 coins: SOL, XRP, DOGE, AVAX, SUI.

Big names. High volume. Safe choices.

**Zero trades.**

Why? These large-cap coins barely move on the 5-minute timeframe. My entry condition requires a candle body ≥ 0.7%. Blue chips like SOL average 0.3% per candle. They're too stable for a momentum strategy.

Meanwhile, smaller altcoins like SIREN, LYN, and PIPPIN were printing money — 0.5-1.3% average candle bodies with 100%+ weekly ranges.

I was watching the wrong market.

## The Solution: Automatic Coin Rotation

Every 3 hours, my bot runs this process:

### Step 1: Volatility Filter

Fetch 7 days of 5-minute OHLCV data for all Binance Futures pairs. Keep only coins that meet:

- **Average candle body ≥ 0.4%** — Enough movement to trigger entries
- **24h price range ≥ 12%** — Coin is actually moving, not just twitching

This immediately eliminates ~80% of pairs. BTC, ETH, SOL — all gone. They're great for holding, terrible for scalping.

### Step 2: Exclude Problematic Pairs

Some pairs look good but will break your bot:

- **TradFi tokens** (TSLA, NVDA, GOOGL) — Require special agreement signing
- **Commodity tokens** (XAU, XAG) — Different trading rules
- **Index tokens** (BTCDOM, DEFI) — Low liquidity
- **Pre-market tokens** — Can halt unexpectedly

I auto-exclude anything where `underlyingType != 'COIN'`. This filters out ~24 problematic pairs.

### Step 3: Backtest Ranking

For each surviving coin, run a 6-hour backtest using the exact same strategy the live bot uses. Rank by PnL.

Take the **top 8**.

### Why 8 Coins?

I tested different TOP_N values in backtests:

- **3-5 coins:** Too concentrated. If one coin's scan picks a dud, your whole portfolio suffers.
- **8 coins:** Sweet spot — enough diversification to survive bad picks, few enough to concentrate on the best opportunities.
- **10-14 coins:** Diluted. Most days can't find that many coins meeting the volatility filter, so you end up trading mediocre performers.

8 worked best in my backtests across different market periods.

## The Results

The improvement from switching to automatic coin rotation was dramatic. With fixed large-cap coins, the bot barely traded — not enough volatility to trigger entries. With auto-rotation picking high-volatility coins, the bot consistently found opportunities.

**The right coins matter as much as the right strategy.** A perfect trend-following setup on a coin that doesn't trend is worthless.

## The Gotchas

### 1. Hot Coins Cool Off

A coin that's pumping for the last 6 hours might be exhausted for the next 6. The 6-hour backtest window is a compromise — long enough to identify real movers, short enough to stay current.

### 2. New Listings Are Dangerous

Freshly listed coins have extreme volatility but also extreme spreads and erratic behavior. The volatility filter catches them, but the backtest period is too short to be reliable.

### 3. Don't Fight the Filter

I've been tempted to manually add coins I "feel good about." Every time I did, they underperformed the auto-selected ones.

**Trust the data over your gut.**

## Key Takeaway

Your entry strategy is only as good as the coins you apply it to. A perfect trend-following setup on a coin that doesn't trend is worthless.

**Let the bot pick its own coins. It's better at it than you are.**

---

*The best trade is sometimes the one you didn't take — on a coin you shouldn't have been watching.*
