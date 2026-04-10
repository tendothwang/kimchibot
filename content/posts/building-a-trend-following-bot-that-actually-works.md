---
title: "Building a Trend Following Bot That Actually Works"
date: 2026-04-03
draft: false
tags: ["trend-following", "trading-bot", "python", "crypto", "binance"]
categories: ["Strategy"]
summary: "After killing 4 bots, I built one that survived backtesting, dry runs, and live trading. Here's the full breakdown."
---

## Can a trend following bot actually make money in crypto?

Out of 6 bots I built, this is the one that lived. The Trend Following Bot v4.0.

It's not sexy. It doesn't have a fancy name. It doesn't promise 1000% returns. But it makes money — consistently, across different market conditions, with real capital.

Here's how it works.

## How does a trend following trading bot work?

**Follow the trend. Don't predict it.**

When a coin starts moving with strong momentum and volume, jump on. When the momentum fades, get out. Don't try to catch tops or bottoms. Don't try to be clever.

Most beginner traders try to predict reversals. "It's gone up too much, it must come down." This is how you blow up. Markets can stay irrational longer than you can stay solvent.

## What entry signals does the bot use?

The bot scans every 5 minutes. To enter a trade, ALL of these must be true:

### 1. Candle Body Size ≥ 0.7%
The current 5-minute candle must have a body (open-to-close) of at least 0.7%. This filters out noise and sideways chop.

### 2. Volume Ratio (VR)
- Long: VR ≥ 1.8
- Short: VR ≥ 1.5

Volume must be significantly above average. Big moves on low volume are traps.

### 3. CHOP Index < 50
The Choppiness Index measures how "choppy" (sideways) the market is. Below 50 means trending. Above 50 means ranging.

This is the most important filter. It keeps the bot out of sideways markets where trend-following strategies get chopped up (pun intended).

### 4. BTC RSI ≥ 35 (Longs Only)
Don't go long on altcoins when Bitcoin is in freefall. Simple but effective.

## How does the bot exit trades?

Getting in is easy. Getting out is where the real money is made or lost.

### Stop Loss: 2.0% (STOP_LIMIT Order)
- Placed as a limit order on the exchange, not monitored client-side
- No slippage from cascade liquidations
- If the limit order doesn't fill, auto-converts to market order

### Trailing Stop: TA 2.0% / TS 0.5%
- Activates when profit reaches 2.0%
- Trails at 0.5% behind the best price
- **Critical:** Checked only at 5-minute candle closes, not tick-by-tick
- This prevents getting stopped out by momentary price dips

### Surge Detection
When a trade moves +4% before the first 5-minute candle closes:
- Phase 1: Tight trailing stop (0.5%) on 1-minute candle closes
- Phase 2: Reverts to normal trailing

This captures explosive moves without giving back too much profit.

### Time-Based Take Profit
After 30 minutes, if profit ≥ 0.5%, switch to a tight 0.25% trailing stop. This prevents winners from becoming losers due to momentum exhaustion.

## How does the bot automatically select which coins to trade?

The bot doesn't trade the same coins forever. Every 3 hours, it automatically:

1. **Filters** all Binance Futures pairs by volatility (avg candle body ≥ 0.4%, 24h range ≥ 12%)
2. **Backtests** each passing coin over the last 6 hours
3. **Selects** the top 8 by PnL

This way, the bot always trades the coins that are actually moving right now.

## Money Management

- Uses 80% of balance, divided equally among 8 coins
- 3x leverage (conservative for crypto)
- Compound growth — profits increase position sizes

## What are realistic win rates and returns for a trend following bot?

This isn't a get-rich-quick setup. Here's what realistic performance looks like:

- **Win rate:** ~57% (not spectacular, and that's fine)
- **Risk-reward:** Better than 1:1 on average
- **Stop losses:** ~2.6% of trades
- **Average hold time:** ~2.6 hours

The key insight from an expert I respect:

> "Total returns are far more influenced by risk-reward ratio than by win rate. A 1:1.5 risk-reward with 30-40% win rate is enough."

## What makes this bot different from other trend following bots?

### 1. Separate Long/Short Parameters
Longs and shorts behave differently in crypto. Crashes are faster than rallies. The bot uses different VR thresholds, SL levels, and trailing parameters for each direction.

### 2. No Prediction, Just Reaction
The bot doesn't try to predict where the market is going. It reacts to what's already happening. This is boring but profitable.

### 3. Ruthless Filtering
Most signals are rejected. CHOP filter alone eliminates ~60% of potential entries. Better to miss a trade than take a bad one.

### 4. Backtest-Live Parity
Every parameter in the live bot has an exact match in the backtest. I verify regularly that live trades match backtest predictions within 0.5U. This took weeks of debugging but it's the foundation of trust in the system.

## What are the weaknesses of a trend following bot?

It's not all profits:

- **Sideways markets hurt.** When crypto goes flat, the bot either doesn't trade (good) or gets chopped (bad).
- **SL cascades happen.** Sometimes 3-4 stop losses in a row. Psychologically brutal, mathematically expected.
- **Coin selection can fail.** Hot coins in the last 6 hours aren't always hot in the next 6.

The key is accepting that ~40% of trades will lose, and the winners will more than cover the losses. If you can't stomach that, automated trading isn't for you.

---

*Next up: the FVG (Fair Value Gap) bot — a completely different approach that also works.*
