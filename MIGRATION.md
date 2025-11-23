# Project Restructure - Migration Guide

## Overview

The trading system has been completely restructured from a monolithic layout to a microservices-oriented architecture with clear separation of concerns.

## Old vs New Structure

### Old Structure

```
src/
├── backend/
│   ├── main.py
│   ├── engine.py
│   ├── clients/
│   ├── config/
│   ├── server/
│   ├── servers/
│   └── strategy/
├── database/
│   └── sqlite_db.py
└── frontend/
    └── app.py
```

### New Structure

```
src/
├── servers/
│   ├── tes/              # Trading Engine Server
│   └── obs/              # Order Book Server
├── database/
│   ├── transactional/    # ACID operations
│   ├── historical/       # KDB+ time-series
│   ├── analytics/        # Aggregated metrics
│   └── utilities/        # Configuration
├── frontend/
│   ├── trader-portal/    # External UI
│   └── analytics/        # Internal dashboard
├── messaging/            # RabbitMQ layer
├── shared/               # Common utilities
└── clients/              # Test clients
```

## Key Changes

### 1. Server Separation

- **Old**: `src/backend/servers/trading_engine.py` and `order_book.py`
- **New**:
  - `src/servers/tes/server.py` (Trading Engine Server)
  - `src/servers/obs/server.py` (Order Book Server)
- **Benefit**: Clear service boundaries, easier to scale independently

### 2. Database Layer

- **Old**: Single `sqlite_db.py` file
- **New**: Multiple specialized databases
  - `transactional/` - Orders, trades, users
  - `historical/` - KDB+ tick data
  - `analytics/` - Pre-aggregated metrics
  - `utilities/` - Configuration and reference data
- **Benefit**: Optimized for different access patterns, better performance

### 3. Messaging Abstraction

- **Old**: Direct pika usage scattered across files
- **New**: Dedicated `messaging/` module with:
  - `broker.py` - Connection management
  - `publishers.py` - Message publishing
  - `consumers.py` - Message consumption
  - `schemas.py` - Type-safe message schemas
- **Benefit**: Cleaner code, easier to test, consistent messaging patterns

### 4. Shared Utilities

- **Old**: `src/backend/config/logger.py`
- **New**: `src/shared/` module with:
  - `logging.py` - Centralized logging
  - `config.py` - Configuration management
  - `models/` - Domain models (Order, Trade, Trader)
- **Benefit**: DRY principle, consistent across services

### 5. Frontend Split

- **Old**: Single `app.py`
- **New**:
  - `trader-portal/app.py` - External trader interface
  - `analytics/app.py` - Internal analytics dashboard
- **Benefit**: Separation of concerns, different audiences

## Import Changes

### Old Imports

```python
from config.logger import setup_logger
from servers.trading_engine import TradingEngineServer
from servers.order_book import OrderBookServer
```

### New Imports

```python
from shared.logging import setup_logger
from servers.tes import TradingEngineServer
from servers.obs import OrderBookServer
from messaging import MessageBroker, MessagePublisher
from shared.models import Order, Trade
```

## Running the System

### Old Way

```bash
python src/backend/main.py -s OBS
python src/backend/main.py -s TES
python src/backend/main.py -c trader
streamlit run src/frontend/app.py
```

### New Way

```bash
python main.py -s OBS
python main.py -s TES
python main.py -c trader
python main.py --frontend trader
python main.py --frontend analytics
```

## Migration Steps for Existing Code

If you have custom code that uses the old structure:

1. **Update imports** to use new module paths
2. **Use messaging layer** instead of direct pika calls
3. **Use shared models** for Order, Trade, Trader
4. **Update database paths** to new locations
5. **Use Config class** for configuration management

## New Features

### Configuration Management

```python
from shared.config import Config

config = Config(env='dev')
rabbitmq_config = config.get_rabbitmq_config()
```

### Messaging Layer

```python
from messaging import MessageBroker, MessagePublisher

with MessageBroker(host='localhost') as broker:
    publisher = MessagePublisher(broker)
    publisher.publish('my_queue', {'data': 'value'})
```

### Domain Models

```python
from shared.models import Order, OrderSide, OrderType

order = Order(
    id="order_123",
    user_id=1,
    symbol="AAPL",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity=100,
    price=150.0
)
```

## Docker Support

New Docker deployment:

```bash
cd docker
docker-compose up -d
```

This starts:

- RabbitMQ
- KDB+
- OBS
- TES
- Trader Portal
- Analytics Dashboard

## Testing

Run the new test suite:

```bash
# All tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test types
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

## Documentation

Each module now has its own README:

- [Servers](src/servers/README.md)
- [Database](src/database/README.md)
- [Frontend](src/frontend/README.md)
- [Messaging](src/messaging/README.md)
- [Shared](src/shared/README.md)

## Questions?

Refer to the main [README.md](README.md) for comprehensive documentation.
