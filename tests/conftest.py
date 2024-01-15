from ocrd_network.database import sync_initiate_database
from ocrd_utils.config import config


pytest_plugins = [
    "tests.network.fixtures_mongodb",
    "tests.network.fixtures_rabbitmq"
]

config.add("DB_NAME", description="...", default=(True, 'ocrd'))
config.add("DB_URL", description="...", default=(True, 'mongodb://network_test:network_test@0.0.0.0:6701'))

config.add('DEFAULT_EXCHANGER_NAME', description="...", default=(True, 'ocrd-network-default'))
config.add('DEFAULT_QUEUE', description="...", default=(True, 'ocrd-network-default'))

config.add('PROCESSING_SERVER_URL', description="...", default=(True, "http://0.0.0.0:8000"))
config.add('RABBITMQ_URL', description="...", default=(True, "amqp://network_test:network_test@0.0.0.0:6672/"))

sync_initiate_database(config.DB_URL, config.DB_NAME)
