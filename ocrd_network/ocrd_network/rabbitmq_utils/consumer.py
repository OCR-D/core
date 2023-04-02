"""
The source code in this file is adapted by reusing
some part of the source code from the official
RabbitMQ documentation.
"""

import logging
from typing import Any, Union

from pika import PlainCredentials

from .constants import (
    DEFAULT_QUEUE,
    LOG_LEVEL,
    RABBIT_MQ_HOST as HOST,
    RABBIT_MQ_PORT as PORT,
    RABBIT_MQ_VHOST as VHOST
)
from .connector import RMQConnector


class RMQConsumer(RMQConnector):
    def __init__(self, host: str = HOST, port: int = PORT, vhost: str = VHOST,
                 logger_name: str = '') -> None:
        if not logger_name:
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

    def authenticate_and_connect(self, username: str, password: str) -> None:
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

    def setup_defaults(self) -> None:
        RMQConnector.declare_and_bind_defaults(self._connection, self._channel)

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
            queue_name: str,
            callback_method: Any
    ) -> None:
        self._logger.debug(f'Configuring consuming with queue: {queue_name}')
        self._channel.add_on_cancel_callback(self.__on_consumer_cancelled)
        self.consumer_tag = self._channel.basic_consume(
            queue_name,
            callback_method
        )
        self.was_consuming = True
        self.consuming = True

    def start_consuming(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.start_consuming()

    def get_waiting_message_count(self) -> Union[int, None]:
        if self._channel and self._channel.is_open:
            return self._channel.get_waiting_message_count()
        return None

    def __on_consumer_cancelled(self, frame: Any) -> None:
        self._logger.warning(f'The consumer was cancelled remotely in frame: {frame}')
        if self._channel:
            self._channel.close()

    def ack_message(self, delivery_tag: int) -> None:
        self._logger.debug(f'Acknowledging message {delivery_tag}')
        self._channel.basic_ack(delivery_tag)
