from logging import Logger
from pika import URLParameters
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker
from re import match as re_match
from time import sleep
from typing import Dict, List, Union

from .constants import RABBITMQ_URI_PATTERN, RECONNECT_TRIES, RECONNECT_WAIT
from .consumer import RMQConsumer
from .publisher import RMQPublisher


def __connect_rabbitmq_client(
    logger: Logger, client_type: str, rmq_data: Dict, attempts: int = RECONNECT_TRIES, delay: int = RECONNECT_WAIT
) -> Union[RMQConsumer, RMQPublisher]:
    try:
        rmq_host: str = rmq_data["host"]
        rmq_port: int = rmq_data["port"]
        rmq_vhost: str = rmq_data["vhost"]
        rmq_username: str = rmq_data["username"]
        rmq_password: str = rmq_data["password"]
    except ValueError as error:
        raise Exception("Failed to parse RabbitMQ connection data") from error
    logger.info(f"Connecting client to RabbitMQ server: {rmq_host}:{rmq_port}{rmq_vhost}")
    logger.debug(f"RabbitMQ client authenticates with username: {rmq_username}, password: {rmq_password}")
    while attempts > 0:
        try:
            if client_type == "consumer":
                rmq_client = RMQConsumer(host=rmq_host, port=rmq_port, vhost=rmq_vhost)
            elif client_type == "publisher":
                rmq_client = RMQPublisher(host=rmq_host, port=rmq_port, vhost=rmq_vhost)
            else:
                raise RuntimeError(f"RabbitMQ client type can be either a consumer or publisher. Got: {client_type}")
            rmq_client.authenticate_and_connect(username=rmq_username, password=rmq_password)
            return rmq_client
        except AMQPConnectionError:
            attempts -= 1
            sleep(delay)
            continue
    raise RuntimeError(f"Failed to establish connection with the RabbitMQ Server. Connection data: {rmq_data}")


def connect_rabbitmq_consumer(logger: Logger, rmq_data: Dict) -> RMQConsumer:
    rmq_consumer = __connect_rabbitmq_client(logger=logger, client_type="consumer", rmq_data=rmq_data)
    logger.info(f"Successfully connected RMQConsumer")
    return rmq_consumer


def connect_rabbitmq_publisher(logger: Logger, rmq_data: Dict, enable_acks: bool = True) -> RMQPublisher:
    rmq_publisher = __connect_rabbitmq_client(logger=logger, client_type="publisher", rmq_data=rmq_data)
    if enable_acks:
        rmq_publisher.enable_delivery_confirmations()
        logger.info("Delivery confirmations are enabled")
    logger.info("Successfully connected RMQPublisher")
    return rmq_publisher


def check_if_queue_exists(logger: Logger, rmq_data: Dict, processor_name: str) -> bool:
    rmq_publisher = connect_rabbitmq_publisher(logger, rmq_data)
    try:
        # Passively checks whether the queue name exists, if not raises ChannelClosedByBroker
        rmq_publisher.create_queue(processor_name, passive=True)
        return True
    except ChannelClosedByBroker as error:
        # The created connection was forcibly closed by the RabbitMQ Server
        logger.warning(f"Process queue with id '{processor_name}' not existing: {error}")
        return False


def create_message_queues(logger: Logger, rmq_publisher: RMQPublisher, queue_names: List[str]) -> None:
    # TODO: Reconsider and refactor this.
    #  Added ocrd-dummy by default if not available for the integration tests.
    #  A proper Processing Worker / Processor Server registration endpoint is needed on the Processing Server side
    if "ocrd-dummy" not in queue_names:
        queue_names.append("ocrd-dummy")

    for queue_name in queue_names:
        # The existence/validity of the worker.name is not tested.
        # Even if an ocr-d processor does not exist, the queue is created
        logger.info(f"Creating a message queue with id: {queue_name}")
        rmq_publisher.create_queue(queue_name=queue_name)


def verify_and_parse_mq_uri(rabbitmq_address: str):
    """
    Check the full list of available parameters in the docs here:
    https://pika.readthedocs.io/en/stable/_modules/pika/connection.html#URLParameters
    """
    match = re_match(pattern=RABBITMQ_URI_PATTERN, string=rabbitmq_address)
    if not match:
        raise ValueError(f"The message queue server address is in wrong format: '{rabbitmq_address}'")
    url_params = URLParameters(rabbitmq_address)
    parsed_data = {
        "username": url_params.credentials.username,
        "password": url_params.credentials.password,
        "host": url_params.host,
        "port": url_params.port,
        "vhost": url_params.virtual_host
    }
    return parsed_data


def verify_rabbitmq_available(logger: Logger, rabbitmq_address: str) -> None:
    rmq_data = verify_and_parse_mq_uri(rabbitmq_address=rabbitmq_address)
    temp_publisher = connect_rabbitmq_publisher(logger, rmq_data, enable_acks=True)
    temp_publisher.close_connection()
