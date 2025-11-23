# Development Mode - Quick Reference

## Overview

Development mode provides automated tools for testing and development:

- **Mock Data Generator**: Populate databases with realistic test data
- **Simulated Traders**: Automated bots that place random orders

## 🚀 Quick Start

### One-Command Setup

```bash
./scripts/setup_dev.sh
```

This initializes all databases and loads mock data.

### Manual Setup

```bash
# 1. Initialize databases with mock data
python main.py --init-mock-data

# 2. Start servers
python main.py -s OBS    # Terminal 1
python main.py -s TES    # Terminal 2

# 3. Start simulated traders
python main.py --simulated-traders 5    # Terminal 3
```

---

## 📊 Mock Data Generator

### What It Creates

| Data Type       | Count    | Description                             |
| --------------- | -------- | --------------------------------------- |
| **Users**       | 20       | Mock trader accounts                    |
| **Orders**      | 100      | Historical orders (various statuses)    |
| **Trades**      | 50       | Executed trades                         |
| **Instruments** | 10       | Trading instruments (AAPL, GOOGL, etc.) |
| **Positions**   | 40-60    | User positions across symbols           |
| **Analytics**   | 10 users | Performance metrics and PnL data        |

### Symbols Available (Dev Mode)

- `AAPL` - Apple Inc. ($150-$200)
- `GOOGL` - Alphabet Inc. ($130-$180)
- `MSFT` - Microsoft Corp. ($350-$450)
- `TSLA` - Tesla Inc. ($200-$300)
- `AMZN` - Amazon.com Inc. ($140-$180)
- `META` - Meta Platforms ($300-$400)
- `NVDA` - NVIDIA Corp. ($450-$550)
- `JPM` - JPMorgan Chase ($140-$180)
- `BAC` - Bank of America ($30-$45)
- `WMT` - Walmart Inc. ($150-$180)

### Initialize Mock Data

```bash
# Initialize all databases with mock data
python main.py --init-mock-data
```

**What happens:**

1. Creates 20 test users with usernames like `Alice123`, `Bob456`
2. Generates 100 historical orders across all symbols
3. Records 50 executed trades
4. Populates instrument definitions in utilities DB
5. Creates analytics data (PnL, metrics) for first 10 users

**Configuration** (`config/dev.yaml`):

```yaml
dev:
  initialize_mock_data: true
  mock_data:
    num_users: 20
    num_orders: 100
    num_trades: 50
    time_spread_hours: 24
```

### Customize Mock Data

Edit `src/shared/mock_data.py`:

```python
# Add more symbols
DEV_SYMBOLS = ['AAPL', 'GOOGL', 'YOUR_SYMBOL']

# Adjust price ranges
SYMBOL_PRICES = {
    'YOUR_SYMBOL': (min_price, max_price, tick_size)
}
```

---

## 🤖 Simulated Traders

### What They Do

Simulated traders are automated bots that:

- Connect to the TES via RabbitMQ
- Place random buy/sell orders
- Trade across configured symbols
- Run continuously until stopped

### Start Simulated Traders

```bash
# Start 5 simulated traders
python main.py --simulated-traders 5

# Start 10 traders
python main.py --simulated-traders 10
```

### Behavior

Each simulated trader:

- Places orders every ~5 seconds (configurable)
- Randomly selects symbol from dev symbols
- Randomly chooses buy or sell
- Random quantity: 10, 25, 50, 100, 150, or 200 shares
- Random price within symbol's range
- Connects via RabbitMQ like a real client

### Statistics

Traders print statistics every 30 seconds:

```
===========================================================
SIMULATED TRADERS STATISTICS
===========================================================
SimTrader_1     🟢 Running    Orders: 45    Responses: 45
SimTrader_2     🟢 Running    Orders: 43    Responses: 43
SimTrader_3     🟢 Running    Orders: 47    Responses: 47
SimTrader_4     🟢 Running    Orders: 44    Responses: 44
SimTrader_5     🟢 Running    Orders: 46    Responses: 46
-----------------------------------------------------------
TOTAL           Active: 5     Orders: 225   Responses: 225
===========================================================
```

### Configuration

Edit `config/dev.yaml`:

```yaml
dev:
  enable_simulated_traders: true
  simulated_traders:
    count: 5 # Default number of traders
    trade_frequency: 5.0 # Seconds between trades (average)
    symbols: # Symbols to trade
      - AAPL
      - GOOGL
      - MSFT
      - TSLA
      - AMZN
```

### Customize Behavior

Edit `src/clients/simulated_traders.py`:

```python
# Adjust trade frequency
trade_frequency = 10.0  # Slower: 10 seconds between trades

# Change quantity distribution
quantity = random.choice([50, 100, 200, 500])

# Modify price logic
price = round(random.uniform(min_price, max_price), 2)
```

---

## 🎛️ Configuration

### Environment Variable

```bash
# Set environment
export ENV=dev    # Enable dev features
export ENV=prod   # Disable dev features
```

### Config Files

**`config/dev.yaml`** - Development settings

```yaml
dev:
  initialize_mock_data: true # Auto-load mock data
  enable_simulated_traders: true # Allow simulated traders
  mock_data:
    num_users: 20
    num_orders: 100
    num_trades: 50
  simulated_traders:
    count: 5
    trade_frequency: 5.0
    symbols: [AAPL, GOOGL, MSFT, TSLA, AMZN]
```

**`config/prod.yaml`** - Production settings

```yaml
dev:
  initialize_mock_data: false # Disable mock data
  enable_simulated_traders: false # Disable simulated traders
```

---

## 📋 Common Workflows

### Full System Test with Simulated Load

```bash
# Terminal 1: Order Book Server
python main.py -s OBS

# Terminal 2: Trading Engine Server
python main.py -s TES

# Terminal 3: Simulated Traders (5 bots)
python main.py --simulated-traders 5

# Terminal 4: Analytics Dashboard (monitor activity)
python main.py --frontend analytics
```

### Reset and Reload Data

```bash
# 1. Stop all services
# Ctrl+C in all terminals

# 2. Delete databases
rm src/database/transactional/trading_engine.db
rm src/database/analytics/analytics.db
rm src/database/utilities/utilities.db

# 3. Reinitialize with fresh mock data
./scripts/setup_dev.sh

# 4. Restart services
```

### Test Specific Scenario

```bash
# 1. Initialize with custom mock data
python main.py --init-mock-data

# 2. Start servers
python main.py -s OBS &
python main.py -s TES &

# 3. Run specific number of simulated traders
python main.py --simulated-traders 3

# 4. Monitor with manual client
python main.py -c trader
```

---

## 🔧 Troubleshooting

### Mock Data Already Exists

```
ERROR: User alice123 might already exist
```

**Solution:** Delete database files and reinitialize

```bash
rm src/database/transactional/trading_engine.db
python main.py --init-mock-data
```

### Simulated Traders Won't Start

```
ERROR: Failed to connect to RabbitMQ
```

**Solution:** Ensure RabbitMQ is running

```bash
brew services start rabbitmq
# Wait 5 seconds, then retry
```

### Orders Not Being Matched

```
Simulated traders sending orders but no trades executing
```

**Solution:** Ensure both OBS and TES are running

```bash
# Check if both are running
ps aux | grep "main.py"
```

### Too Much Load

```
System is slow with many simulated traders
```

**Solution:** Reduce trader count or trade frequency

```bash
# Fewer traders
python main.py --simulated-traders 2

# Or edit config/dev.yaml
trade_frequency: 10.0  # Slower trades
```

---

## 🎯 Best Practices

1. **Always start OBS before TES**
   - TES connects to OBS on startup
2. **Initialize mock data before first run**
   - Provides realistic data for testing
3. **Start with fewer simulated traders**
   - Test with 2-3 traders first
   - Scale up as needed
4. **Monitor with analytics dashboard**
   - Real-time visibility into system behavior
5. **Use dev environment only**
   - Mock data and simulated traders are dev-only features
   - Production environment disables these automatically

---

## 📚 Related Documentation

- [Main README](../README.md) - System overview
- [Servers README](../src/servers/README.md) - TES and OBS details
- [Database README](../src/database/README.md) - Database architecture
- [Clients README](../src/clients/README.md) - Client implementation

---

## 🎉 Quick Test

Try this 1-minute test:

```bash
# Terminal 1
python main.py --init-mock-data
python main.py -s OBS

# Terminal 2
python main.py -s TES

# Terminal 3
python main.py --simulated-traders 3
```

Watch the simulated traders place orders! 🚀
