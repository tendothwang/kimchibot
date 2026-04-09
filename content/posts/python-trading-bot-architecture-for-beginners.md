---
title: "Python Trading Bot Architecture: How to Structure Your Code"
date: 2026-04-05T12:00:00
draft: false
tags: ["python", "architecture", "trading-bot", "tutorial", "beginner"]
categories: ["Guide"]
summary: "Most trading bot tutorials show you the strategy but not the structure. Here's how to organize a production-ready trading bot in Python."
---

## The Problem With Tutorials

Every "build a trading bot" tutorial gives you a single Python file with everything crammed in: connection, data fetching, signals, orders, and a while loop.

This works for learning. It doesn't work for production.

When your bot runs 24/7 with real money, you need:
- Clean separation of concerns
- State persistence across restarts
- Error handling at every level
- Logging you can actually debug with

## The Architecture

Here's how I structure my trading bots:

```
bot/
├── bot_main.py          # Main loop and orchestration
├── config.py            # All parameters in one place
├── exchange_client.py   # Exchange connection and API calls
├── signals.py           # Entry/exit signal detection
├── position_manager.py  # Position tracking and state
├── order_manager.py     # Order placement and management
├── state.json           # Persistent state file
└── logs/
    └── bot_2026-04-05.log
```

Let me walk through each piece.

## 1. Config: One Source of Truth

```python
# config.py

# Exchange
API_KEY = os.environ['BINANCE_API_KEY']
SECRET = os.environ['BINANCE_SECRET']

# Strategy parameters
LEVERAGE = 3
TRADE_PCT = 0.80          # Use 80% of balance
TOP_N = 8                 # Number of coins to trade

# Entry
MIN_BODY_PCT = 0.007      # 0.7% candle body
LONG_VR = 1.8             # Volume ratio for longs
SHORT_VR = 1.5            # Volume ratio for shorts
CHOP_THRESHOLD = 50       # Choppiness index

# Exit
SL_PCT = 0.02             # 2% stop loss
TRAIL_ACTIVATE = 0.02     # 2% trailing activation
TRAIL_STOP = 0.005        # 0.5% trailing stop
SURGE_THRESHOLD = 0.04    # 4% surge detection

# Timing
SCAN_INTERVAL = 10        # seconds between checks
COIN_ROTATE_HOURS = 3     # coin rotation interval
```

**Why this matters:** When you want to change a parameter, you change it in one place. No hunting through 500 lines of code to find where `0.02` appears.

## 2. Exchange Client: Wrap the API

```python
# exchange_client.py

class ExchangeClient:
    def __init__(self):
        self.exchange = ccxt.binance({...})
        self.exchange.load_time_difference()
    
    def get_candles(self, symbol, timeframe='5m', limit=100):
        """Fetch OHLCV with retry logic."""
        for attempt in range(3):
            try:
                return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            except ccxt.NetworkError:
                time.sleep(2 ** attempt)
        return None
    
    def get_balance(self):
        """Get available USDT balance."""
        try:
            bal = self.exchange.fetch_balance()
            return float(bal['USDT']['free'])
        except Exception as e:
            log.error(f"Balance fetch failed: {e}")
            return None
    
    def place_market_order(self, symbol, side, amount):
        """Place market order with error handling."""
        try:
            order = self.exchange.create_order(
                symbol, 'market', side, amount
            )
            log.info(f"Order filled: {side} {amount} {symbol} @ {order['average']}")
            return order
        except ccxt.InsufficientFunds:
            log.error(f"Insufficient funds for {symbol}")
            return None
        except Exception as e:
            log.error(f"Order failed: {e}")
            return None
```

**Why wrap it?** Every API call gets retry logic and error handling automatically. Your strategy code stays clean.

## 3. Signals: Pure Logic, No Side Effects

```python
# signals.py

def check_entry(df, side='long'):
    """Check entry conditions. Returns True/False.
    
    This function has NO side effects — no API calls,
    no state changes, no logging. Just math.
    """
    last = df.iloc[-1]
    
    body_pct = abs(last['close'] - last['open']) / last['open']
    
    if side == 'long':
        return (
            body_pct >= config.MIN_BODY_PCT
            and last['close'] > last['open']
            and last['vol_ratio'] >= config.LONG_VR
            and last['chop'] < config.CHOP_THRESHOLD
        )
    else:
        return (
            body_pct >= config.MIN_BODY_PCT
            and last['close'] < last['open']
            and last['vol_ratio'] >= config.SHORT_VR
            and last['chop'] < config.CHOP_THRESHOLD
        )

def check_trailing_exit(position, current_price):
    """Check if trailing stop should trigger."""
    if position.best_price is None:
        return False
    
    if position.side == 'long':
        trail_pct = (position.best_price - current_price) / position.best_price
    else:
        trail_pct = (current_price - position.best_price) / position.best_price
    
    return trail_pct >= config.TRAIL_STOP
```

**Why pure functions?** They're easy to test. You can unit test signals without connecting to an exchange. You can backtest by feeding them historical data.

## 4. Position Manager: State That Survives Restarts

```python
# position_manager.py

import json

class PositionManager:
    def __init__(self, state_file='state.json'):
        self.state_file = state_file
        self.positions = {}
        self.load()
    
    def load(self):
        """Load state from disk."""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.positions = data.get('positions', {})
        except FileNotFoundError:
            self.positions = {}
    
    def save(self):
        """Save state to disk. Called after EVERY change."""
        with open(self.state_file, 'w') as f:
            json.dump({'positions': self.positions}, f, indent=2)
    
    def add_position(self, symbol, side, entry_price, size, sl_order_id):
        """Record a new position."""
        self.positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'size': size,
            'sl_order_id': sl_order_id,
            'best_price': entry_price,
            'entry_time': datetime.now().isoformat(),
        }
        self.save()  # Immediately persist
    
    def remove_position(self, symbol):
        """Remove a closed position."""
        if symbol in self.positions:
            del self.positions[symbol]
            self.save()
    
    def update_best_price(self, symbol, price):
        """Update best price for trailing stop."""
        pos = self.positions.get(symbol)
        if pos:
            if pos['side'] == 'long' and price > pos['best_price']:
                pos['best_price'] = price
                self.save()
            elif pos['side'] == 'short' and price < pos['best_price']:
                pos['best_price'] = price
                self.save()
```

**Why save after every change?** Because your bot will crash at the worst possible moment. If it crashes between opening a position and saving state, it forgets the position exists on restart.

## 5. Main Loop: The Orchestrator

```python
# bot_main.py

def main():
    # Initialize
    client = ExchangeClient()
    positions = PositionManager()
    acquire_pid_lock()
    
    log.info("Bot started")
    
    # Sync with exchange on startup
    sync_positions_with_exchange(client, positions)
    
    while True:
        try:
            for symbol in active_coins:
                # Check existing positions
                if symbol in positions.positions:
                    handle_exit(client, positions, symbol)
                
                # Check for new entries
                elif can_open_new_position(positions):
                    handle_entry(client, positions, symbol)
            
            # Rotate coins periodically
            if should_rotate_coins():
                active_coins = select_best_coins(client)
            
            time.sleep(config.SCAN_INTERVAL)
        
        except KeyboardInterrupt:
            log.info("Shutdown requested")
            break
        except Exception as e:
            log.error(f"Main loop error: {e}")
            time.sleep(30)

if __name__ == '__main__':
    main()
```

## 6. Logging: Your Black Box Recorder

```python
import logging

log = logging.getLogger('bot')
log.setLevel(logging.INFO)

# File handler — one file per day
handler = logging.FileHandler(
    f'logs/bot_{datetime.now().strftime("%Y-%m-%d")}.log'
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
log.addHandler(handler)

# Console handler
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
log.addHandler(console)
```

**Log everything:**
```
2026-04-05 14:32:15 [INFO] Signal: LONG SIREN/USDT body=0.82% VR=2.1 CHOP=43
2026-04-05 14:32:16 [INFO] Order filled: buy 1000 SIREN/USDT @ 0.0523
2026-04-05 14:32:16 [INFO] SL placed at 0.0512 (2.0%)
2026-04-05 14:47:15 [INFO] Trail activated: SIREN/USDT best=0.0545 (+4.2%)
2026-04-05 14:52:15 [INFO] Trail exit: SIREN/USDT @ 0.0541 (+3.4%)
```

When something goes wrong at 3 AM, these logs are your only evidence.

## The Anti-Patterns

Things I did wrong before arriving at this structure:

### 1. Global State Everywhere
```python
# BAD — who modified this? when? why?
current_position = None
best_price = 0
sl_order_id = None
```

Use a PositionManager class instead. State changes are explicit and logged.

### 2. API Calls Inside Signal Logic
```python
# BAD — signals should be pure math
def check_signal():
    price = exchange.fetch_ticker(symbol)['last']  # API call here!
    if price > threshold:
        exchange.create_order(...)  # And an order here?!
```

Fetch data → Calculate signals → Execute orders. Three separate steps.

### 3. No Error Recovery
```python
# BAD — one error kills the whole bot
while True:
    df = exchange.fetch_ohlcv(symbol)  # Network error = crash
    process(df)
```

Wrap every external call in try/except. Log the error. Continue.

## Start Simple, Add Complexity

You don't need all of this on day one. Start with:

1. A single file with the main loop
2. Add config separation
3. Add state persistence
4. Add proper logging
5. Split into modules

Each step makes the bot more maintainable and debuggable. But don't over-architect before you have a working strategy.

---

*Good architecture doesn't make a bad strategy profitable. But bad architecture will definitely make a good strategy unprofitable.*
