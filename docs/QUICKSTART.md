# Quick Start Guide

Get the trading system up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check if RabbitMQ is installed
brew list | grep rabbitmq
# or
which rabbitmq-server

# Optional: Check KDB+
which q
```

## 1. Install Dependencies (2 min)

```bash
# Install Python dependencies
pip install -r requirements/base.txt

# Start RabbitMQ
brew services start rabbitmq

# Verify RabbitMQ is running
rabbitmqctl status
```

## 2. Initialize Databases (1 min)

```bash
# Run the setup script
./scripts/setup_databases.sh

# Or manually:
python src/database/transactional/manager.py
python src/database/analytics/aggregations.py
python src/database/utilities/model_params.py
```

## 3. Start Services (1 min)

Open **4 terminal windows**:

**Terminal 1: Order Book Server**

```bash
python main.py -s OBS
```

Wait for: `OrderBookServer started. Waiting for client requests...`

**Terminal 2: Trading Engine Server**

```bash
python main.py -s TES
```

Wait for: `TradingEngineServer started. Waiting for client requests...`

**Terminal 3: Trader Portal**

```bash
python main.py --frontend trader
```

Opens browser at: http://localhost:8501

**Terminal 4: Test Client (Optional)**

```bash
python main.py -c trader
```

## 4. Verify Everything Works (1 min)

1. **Check RabbitMQ Management UI**: http://localhost:15672

   - Login: guest/guest
   - You should see queues: `tes_requests`, `obs_requests`

2. **Check Trader Portal**: http://localhost:8501

   - Navigate through Dashboard, Order Entry, Positions

3. **Check Analytics Dashboard**:
   ```bash
   # In a new terminal
   python main.py --frontend analytics
   ```
   - Opens at: http://localhost:8502

## Common Issues & Solutions

### Issue: "Connection refused" for RabbitMQ

**Solution:**

```bash
brew services restart rabbitmq
# Wait 10 seconds
python main.py -s OBS
```

### Issue: Port already in use

**Solution:**

```bash
# Find process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
STREAMLIT_SERVER_PORT=8503 streamlit run src/frontend/trader-portal/app.py
```

### Issue: KDB+ connection errors

**Solution:**

```bash
# KDB+ is optional for basic functionality
# To use KDB+, start it first:
q src/database/historical/schemas.q -p 8080
```

### Issue: Module not found errors

**Solution:**

```bash
# Make sure you're in the project root
cd /Users/mgale/dev/mgale694/py-trading-engine

# Reinstall dependencies
pip install -r requirements/base.txt
```

## Test the System

### Place a Test Order

1. Go to Trader Portal (http://localhost:8501)
2. Click "Order Entry" in sidebar
3. Enter:
   - Symbol: AAPL
   - Side: buy
   - Quantity: 100
   - Price: 150.00
4. Click "Submit Order"

### View in Terminal

Check Terminal 1 (OBS) and Terminal 2 (TES) for log messages about order processing.

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Explore individual module READMEs:
   - [Servers](src/servers/README.md)
   - [Database](src/database/README.md)
   - [Frontend](src/frontend/README.md)
   - [Messaging](src/messaging/README.md)
3. Review [MIGRATION.md](./MIGRATION.md) if migrating existing code
4. Check out the Docker setup: `cd docker && docker-compose up`

## Stopping Services

```bash
# Stop RabbitMQ
brew services stop rabbitmq

# Stop servers: Ctrl+C in each terminal

# Or kill all Python processes
pkill -f "python main.py"
```

## Full Docker Deployment (Alternative)

If you prefer Docker:

```bash
cd docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

Services will be available at:

- Trader Portal: http://localhost:8501
- Analytics: http://localhost:8502
- RabbitMQ UI: http://localhost:15672

## Need Help?

- Check [README.md](README.md) for detailed docs
- Review logs in `logs/` directory
- Check RabbitMQ queues for message flow
- Verify database files exist in `src/database/*/`

Happy Trading! 🚀
