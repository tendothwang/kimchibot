---
title: "The 3 AM Bug: PID Lockfiles and Duplicate Processes"
date: 2026-03-24
draft: false
tags: ["debugging", "python", "pid", "trading-bot", "devops"]
categories: ["Engineering"]
summary: "My bot was running twice. Two instances, same account, doubling every order. Here's how PID lockfiles saved me."
---

## The Nightmare Scenario

Picture this: you wake up at 3 AM to check your bot. Everything looks normal — except your position sizes are doubled. Every trade has two identical entries.

Your bot is running **twice**.

How? You restarted the bot but the old process didn't die. Or your system service spawned a second instance. Or you ran the script in a second terminal and forgot.

Two bots, same API keys, same strategy, same coins. Every signal triggers two orders. Your risk is now 2x what you planned.

## The Problem

Python scripts don't have built-in protection against duplicate instances. If you run `python bot_trendfollow.py` twice, you get two bots. Both connect to Binance. Both place orders. Chaos.

This is especially dangerous because:
- Both instances see the same signals
- Both try to open positions → double exposure
- Both try to close positions → one succeeds, one gets ReduceOnly errors
- Log files get interleaved → impossible to debug

## The Solution: PID Lockfile

```python
import os
import sys

LOCKFILE = '/tmp/bot_trendfollow.pid'

def acquire_lock():
    if os.path.exists(LOCKFILE):
        with open(LOCKFILE, 'r') as f:
            old_pid = int(f.read().strip())
        
        # Check if the old process is still running
        try:
            os.kill(old_pid, 0)  # Signal 0 = just check
            print(f"Bot already running (PID {old_pid}). Exiting.")
            sys.exit(1)
        except OSError:
            # Old process is dead, stale lockfile
            print(f"Removing stale lockfile (PID {old_pid})")
    
    # Write our PID
    with open(LOCKFILE, 'w') as f:
        f.write(str(os.getpid()))

def release_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)
```

At startup: check if another instance is running. If yes, refuse to start. If the old process crashed (stale lockfile), clean up and proceed.

## Why Not Just Check the Process Name?

You might think: just check if `python bot_trendfollow.py` is in the process list.

Problems:
1. Multiple Python scripts might be running
2. Process names can be ambiguous
3. What if the script was renamed?
4. What if it's running inside a virtual environment with a different Python path?

PID lockfiles are explicit: "process X claimed this lock." If process X is dead, the lock is stale. Simple.

## The Stale Lockfile Problem

What if your bot crashes without cleaning up the lockfile? The next time you start it, it finds the lockfile, checks the PID, and... the PID belongs to a completely different process that reused the number.

This is rare on modern systems (PID numbers go up to 32768+ and cycle slowly), but it happens.

**Solution:** Add a process name check as a secondary validation:

```python
import psutil

def is_our_process(pid):
    try:
        proc = psutil.Process(pid)
        return 'bot_trendfollow' in ' '.join(proc.cmdline())
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
```

## What I Actually Use

My bot's startup sequence:

1. **Check lockfile** — Is another instance running?
2. **Sync with exchange** — What positions are already open?
3. **Resync time** — Match clock with Binance
4. **Start main loop** — Begin scanning

And on shutdown (including crashes):

```python
import atexit
import signal

atexit.register(release_lock)
signal.signal(signal.SIGTERM, lambda *_: (release_lock(), sys.exit(0)))
signal.signal(signal.SIGINT, lambda *_: (release_lock(), sys.exit(0)))
```

The `atexit` handler covers normal exits. Signal handlers cover CTRL+C and system kills.

## Other Safeguards

Beyond PID lockfiles, I added:

1. **Position size validation** — If a position is larger than expected (2x normal), refuse to add more
2. **Duplicate order detection** — Check if an identical order was placed in the last 60 seconds
3. **Balance sanity check** — If available balance is too low (positions already open), skip new entries

Defense in depth. The lockfile prevents the obvious case. These catch the edge cases.

## The Lesson

Every trading bot tutorial focuses on strategy and signals. Nobody talks about operational safety:

- What if it runs twice?
- What if it crashes mid-order?
- What if the exchange connection drops during a close?
- What if the balance fetch fails?

**Your bot will run 24/7. Everything that can go wrong will go wrong at 3 AM when you're asleep.**

Build your bot like it's going to crash. Because it will.

---

*The best feature in a trading bot isn't the entry signal — it's the thing that stops it from doing something stupid at 3 AM.*
