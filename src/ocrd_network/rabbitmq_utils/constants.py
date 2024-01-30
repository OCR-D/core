__all__ = [
    'DEFAULT_EXCHANGER_NAME',
    'DEFAULT_EXCHANGER_TYPE',
    'DEFAULT_QUEUE',
    'DEFAULT_ROUTER',
    'RABBIT_MQ_HOST',
    'RABBIT_MQ_PORT',
    'RABBIT_MQ_VHOST',
    'RECONNECT_WAIT',
    'RECONNECT_TRIES',
    'PREFETCH_COUNT',
]

DEFAULT_EXCHANGER_NAME: str = 'ocrd-network-default'
DEFAULT_EXCHANGER_TYPE: str = 'direct'
DEFAULT_QUEUE: str = 'ocrd-network-default'
DEFAULT_ROUTER: str = 'ocrd-network-default'

# 'rabbit-mq-host' when Dockerized
RABBIT_MQ_HOST: str = 'localhost'
RABBIT_MQ_PORT: int = 5672
RABBIT_MQ_VHOST: str = '/'

# Wait seconds before next reconnect try
RECONNECT_WAIT: int = 5
# Reconnect tries before timeout
RECONNECT_TRIES: int = 3
# QOS, i.e., how many messages to consume in a single go
# Check here: https://www.rabbitmq.com/consumer-prefetch.html
PREFETCH_COUNT: int = 1
