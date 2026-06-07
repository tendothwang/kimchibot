---
title: "30 Days, +$952.72 on Binance — Copy-Trade Coming"
date: 2026-06-07T20:34:18+09:00
draft: false
tags: ["live-trading", "performance", "fvg", "trading-bot", "monthly-report", "copy-trade"]
categories: ["Report"]
series: ["Monthly Report"]
summary: "30 days from May 9 to June 7, +$952.72 net by Binance's own ledger. The current bot, the work spent matching live to backtest, and a few real trades."
---

From May 9 to June 7 — 30 days — the bot finished **+$952.72** by Binance's own ledger.

Second monthly report in a row in the green.

I made small adjustments this month.

The dynamic risk-reward ladder is tuned to clip losses in overheated zones, and the FVG entry condition now allows a setup where the C3 candle has a bigger body than the C2 (a trend acceleration case).

Nothing dramatic — the kind of small parameter changes that show consistently positive across the 90-day backtest.

Here's what the engine does right now.

5-minute FVG retracement — when price returns to a gap left by a C2 strong-body candle (body ≥ 2.0%), the bot enters. The stop sits just past the C1 wick, placed on the exchange as a STOP_LIMIT at entry. The take-profit ratio is something the user decides.

A 25-MA angle filter blocks entries when the trend is breaking apart (±40°). Anything still alive at +1% after four hours gets cut by a time exit.

The coin pool re-rolls every 12 hours (08:32 and 20:32 KST) — 20 names.

What I've spent most of my time on the last few months is making the live bot match the backtest, bar-for-bar.

I shut down look-ahead at the resample boundary, disabled within-the-entry-bar SL/TP processing, mirrored the STOP_LIMIT fill timing in the backtest engine, and verified that the 5-minute cache's quote-volume and trade-count columns line up with raw kline values every time.

The result is that `bt_standard.py` — a 1:1 mirror of the live bot — produces trade-by-trade output that matches the live log almost exactly.

The practical meaning: if a new backtest comes back positive, the live bot is very likely to come back positive too.

A few trades the bot caught this window (for credibility):

| Time (KST) | Symbol | Side | Entry | Exit | Result | PnL |
|---|---|---|---|---|---|---|
| 2026-05-23 01:50 | BSB/USDT | long | 0.5716 | 0.7613 | TP | +$198.74 |
| 2026-05-26 21:40 | DRIFT/USDT | short | 0.0384 | 0.0435 | SL | -$81.70 |
| 2026-05-29 10:29 | ALLO/USDT | long | 0.1696 | 0.2050 | TP | +$124.91 |
| 2026-06-01 07:55 | H/USDT | long | 0.4545 | 0.5504 | TP | +$125.77 |
| 2026-06-03 06:55 | LAB/USDT | long | 20.1145 | 15.1164 | SL | -$144.11 |

I'm also running a separate MA-only strategy on a sub-account.

---

Up to now this blog has just been about writing up a bot that runs on my own account.

**A Binance copy-trade account is coming soon.**

Copy trading is a Binance feature that lets one account's trades automatically replicate to other subscribed accounts — subscribers don't have to trade manually, they ride along when my bot enters and exits.

I'll write a dedicated post once it's set up.

If you trade futures and want to use the same exchange the bot runs on, my Binance referral code is **`320671536`** — [register here](https://www.binance.com/register?ref=320671536).

I get a small commission on your fees, no extra cost to you.
