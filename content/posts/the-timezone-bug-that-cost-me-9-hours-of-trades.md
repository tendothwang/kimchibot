---
title: "The Timezone Bug That Cost Me 9 Hours of Trades"
date: 2026-03-29
draft: false
tags: ["debugging", "timezone", "python", "trading-bot", "crypto"]
categories: ["Engineering"]
summary: "My bot was missing every trade for the first 9 hours of each day. The cause? Mixing UTC and KST in one line of code."
---

## The Symptom

I noticed something weird. My backtest showed entries throughout the day, but the first batch of trades always started around 9 AM KST.

For the first 9 hours? Nothing. Zero entries. Every single day.

My live bot was trading fine during those hours. But my backtest was blind to them.

## The Hunt

I checked everything:
- Entry conditions? Working.
- Data feed? Complete.
- Candle timestamps? Looked correct.
- RSI warmup? Sufficient.

Everything looked fine individually. The bug was in the interaction between two correct-looking pieces of code.

## The Bug

```python
# What I wrote
start_dt = datetime(2026, 3, 10, 0, 0)  # "March 10, midnight"

# What I meant
# March 10, 00:00 KST

# What the exchange interpreted
# March 10, 00:00 UTC = March 10, 09:00 KST
```

I was passing a "naive" datetime (no timezone info) to an API that expected UTC. My local time is KST (UTC+9).

So when I said "start at midnight," the exchange heard "start at midnight UTC," which is 9 AM in Korea.

**Nine hours of trades, invisible.**

## Why It Was Hard to Find

The timestamps in my logs looked correct because I was formatting them in local time. The data was correct — just starting 9 hours late. And since I usually analyzed data from "yesterday" (a full day), the missing morning hours weren't obvious.

It only became visible when I compared live trades against the backtest hour by hour.

## The Fix

```python
# Convert local time to UTC before API calls
KST_OFFSET = 9  # hours
start_dt_utc = start_dt - timedelta(hours=KST_OFFSET)
```

And for display, always convert back to KST:

```python
ts_label = utc_time + timedelta(hours=KST_OFFSET)
```

**One rule: all internal times in UTC, all display times in KST. No exceptions.**

## The Deeper Problem

This bug existed because I was sloppy about timezones from the start. I mixed:
- `datetime.now()` (local KST) in the live bot
- UTC timestamps from the exchange API
- Naive datetimes in the backtest

Every combination of two worked fine. All three together created a 9-hour ghost.

## Timezone Rules for Trading Bots

After this disaster, I follow these rules:

1. **Pick one internal timezone and stick with it.** UTC is standard, but whatever you pick, be consistent.

2. **Never use naive datetimes.** Always attach timezone info, or at minimum, document which timezone every variable uses.

3. **Label your outputs.** Every timestamp in logs should say `(KST)` or `(UTC)`. Future you will thank present you.

4. **Test across timezone boundaries.** If your backtest starts at midnight, does it start at YOUR midnight or the exchange's midnight?

5. **Compare live vs backtest hourly.** Daily totals can mask timezone offsets that cancel out.

## The Cost

This wasn't just a code quality issue. Those 9 missing hours in the backtest meant:
- Optimization results were wrong (trained on partial data)
- Strategy comparisons were skewed
- I couldn't verify live trades against backtest for morning sessions

**A one-line bug that invalidated weeks of analysis.**

---

*The scariest bugs aren't the ones that crash your program. They're the ones that silently give you wrong answers.*
