"""Configuration for Order Book Server."""

RABBITMQ_HOST = "localhost"
OBS_QUEUE = "obs_requests"
OBS_RESPONSE_QUEUE = "obs_responses"

# Order book settings
MAX_PRICE_LEVELS = 100
TICK_SIZE = 0.01
