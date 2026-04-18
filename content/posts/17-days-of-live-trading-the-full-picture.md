---
title: "17 Days of Live Trading: +394U, a -527U Hole, and the Comeback"
date: 2026-04-18T18:00:00
draft: false
tags: ["live-trading", "performance", "fvg", "real-money", "trading-bot", "monthly-report"]
categories: ["Story"]
series: ["AI vs Market"]
summary: "My bot went -527U in the first week. I didn't turn it off. Here's what happened next — with real numbers from Binance."
---

## What does it feel like to watch your bot lose $527 in a week?

Day 3 was the worst. The bot lost **-385U in a single day**. Not in a backtest. Not in simulation. Real money, real Binance account, real loss.

I stared at the screen. The equity curve looked like a cliff. Every instinct said: *turn it off. Cut the losses. This doesn't work.*

I didn't turn it off.

By day 17, the bot had climbed back to **+394U profit**. Here's the full story — with every number pulled directly from my Binance account.

## What do 17 days of real trading actually look like?

| Day | Trades | Net PnL | Cumulative |
|-----|--------|---------|------------|
| Apr 1 | 112 | +25.1U | +25.1U |
| Apr 2 | 447 | -37.2U | -12.1U |
| **Apr 3** | **627** | **-385.9U** | **-398.0U** |
| Apr 4 | 502 | -87.1U | -485.1U |
| Apr 5 | 926 | +38.7U | -446.4U |
| Apr 6 | 279 | -9.3U | -455.8U |
| Apr 7 | 256 | +150.0U | -305.8U |
| Apr 8 | 174 | -40.4U | -346.2U |
| Apr 9 | 101 | -112.5U | -458.6U |
| Apr 10 | 138 | -43.6U | -502.3U |
| Apr 11 | 120 | +115.4U | -386.9U |
| Apr 12 | 266 | +33.5U | -353.5U |
| Apr 13 | 230 | -69.1U | -422.6U |
| Apr 14 | 270 | +16.6U | -406.0U |
| Apr 15 | 165 | +204.1U | -201.9U |
| Apr 16 | 192 | +8.5U | -193.5U |
| **Apr 17** | **381** | **+429.6U** | **+236.2U** |
| Apr 18 | 113 | +157.8U | +394.0U |

5,299 trades. 17 days. The equity curve went from +25U to -527U to +394U.

## What happened on the worst day?

April 3rd. -385.9U.

The bot executed 627 trades — the highest daily count. This was early in the month, before I had tightened the coin selection filters. The bot was trading too many coins, including ones that don't respect Fair Value Gaps.

The problem wasn't one catastrophic trade. It was **death by a thousand cuts** — dozens of small stop losses, all hitting in the same direction, on coins that shouldn't have been in the rotation.

This single day led me to implement the SL ratio filter that bans coins with stop loss rates above 65%.

## How did the bot recover from -527U?

It didn't "recover" in one dramatic moment. It ground back slowly:

- **Days 1-10:** -502U. Painful. Multiple failed days.
- **Days 11-14:** Stabilized. Small wins, small losses. Stopped the bleeding.
- **Days 15-18:** The breakout. +204U, +8U, +429U, +157U in four days.

The turning point was the filter improvements from the first week: tighter coin selection, SL ratio banning, and the gap/body parameter changes. The bot was trading fewer coins but better ones.

## Where did the money actually go?

Here's the honest breakdown:

| Category | Amount |
|----------|--------|
| Realized PnL | +685.9U |
| Funding fees | -65.1U |
| Trading fees | -226.9U |
| **Net profit** | **+394.0U** |

**Fees ate 42% of the gross profit.** This is the number nobody talks about. My bot made +685U in raw trading gains, but I only kept +394U after fees.

Trading fees alone were -226.9U across 5,299 trades — that's about 0.04U per trade. It sounds tiny, but it compounds: 5,299 × 0.04 = 226U gone.

Funding fees were another -65U. These are the costs of holding leveraged positions on Binance Futures.

## Which coins made money and which lost?

**Top 5 winners:**

| Coin | Net PnL |
|------|---------|
| STO | +218.5U |
| SIREN | +124.7U |
| 1000SATS | +112.4U |
| BULLA | +94.5U |
| RAVE | +85.8U |

**Top 5 losers:**

| Coin | Net PnL |
|------|---------|
| NOM | -168.3U |
| AIOT | -116.3U |
| PIPPIN | -62.1U |
| LAB | -49.6U |
| TNSR | -44.9U |

NOM alone cost -168U — mostly from -22.7U in funding fees (holding losing positions too long) plus -136U in realized losses.

The pattern is clear: **a few good coins carry the portfolio, and a few bad coins drag it down.** The SL ratio filter exists to catch the bad ones before they do too much damage.

## What's the gap between backtest and reality?

| Metric | Bot Record | Actual |
|--------|-----------|--------|
| PnL | +920U | +394U |
| Difference | | -526U |

The bot's internal log says +920U. The actual Binance account says +394U. Where did 526U disappear?

- **Fees:** -227U in trading fees + -65U in funding = -292U
- **Slippage:** Market orders don't fill at exact backtest prices
- **Timing gaps:** The bot's internal clock vs exchange execution has micro-delays
- **Failed orders:** Some orders were rejected and re-entered at worse prices

This is why I never trust backtest numbers alone. The only number that matters is what Binance actually shows.

## What would I change looking back?

1. **Start with the SL filter from day 1.** The first week's losses were mostly from coins that should have been filtered out.
2. **Smaller position sizes during the learning period.** I used 160U per trade from day 1. Starting at 80U and scaling up after validation would have cut the drawdown in half.
3. **Nothing about the strategy itself.** The FVG logic, the 1:3 risk-reward, the coin scanning — all of that worked as designed. The issue was operational, not strategic.

## Is +394U in 17 days good?

That's +23.2U per day on average. On a starting capital that supports 160U positions at 3x leverage across 10 coins, that's a meaningful return.

But the maximum drawdown was -527U. That means at one point, I was down more than I eventually made. The risk-adjusted return matters more than the raw number.

The honest answer: **it's promising, but 17 days isn't enough data.** I need 3-6 months of live results to know if this is a sustainable edge or a lucky streak. The out-of-sample backtest says it's real. The first 17 days of live trading don't contradict that. But I'm not calling it proven yet.

---

*The backtest tells you what could happen. Live trading tells you what actually happened. The gap between them is where the real lessons live.*

**Related:**
- [April 2026 Live Trading Report](/posts/april-2026-live-trading-report/) — Full monthly breakdown with detailed stats
- [One Year of Out-of-Sample Testing](/posts/one-year-of-out-of-sample-testing-did-the-fvg-bot-survive/) — The backtest that gave me confidence to go live
- [Some Coins Will Always Kill Your Bot](/posts/the-sl-ratio-filter-how-i-ban-coins-that-dont-respect-fvgs/) — The filter that stopped the bleeding
- [Why My Bot Loses 67% of Trades and Still Makes Money](/posts/why-my-bot-loses-67-percent-of-trades-and-still-makes-money/) — The math behind low win rate profitability
