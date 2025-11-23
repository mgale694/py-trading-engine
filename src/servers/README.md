# Servers

This directory contains the core server components of the trading system.

## Structure

```
servers/
├── tes/                 # Trading Engine Server
│   ├── server.py       # Main TES server
│   ├── config.py       # TES configuration
│   ├── routes/         # API routes (FastAPI)
│   ├── services/       # Business logic
│   └── models/         # Pydantic models
│
└── obs/                 # Order Book Server
    ├── server.py       # Main OBS server
    ├── config.py       # OBS configuration
    ├── routes/         # API routes (FastAPI)
    ├── services/       # Business logic (matching, PnL)
    ├── models/         # Pydantic models
    └── strategy/       # Trading strategies
        └── basic.py
```

## Trading Engine Server (TES)

The Trading Engine Server handles:

- Client registration and authentication
- Portfolio management
- Routing trading actions to OBS
- Trade confirmation and client notifications

### Running TES

```bash
python main.py -s TES
```

## Order Book Server (OBS)

The Order Book Server manages:

- Order book maintenance
- Order matching logic
- Trading strategy execution
- Trade recording to KDB+

### Running OBS

```bash
python main.py -s OBS
```

## Communication

Both servers communicate via RabbitMQ message queues:

- `tes_requests`: Trader → TES
- `obs_requests`: TES → OBS
- Responses use dedicated callback queues

## Future Enhancements

- [ ] Convert to FastAPI REST APIs
- [ ] Add WebSocket support for real-time updates
- [ ] Implement comprehensive logging and monitoring
- [ ] Add rate limiting and authentication
- [ ] Implement circuit breakers for fault tolerance
