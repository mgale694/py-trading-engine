"""Configuration for Trading Engine Server."""

RABBITMQ_HOST = "localhost"
TES_QUEUE = "tes_requests"
TES_RESPONSE_QUEUE = "tes_responses"
OBS_QUEUE = "obs_requests"
OBS_RESPONSE_QUEUE = "obs_responses"

# Server settings
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY = 3
