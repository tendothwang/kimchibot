---
title: "The Coin Scanner: How My Bot Picks 8 Coins Every 3 Hours"
date: 2026-04-10T16:00:00
draft: false
tags: ["coin-selection", "scanner", "volatility", "trading-bot", "crypto", "binance"]
categories: ["Strategy"]
summary: "My bot doesn't trade fixed coins. Every 3 hours it scans all Binance Futures pairs, filters by volatility, backtests each one, and picks the top 8. Here's the full algorithm."
---

## Why does automatic coin selection matter for trading bots?

I started with 5 hardcoded large-cap coins: SOL, XRP, DOGE, AVAX, SUI. The bot barely traded — these coins don't move enough on the 5-minute timeframe.

My entry requires a candle body of at least 0.7%. Large-cap coins average 0.3% per 5-minute candle. They're too stable for momentum strategies.

The fix wasn't to lower the threshold (that would let in noise). It was to **find the coins that actually move**.

## How does the coin scanner work?

Every 3 hours (at :02 past the hour), the bot runs this process:

### Step 1: Fetch all Binance Futures pairs

```python
exchange.load_markets()
all_pairs = [s for s in exchange.symbols 
             if s.endswith('/USDT') and ':USDT' in s]
```

### Step 2: Exclude problematic pairs

Some pairs will break your bot:

```python
# Auto-exclude non-crypto tokens
for symbol, market in exchange.markets.items():
    if market.get('info', {}).get('underlyingType') != 'COIN':
        exclude_list.append(symbol)
```

This filters out:
- **TradFi tokens** (TSLA, NVDA, GOOGL) — require agreement signing, throw `-4411` errors
- **Commodity tokens** (XAU, XAG, PAXG) — different trading rules
- **Index tokens** (BTCDOM, DEFI) — low liquidity
- **Pre-market tokens** — can halt unexpectedly

That's roughly 24 pairs eliminated automatically.

### Step 3: Volatility filter

For each remaining pair, fetch 7 days of 5-minute data and check:

- **Average candle body ≥ 0.4%** — enough movement to trigger entries
- **24h price range ≥ 12%** — the coin is actually trending, not just twitching

This eliminates about 80% of remaining pairs. BTC, ETH, SOL — all filtered out. Great for holding, terrible for 5-minute scalping.

### Step 4: 6-hour backtest ranking

For each coin that passes the volatility filter, run a 6-hour backtest using the exact same strategy parameters as the live bot. Rank by PnL.

**Take the top 8.**

### Step 5: Deploy

Replace the active coin list. Open positions on old coins are kept until they close naturally — the bot doesn't force-close them just because the coin rotated out.

## Why 3-hour rotation? Why not faster or slower?

| Interval | Problem |
|----------|---------|
| 30 minutes | Too reactive — keeps switching coins mid-trend |
| 1 hour | Slightly better but still noisy |
| **3 hours** | Balances freshness vs stability |
| 6 hours | Misses intraday volatility shifts |
| 24 hours | Coins can go cold long before rotation |

3 hours gives the bot enough time to actually trade the selected coins before re-evaluating.

## Why 8 coins specifically?

Too few coins = concentrated risk. If the scanner picks a dud, your whole session suffers.

Too many coins = diluted capital. With 80% of balance split across too many coins, position sizes become too small to overcome fees.

8 was the sweet spot in my backtests across different market periods — enough diversification to survive bad picks, few enough to concentrate on the best opportunities.

## How does the FVG bot scan differently?

I run two bots. The trend-following bot scans as described above. The FVG bot uses a different method:

- **Scan interval:** Every 6 hours
- **Universe:** Top 80 coins by 24h trading volume (50M+ USDT)
- **Ranking:** 24-hour backtest PnL (not 6-hour)
- **Selection:** Top 10 coins
- **Extra filter:** `MIN_BODY_PCT = 2.0%` — coins with small candle bodies don't produce valid FVGs

Different strategies need different coin sets. A coin that trends well (good for trend following) might not produce clean FVGs (bad for mean reversion). The scanners are independent.

## What are the gotchas with automatic coin scanning?

### Hot coins cool off

A coin pumping for the last 6 hours might be exhausted for the next 6. The 6-hour backtest window catches recent momentum, but momentum doesn't guarantee continuation.

This is a known weakness. The mitigation is diversification — 8 coins means any single bad pick is limited to 12.5% of the portfolio.

### New listings are dangerous

Freshly listed coins have extreme volatility, wide spreads, and erratic price action. The volatility filter catches them, but the backtest period is too short to be reliable.

### Don't fight the filter

I've been tempted to manually add coins I "feel good about." Every time I did, they underperformed the auto-selected ones.

**Trust the data over your gut.**

## How does coin history help?

Every scan result is saved to `coin_scan_history.json`:

```json
{
  "2026-04-10T09:02:00": {
    "selected": ["RAVE", "SIREN", "LYN", "PIPPIN", ...],
    "scores": {"RAVE": 45.2, "SIREN": 38.1, ...}
  }
}
```

This lets me:
- Track which coins appear most frequently (consistent movers vs one-time spikes)
- Compare scan selections against actual performance
- Debug why the bot traded a specific coin at a specific time

---

*The best trade is sometimes the one you didn't take — on a coin you shouldn't have been watching.*

**Related:**
- [How I Pick Coins for My Bot](/posts/how-i-pick-coins-for-my-bot-to-trade/) — The original coin selection approach
- [Building a Trend Following Bot](/posts/building-a-trend-following-bot-that-actually-works/) — The strategy these coins feed into
- [Fair Value Gaps](/posts/fair-value-gaps-the-strategy-that-changed-everything/) — Different scanner, different strategy
