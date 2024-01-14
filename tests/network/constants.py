__all__ = [
    "DB_NAME",
    "DB_URL",
    "DEFAULT_EXCHANGER_NAME",
    "DEFAULT_QUEUE",
    "PROCESSING_SERVER_URL",
    "RABBITMQ_URL"
]

# mongodb://localhost:6701/ocrd_network_test
DB_NAME: str = "ocrd_network_test"
DB_URL: str = "mongodb://0.0.0.0:6701"

DEFAULT_EXCHANGER_NAME: str = "ocrd-network-default"
DEFAULT_QUEUE: str = "ocrd-network-default"

PROCESSING_SERVER_URL: str = "http://0.0.0.0:8000"
RABBITMQ_URL: str = "amqp://network_test:network_test@0.0.0.0:6672/"
