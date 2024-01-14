from pika import URLParameters
from pika.credentials import PlainCredentials
from pytest import fixture
from re import match as re_match
from ocrd_network.rabbitmq_utils import RMQConnector, RMQConsumer, RMQPublisher
from .constants import RABBITMQ_URL, DEFAULT_EXCHANGER_NAME, DEFAULT_QUEUE


def verify_and_parse_mq_uri(rabbitmq_address: str):
    """
    Check the full list of available parameters in the docs here:
    https://pika.readthedocs.io/en/stable/_modules/pika/connection.html#URLParameters
    """

    uri_pattern = r"^(?:([^:\/?#\s]+):\/{2})?(?:([^@\/?#\s]+)@)?([^\/?#\s]+)?(?:\/([^?#\s]*))?(?:[?]([^#\s]+))?\S*$"
    match = re_match(pattern=uri_pattern, string=rabbitmq_address)
    if not match:
        raise ValueError(f"The RabbitMQ server address is in wrong format: '{rabbitmq_address}'")
    url_params = URLParameters(rabbitmq_address)

    parsed_data = {
        "username": url_params.credentials.username,
        "password": url_params.credentials.password,
        "host": url_params.host,
        "port": url_params.port,
        "vhost": url_params.virtual_host
    }
    return parsed_data


@fixture(scope="package", name="rabbitmq_defaults")
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
    assert(test_channel)
    RMQConnector.exchange_declare(
        channel=test_channel,
        exchange_name=DEFAULT_EXCHANGER_NAME,
        exchange_type='direct',
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


@fixture(scope="package", name="rabbitmq_publisher")
def fixture_rabbitmq_publisher(rabbitmq_defaults):
    assert rabbitmq_defaults
    rmq_data = verify_and_parse_mq_uri(RABBITMQ_URL)
    rmq_publisher = RMQPublisher(
        host=rmq_data["host"],
        port=rmq_data["port"],
        vhost=rmq_data["vhost"]
    )
    rmq_publisher.authenticate_and_connect(
        username=rmq_data["username"],
        password=rmq_data["password"]
    )
    rmq_publisher.enable_delivery_confirmations()
    yield rmq_publisher


@fixture(scope="package", name="rabbitmq_consumer")
def fixture_rabbitmq_consumer(rabbitmq_defaults):
    assert rabbitmq_defaults
    rmq_data = verify_and_parse_mq_uri(RABBITMQ_URL)
    rmq_consumer = RMQConsumer(
        host=rmq_data["host"],
        port=rmq_data["port"],
        vhost=rmq_data["vhost"]
    )
    rmq_consumer.authenticate_and_connect(
        username=rmq_data["username"],
        password=rmq_data["password"]
    )
    yield rmq_consumer
