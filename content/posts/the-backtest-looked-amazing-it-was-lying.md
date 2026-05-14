---
title: "The Backtest Looked Amazing. It Was Lying."
date: 2026-04-05
draft: false
robotsNoIndex: true
tags: ["backtesting", "overfitting", "trading-bot", "crypto", "lessons-learned", "killed-bots"]
categories: ["Story"]
series: ["Killed Bots"]
summary: "My momentum bot showed incredible returns in backtests. Then I learned about overfitting — the hard way."
---

## The Dopamine Hit

I'll never forget the moment. My momentum bot's backtest came back with **insane returns**. Win rate through the roof. Drawdowns barely visible. The equity curve looked like a staircase going up.

I was ready to quit my job.

Then I tested it on data it hadn't seen before.

## What Is Overfitting?

Imagine you're studying for an exam. Instead of understanding the material, you memorize every answer from past exams. You score 100% on practice tests.

Then the real exam comes, and the questions are slightly different. You fail.

**That's overfitting.** Your strategy isn't learning patterns — it's memorizing history.

## How My Momentum Bot Fooled Me

The bot used multiple indicators with very specific parameters:
- RSI with a custom period
- Moving average crossovers with precise windows
- Volume filters with exact thresholds
- Entry and exit conditions tuned to perfection

Every parameter was optimized to maximize returns on my test data. The result looked incredible.

The problem? Those parameters were **perfectly shaped to match the past**. They had no predictive power for the future.

## The Out-of-Sample Test

Here's what I should have done from the start:

1. **Split your data.** Train on 70%, test on 30% the strategy has never seen.
2. **Walk-forward analysis.** Optimize on month 1-3, test on month 4. Optimize on month 2-4, test on month 5. Repeat.
3. **Multiple market conditions.** Test in bull markets, bear markets, and sideways. If it only works in one, it's not a strategy — it's a coincidence.

When I finally did this properly with my FVG bot later, I tested across **4 quarters over a full year**:

| Quarter | PnL | Result |
|---------|-----|--------|
| 2025 Q2 | +271U | Profitable |
| 2025 Q3 | +38U | Barely profitable |
| 2025 Q4 | +273U | Profitable |
| 2026 Q1 | -36U | Loss |

3 out of 4 quarters profitable, with one weak quarter during a sideways market. **That's** what a real strategy looks like — not perfect, but consistently positive.

## Red Flags Your Backtest Is Lying

1. **Win rate above 70%** — In crypto, even great strategies win 30-40% of the time. A high win rate usually means you're curve-fitting.

2. **No losing months** — Real strategies have drawdowns. If yours doesn't, you're overfitting.

3. **Too many parameters** — Each parameter you add is another degree of freedom to fit noise. The best strategies are simple.

4. **Smooth equity curve** — Real trading is messy. If your equity curve looks like a smooth line going up, be suspicious.

5. **Huge returns on short data** — +500% in 2 weeks? That's noise, not signal.

## The Expert Principle

> "Total returns are far more influenced by risk-reward ratio than by win rate."

A strategy with 35% win rate and 1:1.5 risk-reward **beats** a strategy with 60% win rate and 1:0.5 risk-reward. Every time.

Stop chasing high win rates. Start thinking about how much you make when you win versus how much you lose when you lose.

## What I Do Now

For every strategy I build:

1. **Backtest on historical data** — Does it work at all?
2. **Out-of-sample test** — Does it work on data it hasn't seen?
3. **Dry run** — Does it match the backtest in real-time (without real money)?
4. **Live with small size** — Does it survive the real market?

Each step kills about 80% of strategies. The ones that survive all four are worth running.

My momentum bot didn't survive step 2. My trend-following bot survived all four. That's the difference between a dream and a strategy.

---

*The most expensive lesson in trading isn't a bad trade — it's trusting a good backtest.*
