"""
The source code in this file is adapted by reusing
some part of the source code from the official
RabbitMQ documentation.
"""

import logging
from time import sleep
from typing import Any, Union

from pika import (
    PlainCredentials
)

from ocrd_webapi.rabbitmq.constants import (
    DEFAULT_QUEUE,
    LOG_FORMAT,
    LOG_LEVEL,
    RABBIT_MQ_HOST as HOST,
    RABBIT_MQ_PORT as PORT,
    RABBIT_MQ_VHOST as VHOST
)
from ocrd_webapi.rabbitmq.connector import RMQConnector


class RMQConsumer(RMQConnector):
    def __init__(self, host: str = HOST, port: int = PORT, vhost: str = VHOST, logger_name: str = None):
        if logger_name is None:
            logger_name = __name__
        logger = logging.getLogger(logger_name)
        logging.getLogger(logger_name).setLevel(LOG_LEVEL)
        # This may mess up the global logger
        logging.basicConfig(level=logging.WARNING)
        super().__init__(logger=logger, host=host, port=port, vhost=vhost)

        self.consumer_tag = None
        self.consuming = False
        self.was_consuming = False
        self.closing = False

        self.reconnect_delay = 0

    def authenticate_and_connect(self, username: str, password: str):
        credentials = PlainCredentials(
            username=username,
            password=password,
            erase_on_connect=False  # Delete credentials once connected
        )
        self._connection = RMQConnector.open_blocking_connection(
            host=self._host,
            port=self._port,
            vhost=self._vhost,
            credentials=credentials,
        )
        self._channel = RMQConnector.open_blocking_channel(self._connection)

    def setup_defaults(self):
        RMQConnector.declare_and_bind_defaults(self._connection, self._channel)

    def example_run(self):
        self.configure_consuming()
        try:
            self.start_consuming()
        except KeyboardInterrupt:
            self._logger.info("Keyboard interruption detected. Closing down peacefully.")
            exit(0)
        # TODO: Clean leftovers here and inform the RabbitMQ
        #  server about the disconnection of the consumer
        # TODO: Implement the reconnect mechanism
        except Exception:
            reconnect_delay = 10
            self._logger.info(f'Reconnecting after {reconnect_delay} seconds')
            sleep(reconnect_delay)

    def get_one_message(
            self,
            queue_name: str,
            auto_ack: bool = False
    ) -> Union[Any, None]:
        message = None
        if self._channel and self._channel.is_open:
            message = self._channel.basic_get(
                queue=queue_name,
                auto_ack=auto_ack
            )
        return message

    def configure_consuming(
            self,
            queue_name: str = None,
            callback_method: Any = None
    ):
        self._logger.debug('Issuing consumer related RPC commands')
        self._logger.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.__on_consumer_cancelled)
        if queue_name is None:
            queue_name = DEFAULT_QUEUE
        if callback_method is None:
            callback_method = self.__on_message_received
        self.consumer_tag = self._channel.basic_consume(
            queue_name,
            callback_method
        )
        self.was_consuming = True
        self.consuming = True

    def start_consuming(self):
        if self._channel and self._channel.is_open:
            self._channel.start_consuming()

    def get_waiting_message_count(self):
        if self._channel and self._channel.is_open:
            return self._channel.get_waiting_message_count()

    def __on_consumer_cancelled(self, frame: Any):
        self._logger.warning(f'The consumer was cancelled remotely in frame: {frame}')
        if self._channel:
            self._channel.close()

    def __on_message_received(
            self,
            channel,
            basic_deliver,
            properties,
            body
    ):
        tag = basic_deliver.delivery_tag
        app_id = properties.app_id
        message = body.decode()
        self._logger.debug(f'Received message #{tag} from {app_id}: {message}')
        self._logger.debug(f'Received message on channel: {channel}')
        self.__ack_message(tag)

    def __ack_message(self, delivery_tag):
        self._logger.debug(f'Acknowledging message {delivery_tag}')
        self._channel.basic_ack(delivery_tag)


def main():
    # Connect to localhost:5672 by
    # using the virtual host "/" (%2F)
    consumer = RMQConsumer(host="localhost", port=5672, vhost="/")
    # Configured with definitions.json when building the RabbitMQ image
    # Check Dockerfile-RabbitMQ
    consumer.authenticate_and_connect(
        username="default-consumer",
        password="default-consumer"
    )
    consumer.setup_defaults()
    consumer.example_run()


if __name__ == '__main__':
    # RabbitMQ Server must be running before starting the example
    # I.e., make start-rabbitmq
    main()
