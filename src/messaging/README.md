# Messaging Layer

RabbitMQ-based messaging infrastructure for inter-service communication.

## Structure

```
messaging/
├── broker.py           # RabbitMQ connection manager
├── publishers.py       # Message publishers
├── consumers.py        # Message consumers
└── schemas.py          # Message schemas
```

## Overview

This module provides a clean abstraction over RabbitMQ for reliable message-based communication between services.

## Components

### Message Broker (`broker.py`)

Manages RabbitMQ connections and channels.

```python
from messaging import MessageBroker

# Create and connect
broker = MessageBroker(host='localhost', port=5672)
broker.connect()

# Declare queues
broker.declare_queue('orders', durable=True)

# Declare exchanges
broker.declare_exchange('trade_events', exchange_type='fanout')

# Clean up
broker.close()
```

### Publishers (`publishers.py`)

Send messages to queues.

```python
from messaging import MessagePublisher, OrderPublisher

# Generic publisher
publisher = MessagePublisher(broker)
publisher.publish('my_queue', {'action': 'test', 'data': 123})

# Specialized order publisher
order_pub = OrderPublisher(broker)
order_pub.publish_order({
    'user_id': 1,
    'symbol': 'AAPL',
    'side': 'buy',
    'quantity': 100,
    'price': 150.0
})
```

### Consumers (`consumers.py`)

Receive and process messages from queues.

```python
from messaging import MessageConsumer

consumer = MessageConsumer(broker)

# Register handler
def handle_order(message, properties):
    print(f"Received order: {message}")
    return {'status': 'ok', 'message': 'Order processed'}

consumer.register_handler('place_order', handle_order)

# Start consuming
consumer.start_consuming('order_queue')
```

### RPC Pattern (`consumers.py`)

Request-reply pattern for synchronous communication.

```python
from messaging import RPCConsumer

rpc = RPCConsumer(broker)

# Make RPC call
response = rpc.call(
    queue_name='obs_requests',
    message={'action': 'get_orderbook', 'symbol': 'AAPL'},
    timeout=5
)
print(response)
```

## Message Schemas (`schemas.py`)

TypedDict schemas for type safety:

```python
from messaging.schemas import OrderMessage, TradeMessage

order: OrderMessage = {
    'action': 'place_order',
    'user_id': 1,
    'symbol': 'AAPL',
    'side': 'buy',
    'quantity': 100.0,
    'price': 150.0,
    'order_type': 'limit',
    'timestamp': 1234567890.0
}
```

## Queue Architecture

### Current Queues

| Queue           | Purpose             | Producer     | Consumer     |
| --------------- | ------------------- | ------------ | ------------ |
| `tes_requests`  | Trader → TES        | TraderClient | TES          |
| `tes_responses` | TES → Trader        | TES          | TraderClient |
| `obs_requests`  | TES → OBS           | TES          | OBS          |
| `obs_responses` | OBS → TES           | OBS          | TES          |
| `trade_events`  | Trade notifications | OBS          | Analytics    |

### Exchange Patterns

**Direct Exchange** (default)

- Point-to-point communication
- Used for request-response patterns

**Topic Exchange** (planned)

- Publish-subscribe with routing
- For trade events, market data

**Fanout Exchange** (planned)

- Broadcast to all subscribers
- For system notifications

## Best Practices

1. **Always use context managers** for automatic cleanup:

```python
with MessageBroker(host='localhost') as broker:
    publisher = MessagePublisher(broker)
    publisher.publish('my_queue', {'data': 'test'})
```

2. **Use correlation IDs** for request-reply patterns
3. **Set proper message persistence** for critical messages
4. **Implement retry logic** with exponential backoff
5. **Use dead letter queues** for failed messages
6. **Monitor queue depths** to detect bottlenecks
7. **Use acknowledgments** to ensure reliable delivery

## Error Handling

```python
try:
    publisher.publish('my_queue', message)
except Exception as e:
    logger.error(f"Failed to publish message: {e}")
    # Implement retry or dead letter logic
```

## Monitoring

Use RabbitMQ Management UI:

```bash
# Access at http://localhost:15672
# Default credentials: guest/guest
```

Key metrics to monitor:

- Queue depth
- Message rates (publish/deliver)
- Consumer count
- Unacknowledged messages

## Future Enhancements

- [ ] Message encryption for sensitive data
- [ ] Message compression for large payloads
- [ ] Priority queues for urgent orders
- [ ] Delayed message delivery
- [ ] Message deduplication
- [ ] Distributed tracing integration
