from tests.network.config import test_config

pytest_plugins = [
    "tests.network.fixtures_mongodb",
    "tests.network.fixtures_processing_requests",
    "tests.network.fixtures_rabbitmq"
]

test_config.add("DB_NAME", description="...", default=(True, 'ocrd_network_test'))
test_config.add("DB_URL", description="...", default=(True, 'mongodb://network_test:network_test@0.0.0.0:27017'))

test_config.add('DEFAULT_EXCHANGER_NAME', description="...", default=(True, 'ocrd-network-default'))
test_config.add('DEFAULT_QUEUE', description="...", default=(True, 'ocrd-network-default'))

test_config.add('PROCESSING_SERVER_URL', description="...", default=(True, "http://0.0.0.0:8000"))
test_config.add('RABBITMQ_URL', description="...", default=(True, "amqp://network_test:network_test@0.0.0.0:5672/"))
