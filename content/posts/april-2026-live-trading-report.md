---
title: "April 2026 Live Trading Report"
date: 2026-04-18T05:00:00
draft: false
tags: ["live-trading", "performance", "monthly-report", "fvg", "trading-bot", "crypto"]
categories: ["Report"]
series: ["Monthly Report"]
summary: "Real Binance numbers from April 2026. 5,299 trades, +394U net profit, -527U max drawdown. Full breakdown by day, coin, and cost."
---

## Summary

| Metric | Value |
|--------|-------|
| Period | Apr 1-18, 2026 (17 days) |
| Total trades | 5,299 |
| Realized PnL | +685.9U |
| Funding fees | -65.1U |
| Trading fees | -226.9U |
| **Net profit** | **+394.0U** |
| Daily average | +23.2U |
| Max drawdown | -527.4U |

## Daily breakdown

| Date | Trades | Realized | Funding | Fees | Net | Cumulative |
|------|--------|----------|---------|------|-----|------------|
| Apr 1 | 112 | +31.6U | -3.1U | -3.5U | +25.1U | +25.1U |
| Apr 2 | 447 | +1.4U | -11.8U | -26.8U | -37.2U | -12.1U |
| Apr 3 | 627 | -353.0U | -10.0U | -22.9U | -385.9U | -398.0U |
| Apr 4 | 502 | -68.2U | +0.2U | -19.2U | -87.1U | -485.1U |
| Apr 5 | 926 | +77.5U | -2.6U | -36.1U | +38.7U | -446.4U |
| Apr 6 | 279 | +4.6U | -2.8U | -11.2U | -9.3U | -455.8U |
| Apr 7 | 256 | +160.3U | +0.8U | -11.1U | +150.0U | -305.8U |
| Apr 8 | 174 | -32.0U | -0.9U | -7.5U | -40.4U | -346.2U |
| Apr 9 | 101 | -106.2U | -1.7U | -4.5U | -112.5U | -458.6U |
| Apr 10 | 138 | -32.6U | -4.2U | -6.8U | -43.6U | -502.3U |
| Apr 11 | 120 | +121.1U | -0.6U | -5.1U | +115.4U | -386.9U |
| Apr 12 | 266 | +41.0U | +1.5U | -9.0U | +33.5U | -353.5U |
| Apr 13 | 230 | -58.4U | -0.9U | -9.9U | -69.1U | -422.6U |
| Apr 14 | 270 | +23.6U | +3.4U | -10.5U | +16.6U | -406.0U |
| Apr 15 | 165 | +244.7U | -31.6U | -9.1U | +204.1U | -201.9U |
| Apr 16 | 192 | +19.2U | +1.3U | -12.0U | +8.5U | -193.5U |
| Apr 17 | 381 | +445.2U | +1.1U | -16.6U | +429.6U | +236.2U |
| Apr 18 | 113 | +166.1U | -3.2U | -5.1U | +157.8U | +394.0U |

## Top performing coins

| Coin | Net PnL | Realized | Funding | Fees |
|------|---------|----------|---------|------|
| STO | +218.5U | +234.1U | +0.4U | -16.0U |
| SIREN | +124.7U | +143.3U | +1.5U | -20.1U |
| 1000SATS | +112.4U | +114.1U | +0.0U | -1.7U |
| BULLA | +94.5U | +102.5U | -0.2U | -7.8U |
| RAVE | +85.8U | +125.0U | -33.3U | -6.0U |
| HIGH | +80.3U | +81.7U | +0.0U | -1.4U |
| IN | +74.5U | +75.2U | +0.0U | -0.7U |
| NEIRO | +65.9U | +67.0U | +0.0U | -1.1U |
| PLAY | +64.6U | +66.5U | +0.8U | -2.7U |
| TRU | +63.5U | +67.0U | -0.5U | -3.0U |

## Worst performing coins

| Coin | Net PnL | Realized | Funding | Fees |
|------|---------|----------|---------|------|
| NOM | -168.3U | -136.1U | -22.7U | -9.5U |
| AIOT | -116.3U | -107.2U | +0.8U | -9.9U |
| PIPPIN | -62.1U | -53.8U | -0.3U | -7.9U |
| LAB | -49.6U | -47.1U | +0.2U | -2.7U |
| TNSR | -44.9U | -46.9U | +2.8U | -0.8U |
| BASED | -44.4U | -36.8U | -0.1U | -7.4U |
| LYN | -42.7U | -40.1U | -0.5U | -2.0U |
| KOMA | -42.2U | -40.5U | +0.0U | -1.7U |
| GIGGLE | -40.5U | -38.6U | +0.0U | -1.9U |
| AGT | -39.6U | -40.9U | +1.6U | -0.4U |

## Cost analysis

| Cost type | Amount | % of gross PnL |
|-----------|--------|----------------|
| Trading fees | -226.9U | 33.1% |
| Funding fees | -65.1U | 9.5% |
| **Total costs** | **-292.0U** | **42.6%** |

Fees consumed 42.6% of the gross trading profit.

## Bot record vs actual

| Source | PnL |
|--------|-----|
| Bot internal log | +920.1U |
| Binance actual | +394.0U |
| Gap | -526.1U |

The gap is primarily from trading fees (-226.9U), funding fees (-65.1U), slippage on market orders, and order rejection/re-entry costs.

## Key events

- **Apr 3:** Worst day (-385.9U). High trade count on unfiltered coins. Led to SL ratio filter implementation.
- **Apr 5:** Gap/body filter tightened (gap 1.5-4%, body ≥ 2%). Trade quality improved immediately.
- **Apr 8:** SL ratio filter set to 65%. Banned high-loss coins from rotation.
- **Apr 9:** AGT incident — market close order rejected, unmanaged position lost -121U. Fixed with 3-retry close + emergency SL placement.
- **Apr 15-18:** Four consecutive profitable days (+800U combined) after filter improvements stabilized.

## Strategy parameters

- **Strategy:** FVG (Fair Value Gap) mean reversion
- **Timeframe:** 5-minute
- **Risk-reward:** 1:3 (fixed)
- **FVG gap:** 1.5% - 4.0%
- **C2 candle body:** ≥ 2.0%
- **Position size:** 160U × 3x leverage
- **Coin selection:** Top 10 by 24h backtest PnL, SL ratio < 65%
- **Scan interval:** Every 6 hours

---

*This report covers April 1-18 only. A full month report will be published after April 30.*

**Related:**
- [17 Days of Live Trading: The Full Picture](/posts/17-days-of-live-trading-the-full-picture/) — The story behind these numbers
- [Fair Value Gaps: The Strategy That Changed Everything](/posts/fair-value-gaps-the-strategy-that-changed-everything/) — How the FVG strategy works
- [Some Coins Will Always Kill Your Bot](/posts/the-sl-ratio-filter-how-i-ban-coins-that-dont-respect-fvgs/) — The SL ratio filter
