# CLI Guide - Enhanced with Typer and Rich

The trading engine now features a beautiful, modern CLI built with **Typer** and **Rich** for an improved developer experience.

## 🎨 Features

- ✨ **Rich formatting** with colors, tables, and panels
- 📊 **Beautiful statistics** with auto-updating tables
- 🎯 **Clear command structure** with intuitive subcommands
- 💡 **Helpful messages** with emojis and visual hierarchy
- 🚀 **Improved help system** with detailed examples

## 📖 Commands

### Show Help

```bash
python main.py --help
```

### Start Servers

**Order Book Server (OBS)**

```bash
python main.py server OBS
```

**Trading Engine Server (TES)**

```bash
python main.py server TES
```

Help for server command:

```bash
python main.py server --help
```

### Start Clients

**Trader Client**

```bash
python main.py client trader
```

Help for client command:

```bash
python main.py client --help
```

### Start Frontends

**Trader Portal**

```bash
python main.py frontend trader
```

**Analytics Dashboard**

```bash
python main.py frontend analytics
```

Help for frontend command:

```bash
python main.py frontend --help
```

### Development Utilities

**Initialize Mock Data**

```bash
python main.py init-mock-data
```

This displays a beautiful panel showing what data will be created:

- 20 test users with balances
- 100 historical orders
- 50 executed trades
- 10 trading instruments
- Portfolio positions and analytics

**Start Simulated Traders**

```bash
python main.py simulated-traders 5
```

This shows:

- Startup panel with configuration
- Live statistics table updating every 30 seconds
- Color-coded status indicators
- Response rate tracking
- Graceful shutdown with final statistics

Example output:

```
╭─────── 🤖 Simulated Traders ────────╮
│  Starting 5 Simulated Traders       │
│                                      │
│  📊 Trade Frequency: ~5.0s          │
│  📈 Symbols: AAPL, GOOGL, MSFT,     │
│             TSLA, AMZN              │
│  ⏱️  Stats Update: Every 30 seconds │
│                                      │
│  Press Ctrl+C to stop               │
╰──────────────────────────────────────╯
```

Then live statistics:

```
╭───────────── 🤖 Simulated Traders Statistics ──────────────╮
│ Trader        │  Status  │ Orders │ Responses │ Response… │
├───────────────┼──────────┼────────┼───────────┼───────────┤
│ SimTrader_1   │ 🟢 Running │     45 │        45 │   100.0% │
│ SimTrader_2   │ 🟢 Running │     43 │        43 │   100.0% │
│ SimTrader_3   │ 🟢 Running │     47 │        47 │   100.0% │
│ SimTrader_4   │ 🟢 Running │     44 │        44 │   100.0% │
│ SimTrader_5   │ 🟢 Running │     46 │        46 │   100.0% │
├───────────────┼──────────┼────────┼───────────┼───────────┤
│ TOTAL (5      │          │    225 │       225 │   100.0% │
│ active)       │          │        │           │           │
╰───────────────┴──────────┴────────┴───────────┴───────────╯
```

## 🎯 Command Structure

The new CLI uses a clearer command structure:

### Old Style (argparse)

```bash
python main.py -s OBS
python main.py -c trader
python main.py --frontend analytics
python main.py --init-mock-data
python main.py --simulated-traders 5
```

### New Style (typer)

```bash
python main.py server OBS
python main.py client trader
python main.py frontend analytics
python main.py init-mock-data
python main.py simulated-traders 5
```

## 🌈 Visual Improvements

### 1. Rich Logging

All log messages now use Rich's logging handler:

- Color-coded log levels
- Better traceback formatting
- Cleaner timestamps
- No path clutter

### 2. Beautiful Panels

Server startup messages are wrapped in styled panels:

```
╭─────── 🚀 Starting Server ───────╮
│ Trading Engine Server (TES)      │
│ Client management • Portfolio    │
│ tracking • Order routing         │
╰──────────────────────────────────╯
```

### 3. Statistics Tables

Simulated traders show statistics in a proper table:

- Rounded borders
- Color-coded columns
- Status indicators (🟢/🔴)
- Summary row
- Auto-calculated response rates

### 4. Status Indicators

Progress indicators for long operations:

```
⠋ Loading mock data...
⠙ Stopping all traders...
```

## 🔧 Technical Details

### Dependencies Added

```python
typer>=0.9.0      # Modern CLI framework
rich>=13.0.0      # Terminal formatting
```

### Files Modified

1. **main.py** - Refactored with typer commands
2. **src/shared/logging.py** - Added RichHandler support
3. **src/clients/simulated_traders.py** - Rich tables and panels
4. **requirements/base.txt** - Added typer and rich

### Key Changes

**main.py structure:**

```python
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(name="Trading Engine", ...)
console = Console()

@app.command()
def server(name: str, env: str = "dev"):
    """Start a trading server"""
    console.print(Panel(...))
    # Start server

@app.command()
def simulated_traders(count: int, env: str = "dev"):
    """Start simulated traders"""
    console.print(Panel(...))
    # Start traders

if __name__ == "__main__":
    app()
```

## 💡 Tips

1. **Use tab completion** - Typer supports shell completion
2. **Check help for each command** - Every command has detailed help
3. **Use --help anywhere** - Works on main app and all subcommands
4. **Environment variable** - Set `ENV=prod` to use production config
5. **Rich rendering** - Works best in modern terminals with color support

## 🎓 Examples

### Full Development Workflow

```bash
# 1. Initialize data
python main.py init-mock-data

# 2. Start servers (separate terminals)
python main.py server OBS
python main.py server TES

# 3. Start simulated traders
python main.py simulated-traders 5

# 4. Monitor with analytics
python main.py frontend analytics
```

### Quick Test

```bash
# One-liner dev setup
./scripts/setup_dev.sh && python main.py server OBS &
python main.py server TES &
python main.py simulated-traders 3
```

### Production Mode

```bash
export ENV=prod
python main.py server OBS --env prod
python main.py server TES --env prod
```

## 🐛 Troubleshooting

### Packages Not Found

```bash
uv pip install typer rich
```

### Colors Not Showing

Check your terminal supports colors:

```bash
echo $TERM
# Should show something like 'xterm-256color'
```

### Rich Formatting Issues

Disable rich logging if needed:

```python
# In src/shared/logging.py
setup_logger(name='main', use_rich=False)
```

## 📚 Further Reading

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Main README](../README.md)
- [Dev Mode Guide](./DEV_MODE.md)
