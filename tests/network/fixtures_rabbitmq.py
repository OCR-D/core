from logging import getLogger
from pika.credentials import PlainCredentials
from pytest import fixture
from src.ocrd_network.rabbitmq_utils import (
    connect_rabbitmq_consumer,
    connect_rabbitmq_publisher,
    RMQConnector,
    verify_and_parse_mq_uri
)
from tests.network.config import test_config


RABBITMQ_URL = test_config.RABBITMQ_URL
DEFAULT_EXCHANGER_NAME = test_config.DEFAULT_EXCHANGER_NAME
DEFAULT_QUEUE = test_config.DEFAULT_QUEUE


@fixture(scope="session", name="rabbitmq_defaults")
def fixture_rabbitmq_defaults():
    rmq_data = verify_and_parse_mq_uri(RABBITMQ_URL)
    rmq_username = rmq_data["username"]
    rmq_password = rmq_data["password"]
    rmq_host = rmq_data["host"]
    rmq_port = rmq_data["port"]
    rmq_vhost = rmq_data["vhost"]

    test_connection = RMQConnector.open_blocking_connection(
        credentials=PlainCredentials(rmq_username, rmq_password),
        host=rmq_host,
        port=rmq_port,
        vhost=rmq_vhost
    )
    test_channel = RMQConnector.open_blocking_channel(test_connection)
    assert test_channel
    RMQConnector.exchange_declare(
        channel=test_channel,
        exchange_name=DEFAULT_EXCHANGER_NAME,
        exchange_type="direct",
        durable=False
    )
    RMQConnector.queue_declare(channel=test_channel, queue_name=DEFAULT_QUEUE, durable=False)
    RMQConnector.queue_bind(
        channel=test_channel,
        exchange_name=DEFAULT_EXCHANGER_NAME,
        queue_name=DEFAULT_QUEUE,
        routing_key=DEFAULT_QUEUE
    )
    # Clean all messages inside if any from previous tests
    RMQConnector.queue_purge(channel=test_channel, queue_name=DEFAULT_QUEUE)


@fixture(scope="session", name="rabbitmq_publisher")
def fixture_rabbitmq_publisher(rabbitmq_defaults):
    rmq_data = verify_and_parse_mq_uri(RABBITMQ_URL)
    logger = getLogger(name="ocrd_network_testing")
    yield connect_rabbitmq_publisher(logger=logger, rmq_data=rmq_data)


@fixture(scope="session", name="rabbitmq_consumer")
def fixture_rabbitmq_consumer(rabbitmq_defaults):
    rmq_data = verify_and_parse_mq_uri(RABBITMQ_URL)
    logger = getLogger(name="ocrd_network_testing")
    yield connect_rabbitmq_consumer(logger=logger, rmq_data=rmq_data)
