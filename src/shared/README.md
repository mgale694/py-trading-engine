# Shared Utilities

Common code and utilities used across all services.

## Structure

```
shared/
├── logging.py          # Logging configuration
├── config.py           # Configuration management
├── models/             # Shared domain models
│   ├── order.py
│   ├── trade.py
│   └── trader.py
└── utils/              # Helper utilities
```

## Logging

Centralized logging configuration for all services.

### Usage

```python
from shared.logging import setup_logger, get_logger

# Setup logger with file output
logger = setup_logger(
    name='my_service',
    level=logging.INFO,
    log_file='my_service.log',
    log_dir='logs'
)

# Or get existing logger
logger = get_logger('my_service')

logger.info("Service started")
logger.error("An error occurred")
```

### Features

- Console and file output
- Configurable log levels
- Structured log format
- Automatic log directory creation

## Configuration

Flexible configuration management with YAML files and environment variables.

### Usage

```python
from shared.config import Config

# Load configuration
config = Config(env='dev')  # Loads config/dev.yaml

# Access configuration
rabbitmq_config = config.get_rabbitmq_config()
kdb_config = config.get_kdb_config()

# Get specific values
host = config.get('rabbitmq.host', default='localhost')
port = config.get('rabbitmq.port', default=5672)
```

### Configuration Files

Create `config/dev.yaml`:

```yaml
rabbitmq:
  host: localhost
  port: 5672
  username: guest
  password: guest

kdb:
  host: localhost
  port: 8080

database:
  transactional: src/database/transactional/trading_engine.db
  analytics: src/database/analytics/analytics.db
  utilities: src/database/utilities/utilities.db
```

### Environment Variables

Override config with environment variables:

```bash
export RABBITMQ_HOST=rabbitmq.example.com
export KDB_PORT=8888
```

## Domain Models

Shared data models used across services.

### Order Model

```python
from shared.models import Order, OrderSide, OrderType, OrderStatus

order = Order(
    id="order_123",
    user_id=1,
    symbol="AAPL",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity=100.0,
    price=150.0,
    status=OrderStatus.OPEN
)

# Fill order
order.fill(50.0)  # Partially filled

# Convert to dict for JSON serialization
order_dict = order.to_dict()
```

### Trade Model

```python
from shared.models import Trade

trade = Trade(
    id="trade_456",
    buyer_id=1,
    seller_id=2,
    symbol="AAPL",
    quantity=100.0,
    price=150.0,
    buy_order_id="order_123",
    sell_order_id="order_124"
)

# Calculate trade value
value = trade.total_value  # quantity * price

# Convert to dict
trade_dict = trade.to_dict()
```

### Trader Model

```python
from shared.models import Trader

trader = Trader(
    id=1,
    username="trader1",
    email="trader1@example.com",
    full_name="John Doe"
)

# Record login
trader.login()

# Deactivate account
trader.deactivate()

# Convert to dict
trader_dict = trader.to_dict()
```

## Best Practices

### Logging

1. **Use appropriate log levels:**

   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General informational messages
   - `WARNING`: Warning messages for unexpected events
   - `ERROR`: Error messages for serious issues
   - `CRITICAL`: Critical issues requiring immediate attention

2. **Include context in log messages:**

```python
logger.info(f"Processing order {order_id} for user {user_id}")
```

3. **Use structured logging for complex data:**

```python
logger.info("Order placed", extra={
    'order_id': order_id,
    'user_id': user_id,
    'symbol': symbol,
    'quantity': quantity
})
```

### Configuration

1. **Use environment-specific configs:**

   - `dev.yaml` for development
   - `prod.yaml` for production

2. **Never commit secrets** to version control

3. **Use environment variables** for sensitive data

4. **Provide sensible defaults** for optional settings

### Domain Models

1. **Use dataclasses** for clean, immutable-ish data structures

2. **Implement validation** in `__post_init__`

3. **Provide `to_dict()` methods** for serialization

4. **Use Enums** for fixed value sets (OrderSide, OrderStatus)

5. **Include type hints** for better IDE support

## Testing

Test shared utilities:

```python
import pytest
from shared.models import Order, OrderSide

def test_order_creation():
    order = Order(
        id="test_order",
        user_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type="limit",
        quantity=100,
        price=150
    )
    assert order.remaining_quantity == 100

def test_order_fill():
    order = Order(...)
    order.fill(50)
    assert order.filled_quantity == 50
    assert order.remaining_quantity == 50
```

## Future Enhancements

- [ ] Add validation decorators
- [ ] Implement caching utilities
- [ ] Add retry decorators
- [ ] Create performance profiling utilities
- [ ] Add data serialization helpers
- [ ] Implement distributed tracing
