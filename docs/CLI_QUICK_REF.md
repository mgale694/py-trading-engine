# CLI Quick Reference Card

## 🚀 Installation

```bash
uv pip install typer rich
```

## 📋 Commands

### Help

```bash
python main.py --help                    # Main help
python main.py server --help             # Server help
python main.py simulated-traders --help  # Traders help
```

### Servers

```bash
python main.py server OBS                # Order Book Server
python main.py server TES                # Trading Engine Server
```

### Clients

```bash
python main.py client trader             # Interactive trader client
```

### Frontends

```bash
python main.py frontend trader           # Trader Portal (port 8501)
python main.py frontend analytics        # Analytics Dashboard (port 8502)
```

### Dev Tools

```bash
python main.py init-mock-data            # Load test data
python main.py simulated-traders 5       # Start 5 bots
```

## 🎯 Common Workflows

### Full System Test

```bash
# Terminal 1
python main.py server OBS

# Terminal 2
python main.py server TES

# Terminal 3
python main.py simulated-traders 5

# Terminal 4
python main.py frontend analytics
```

### Quick Dev Setup

```bash
./scripts/setup_dev.sh
python main.py server OBS &
python main.py server TES &
python main.py simulated-traders 3
```

### Reset Environment

```bash
rm src/database/**/*.db
python main.py init-mock-data
```

## 🎨 Visual Features

- **Panels:** Server startup, mock data info
- **Tables:** Trader statistics (updates every 30s)
- **Progress:** Spinners for long operations
- **Colors:** Cyan=servers, Green=success, Red=errors, Yellow=warnings
- **Status:** 🟢 Running, 🔴 Stopped

## 🔧 Options

### Environment

```bash
python main.py server OBS --env dev      # Development
python main.py server TES --env prod     # Production
export ENV=prod                          # Set globally
```

## ⚡ Tips

1. Use `--help` on any command for details
2. Ctrl+C gracefully stops simulated traders
3. Tables show response rates and totals
4. Progress spinners show operation status
5. Rich logging provides better tracebacks

## 📚 Documentation

- [Main README](../README.md) - System overview
- [Dev Mode Guide](../DEV_MODE.md) - Development features
- [CLI Guide](./CLI_GUIDE.md) - Detailed CLI documentation
- [Before/After](./CLI_BEFORE_AFTER.md) - Migration guide
