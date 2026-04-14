---
title: "I Killed 4 Trading Bots So You Don't Have To"
date: 2026-04-15T18:00:00
draft: false
tags: ["trading-bot", "failures", "lessons", "crypto", "strategy", "killed-bots"]
categories: ["Story"]
series: ["Killed Bots"]
summary: "I built 6 trading bots. 4 of them are dead. Grid bot, RSI scalper, momentum bot, lead-lag bot — each died for a different reason. Here's what killed them."
---

## How many bots did I build before finding one that works?

Six. I built six trading bots. Four are dead. Two survive.

Most trading bot tutorials show you the happy path: write code, run backtest, see profits, deploy. Nobody tells you about the four graveyards you'll fill before finding something that actually works with real money.

Here's how each bot died — and what it taught me.

---

## Bot #1: The Grid Bot

**Strategy:** Place buy orders below the current price and sell orders above it, in a grid pattern. When price bounces between levels, you collect small profits on each bounce.

**How it looked in the backtest:** Smooth, consistent profits. The equity curve went up like a staircase. It felt like free money.

**How it died:** The market trended up. Then it trended down. Grid bots make money in sideways markets. In trending markets, they accumulate losing positions on one side of the grid while the other side never gets filled.

When price dropped 15% in a day, the bot had bought at every grid level on the way down. All those positions were underwater. The "consistent small profits" from sideways periods were wiped out in a single trending day.

**The fatal flaw:** Grid bots have a structural weakness against trends. And crypto trends *a lot*. You can't fix this with better parameters — it's baked into the strategy.

**What it taught me:** A strategy that only works in one market regime is not a strategy. It's a bet on the regime continuing.

---

## Bot #2: The RSI Scalper

**Strategy:** Buy when RSI drops below 30 (oversold), sell when RSI rises above 70 (overbought). Classic mean reversion on the 1-minute timeframe.

**How it looked in the backtest:** Decent win rate, lots of trades, moderate profits.

**How it died:** Slippage. On the 1-minute timeframe, the difference between backtest price and real execution price was devastating. The backtest assumed you could enter at the exact candle close price. In reality, by the time the bot detected the signal, fetched the price, and placed the order, the price had already moved.

On a 5-minute timeframe, a 0.1% slippage is noise. On a 1-minute scalping strategy where the average profit per trade was 0.3%, that same slippage ate a third of every win.

**The fatal flaw:** Scalping strategies need execution speed that's only achievable with co-located servers and direct market access. A Python bot running on a home server can't compete.

**What it taught me:** If your average win is small, slippage will eat you alive. Either make your wins bigger or get faster execution. I chose bigger wins.

---

## Bot #3: The Momentum Bot

**Strategy:** Detect strong momentum (using RSI slope, volume ratio, and candle body size) and ride the trend. Enter on breakouts, trail a stop loss, exit when momentum fades.

**How it looked in the backtest:** Incredible. After parameter optimization, it showed massive returns over historical data. I was convinced this was the one.

**How it died:** Overfitting. The "incredible" backtest results were the product of parameters perfectly tuned to historical data. The bot had memorized the past, not learned the pattern.

I deployed it live. It lost money immediately. Not slowly — immediately. The optimized parameters that worked perfectly on training data were worthless on new data.

I ran an out-of-sample test (which I should have done before going live). The bot failed spectacularly on every quarter of data it hadn't seen during optimization.

**The fatal flaw:** I optimized parameters without validating on unseen data. The backtest was telling me what I wanted to hear, not what was true.

**What it taught me:** If your backtest looks too good, it's lying. Always validate on out-of-sample data before risking real money. This lesson cost me real dollars.

---

## Bot #4: The Lead-Lag Bot

**Strategy:** Some assets lead others — when Bitcoin moves, altcoins follow with a delay. Detect the lead, trade the lag.

**How it looked in research:** The correlation was real. Statistically significant lead-lag relationships existed between BTC and certain altcoins, with delays of 30-60 seconds.

**How it died:** The opportunity disappeared. By the time I built the bot, tested it, and deployed it, the lead-lag windows had compressed from 60 seconds to under 5 seconds. High-frequency trading firms had already automated this edge away.

This isn't a backtesting failure or a coding bug. The edge was real — it just evaporated faster than I could capture it. In crypto, any publicly known inefficiency gets arbitraged away quickly.

**The fatal flaw:** The strategy required speed I couldn't achieve and an edge that was actively being competed away.

**What it taught me:** Some edges have expiration dates. If an opportunity is widely known and technically simple, assume someone faster has already taken it.

---

## What about the 2 bots that survived?

**Bot #5: The Trend Following Bot** — Uses 5-minute candle body + volume ratio + CHOP filter to enter momentum trades. Win rate around 57%, risk-reward around 1:1.2. It works because it filters aggressively and only trades when conditions are clearly trending.

**Bot #6: The FVG (Fair Value Gap) Bot** — Enters mean reversion trades at Fair Value Gaps. Win rate around 33%, but risk-reward is 1:3 — the few winners are 3x larger than the many losers. It survived a full year of out-of-sample testing.

The two survivors have something in common: **they both passed out-of-sample validation before I risked real money.** The four dead bots did not.

## What pattern do the failures share?

Looking back, every dead bot failed for a predictable reason:

| Bot | Death Cause | Warning Sign I Ignored |
|-----|-------------|----------------------|
| Grid | Structural weakness vs trends | Only worked in sideways markets |
| RSI Scalper | Slippage killed thin margins | Average win was too small |
| Momentum | Overfitting to historical data | Backtest was "too good" |
| Lead-Lag | Edge competed away | Publicly known inefficiency |

The common thread: **I wanted each one to work so badly that I ignored the warning signs.** The grid bot's weakness was obvious if I'd tested it on trending data. The RSI scalper's slippage problem was predictable. The momentum bot's overfitting was detectable with a simple out-of-sample test.

## What would I do differently?

If I started over today:

1. **Out-of-sample test before going live.** Not after. Not "I'll do it later." Before.
2. **Calculate expected slippage** and subtract it from backtest results. If the strategy is still profitable after slippage, proceed. If not, the strategy doesn't work.
3. **Test on trending AND sideways markets.** If the strategy only works in one regime, it will eventually hit the other regime and blow up.
4. **Ask: "Can someone faster do this?"** If the edge requires speed, assume you'll lose the speed race.

Four dead bots is an expensive education. But the two survivors — the ones that passed every test — are now running with real money. The graveyard made the survivors possible.

---

*Every working bot is built on the graves of the ones that didn't make it. The question isn't whether your first bot will fail — it's whether you'll learn enough from the failure to build the one that works.*

**Related:**
- [The Backtest Looked Amazing. It Was Lying.](/posts/the-backtest-looked-amazing-it-was-lying/) — The momentum bot's overfitting story
- [Why Grid Bots Are a Beautiful Lie](/posts/why-grid-bots-are-a-beautiful-lie/) — Grid bot deep dive
- [Your Trading Bot Is Overfitting. Here's How to Prove It](/posts/how-to-avoid-overfitting-in-trading-bots/) — The checklist I use now
- [One Year of Out-of-Sample Testing](/posts/one-year-of-out-of-sample-testing-did-the-fvg-bot-survive/) — How the FVG bot proved itself
