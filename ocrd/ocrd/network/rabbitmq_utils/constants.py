import logging
from pkg_resources import resource_filename
import tomli

__all__ = [
    "DEFAULT_EXCHANGER_NAME",
    "DEFAULT_EXCHANGER_TYPE",
    "DEFAULT_QUEUE",
    "DEFAULT_ROUTER",
    "RABBIT_MQ_HOST",
    "RABBIT_MQ_PORT",
    "RABBIT_MQ_VHOST",
    "RECONNECT_WAIT",
    "RECONNECT_TRIES",
    "PREFETCH_COUNT",
    "LOG_FORMAT",
    "LOG_LEVEL"
]

TOML_FILENAME: str = resource_filename(__name__, 'config.toml')
TOML_FD = open(TOML_FILENAME, mode='rb')
TOML_CONFIG = tomli.load(TOML_FD)
TOML_FD.close()

DEFAULT_EXCHANGER_NAME: str = TOML_CONFIG["default_exchange_name"]
DEFAULT_EXCHANGER_TYPE: str = TOML_CONFIG["default_exchange_type"]
DEFAULT_QUEUE: str = TOML_CONFIG["default_queue"]
DEFAULT_ROUTER: str = TOML_CONFIG["default_router"]

# "rabbit-mq-host" when Dockerized
RABBIT_MQ_HOST: str = TOML_CONFIG["rabbit_mq_host"]
RABBIT_MQ_PORT: int = TOML_CONFIG["rabbit_mq_port"]
RABBIT_MQ_VHOST: str = TOML_CONFIG["rabbit_mq_vhost"]

# Wait seconds before next reconnect try
RECONNECT_WAIT: int = 5
# Reconnect tries before timeout
RECONNECT_TRIES: int = 3
# QOS, i.e., how many messages to consume in a single go
# Check here: https://www.rabbitmq.com/consumer-prefetch.html
PREFETCH_COUNT: int = 1

# TODO: Integrate the OCR-D Logger once the logging in OCR-D is improved/optimized
LOG_FORMAT: str = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'
LOG_LEVEL: int = logging.WARNING
