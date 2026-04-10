---
title: "I Let AI Pick My Trading Strategy — Here's What Happened"
date: 2026-04-10T12:00:00
draft: false
tags: ["claude-code", "ai", "trading-bot", "strategy", "crypto", "machine-learning"]
categories: ["Story"]
summary: "I gave Claude Code my trading data, my failures, and my constraints. Then I asked it to design a strategy from scratch. The result outperformed everything I'd built manually."
---

## The Setup

I had just killed my 4th trading bot. Grid bot, RSI scalper, lead-lag arb, momentum bot — all dead for different reasons.

I was frustrated. Not because the code didn't work — it worked perfectly. The strategies were the problem. I kept building bots that looked great in backtests and bled money in production.

So I tried something different. Instead of coming up with another strategy myself, I asked Claude Code to analyze my failures and suggest what to build next.

## What I Gave It

I didn't just say "give me a trading strategy." That would have gotten me a generic RSI crossover tutorial.

Instead, I gave it context:

1. **My dead bots** — what each one did and why it failed
2. **My constraints** — $500 starting capital, Binance Futures, 3x leverage max
3. **My backtest results** — the actual numbers, including the ones that looked good but failed live
4. **My principles** — risk-reward > win rate, no overfitting, must survive trending AND sideways markets

Then I asked: "Given everything that failed, what should I build?"

## What It Suggested

Claude didn't give me one strategy. It analyzed the failure patterns and pointed out something I'd missed:

**Every dead bot shared the same flaw — they all tried to predict direction.**

- Grid bot: predicted a range
- RSI scalper: predicted reversals
- Momentum bot: predicted continuations
- Lead-lag: predicted correlation persistence

Claude's suggestion: **Stop predicting. Start reacting.**

Instead of "I think price will go up, so buy" → "Price IS going up strongly right now, confirmed by volume, so ride it."

This became my Trend Following bot.

## The Strategy Claude Helped Design

The core logic was surprisingly simple:

### Entry Signal
```
1. 5-minute candle has a large body (≥ 0.7%)
   → Price moved decisively, not just noise

2. Volume Ratio ≥ 1.5x average
   → The move has real participation behind it

3. Choppiness Index < 50
   → Market is actually trending, not chopping sideways
```

That's it. No prediction. No "RSI is oversold so it should bounce." Just: **is something happening right now, with conviction?**

### What Claude Got Right

**The volume filter was the key insight I kept missing.**

In my previous bots, I entered on price signals alone. Claude pointed out that price moves without volume are noise — they reverse immediately. Volume confirms that real money is behind the move.

Before the volume filter: 40% win rate, barely profitable.
After: 57% win rate, consistently profitable.

### What Claude Got Wrong

Claude initially suggested using multiple timeframe confirmation — check 5m, 15m, 1h, and 4h signals before entering.

Sounds logical. More confirmation = more certainty, right?

**In practice, it killed the bot.** By the time all four timeframes aligned, the move was already over. The bot entered at the top of every trend.

I removed it and went back to single-timeframe (5m) with a simple choppiness filter. Fewer signals, but they worked.

**Lesson: AI gives you good frameworks but bad parameter choices.** The structural idea was sound. The specific implementation needed human judgment and backtesting.

## The Iteration Loop

Here's how the collaboration actually worked:

```
Me:     "The bot lost $50 this week. Here are the trades."
Claude: "Look at trades #12, #18, #23 — all entered during 
         choppy markets. Your entry filter needs a regime detector."

Me:     "I added CHOP index. Now it filters 40% of trades."
Claude: "Run the backtest. What's the PnL delta?"

Me:     "Net PnL went from +100 to +180. But I'm missing 
         some winning trades too."
Claude: "That's expected. Show me the filtered trades — 
         are the missed winners bigger or smaller than average?"

Me:     "Smaller. Average $4 vs $7 for the ones that passed."
Claude: "Then the filter is working. It's cutting noise, 
         not edge. Keep it."
```

This back-and-forth happened dozens of times. Each cycle:
1. Run the bot or backtest
2. Dump the results to Claude
3. Get analysis and suggestions
4. Implement, test, repeat

**Claude never wrote the final strategy alone.** It analyzed data faster than I could, spotted patterns I missed, and challenged my assumptions. But the decisions were mine.

## The Parameter Optimization Trap

At one point, Claude suggested running a grid search across 15 parameters to find the optimal combination.

The grid search found a combination that returned +1,400 USDT in backtesting. Incredible.

I almost deployed it. Then I remembered my momentum bot — the one that died from overfitting. I asked Claude to run the same parameters on out-of-sample data.

Result: **-200 USDT.**

The "optimal" parameters had memorized the training data. Classic overfitting.

We went back to simpler parameters — fewer variables, wider ranges, less precision. The backtest dropped to +800 USDT, but the out-of-sample held at +500 USDT.

**I asked Claude for the best parameters. Claude gave them to me. They were wrong.** Not because Claude is bad at optimization — because optimization itself is the trap. AI can find the overfitted peak faster than any human. That doesn't make it useful.

## What AI Is Actually Good At (In Trading)

After months of this, here's my honest assessment:

### AI Excels At:
| Task | Why |
|------|-----|
| **Bug detection** | "Your SL is checking best_price but should check worst_price" |
| **Pattern analysis** | "80% of your losses happen in the first hour of Asia session" |
| **Code generation** | Building the actual bot, fast and (mostly) correct |
| **Framework design** | "You need trend detection + volume confirmation + regime filter" |
| **Failure analysis** | "This strategy fails because X, not because of bad luck" |

### AI Is Bad At:
| Task | Why |
|------|-----|
| **Predicting markets** | No AI can consistently predict price direction |
| **Parameter optimization** | It finds the overfitted answer too easily |
| **Knowing when to stop** | It'll keep adding complexity if you let it |
| **Risk management** | It doesn't feel the pain of losing money. You do. |

## The Results

The Trend Following bot (designed with Claude, not by Claude) has been running live since late February 2026:

- **6 weeks of live trading**
- **Win rate: ~57%**
- **Risk-reward: ~1:1.2**
- **Still running. Still profitable.**

It's not a moonshot. It's not "quit your job" money. But it's a strategy that survived the gap between backtest and reality — which is more than I can say for bots #1 through #4.

## The Second Bot

After the trend follower stabilized, I asked Claude to help me build something complementary — a strategy that would perform well when trend following struggled.

The answer: **mean reversion using Fair Value Gaps.**

Different entry logic, different market conditions, different edge. When the trend bot sits idle in choppy markets, the FVG bot trades. When the FVG bot struggles in strong trends, the trend bot prints.

Two bots, designed together, covering each other's weaknesses. That portfolio idea? Claude's suggestion. And it was one of the best ones.

## What I'd Tell Someone Starting Today

1. **Don't ask AI for a strategy.** Ask it to analyze your failures. The strategy emerges from understanding what doesn't work.

2. **AI is a collaborator, not an oracle.** It accelerates your learning by 10x, but the judgment calls are yours.

3. **Be suspicious of AI's "optimal" answers.** The best answer in a backtest is usually the most overfit one.

4. **Feed it real data, not hypotheticals.** "What strategy should I use?" gets a generic answer. "Why did these 47 trades lose money?" gets a useful one.

5. **The AI doesn't care if you lose money.** It'll build whatever you ask for, beautifully, even if what you asked for is garbage. You need to be the skeptic.

## The Honest Truth

Claude Code didn't give me a winning strategy. It gave me a faster way to find one.

Without AI, I'd still be on bot #2, manually scanning trade logs, guessing at what went wrong. With AI, I iterated through 6 strategies in a few months, identified exactly why each one failed, and converged on something that works.

The AI wrote most of the code. The AI analyzed most of the data. But the AI didn't make the decisions that mattered — when to cut a strategy, how much risk to take, when to stop optimizing and start trading.

That part is still human. And honestly? I think it should stay that way.

---

*The best use of AI in trading isn't to replace your judgment. It's to give your judgment better data to work with.*
