# Database Layer

This directory contains all database-related code organized by purpose.

## Structure

```
database/
├── transactional/      # ACID-compliant operational database
│   ├── manager.py      # Database connection manager
│   ├── models.py       # Schema definitions
│   └── migrations/     # Database migrations
│
├── historical/         # Time-series data (KDB+)
│   ├── kdb_client.py   # KDB+ client wrapper
│   ├── schemas.q       # KDB+ table schemas
│   └── queries.py      # Pre-built KDB+ queries
│
├── analytics/          # Aggregated analytics database
│   ├── aggregations.py # Analytics database manager
│   └── metrics.py      # Metric calculations
│
└── utilities/          # Reference data and configuration
    └── model_params.py # Model parameters manager
```

## Database Separation Strategy

### Transactional Database (PostgreSQL/SQLite)

**Purpose:** Core operational data with ACID guarantees

**Tables:**

- `users` - User accounts and authentication
- `orders` - Order records
- `trades` - Executed trades
- `portfolios` - Portfolio definitions
- `positions` - Current positions
- `clients` - Client registration

**Access Pattern:** High write throughput, OLTP queries

### Historical Database (KDB+/q)

**Purpose:** High-performance time-series data storage

**Tables:**

- `trade` - Trade ticks
- `quote` - Market quotes (bid/ask)
- `orderbook_snapshot` - Order book snapshots
- `market_depth` - Market depth data

**Access Pattern:** Write-intensive streaming, time-based analytics

### Analytics Database (PostgreSQL + TimescaleDB)

**Purpose:** Pre-aggregated metrics and reports

**Tables:**

- `daily_pnl` - Daily P&L snapshots
- `trader_metrics` - Trader performance metrics
- `system_performance` - System health metrics
- `trade_analytics` - Trade execution analytics

**Access Pattern:** Read-heavy analytical queries

### Utilities Database (PostgreSQL/Redis)

**Purpose:** Configuration and reference data

**Tables:**

- `model_params` - Model configuration parameters
- `instruments` - Trading instrument definitions
- `holidays` - Trading calendar
- `risk_limits` - Risk management limits
- `feature_flags` - Feature toggles

**Access Pattern:** Read-heavy with caching

## Initialization

### Transactional Database

```bash
python src/database/transactional/manager.py
```

### KDB+ Database

```bash
# Start KDB+ process
q src/database/historical/schemas.q -p 8080

# Or in q session
\l src/database/historical/schemas.q
```

### Analytics Database

```bash
python src/database/analytics/aggregations.py
```

### Utilities Database

```bash
python src/database/utilities/model_params.py
```

## Connection Management

Each database module provides its own connection manager:

```python
from database.transactional import TransactionalDB
from database.historical import KDBClient
from database.analytics import AnalyticsDB
from database.utilities import ModelParamsDB

# Transactional
trans_db = TransactionalDB()
trans_db.place_order(user_id=1, symbol="AAPL", side="buy", quantity=100, price=150.0)

# Historical
kdb = KDBClient(host='localhost', port=8080)
kdb.insert_trade(trade_data)

# Analytics
analytics = AnalyticsDB()
analytics.insert_daily_pnl(user_id=1, date='2025-11-23', realized_pnl=100, unrealized_pnl=50, total_pnl=150)

# Utilities
utils = ModelParamsDB()
utils.set_param('strategy', 'max_position_size', 1000)
```

## Best Practices

1. **Use connection pooling** for high-throughput scenarios
2. **Separate read and write operations** where possible
3. **Use transactions** for multi-step operations
4. **Implement retry logic** for transient failures
5. **Monitor database performance** and optimize queries
6. **Regular backups** especially for transactional data
7. **Archive historical data** based on retention policies
