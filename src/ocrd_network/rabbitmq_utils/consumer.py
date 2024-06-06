"""
The source code in this file is adapted by reusing
some part of the source code from the official
RabbitMQ documentation.
"""
from typing import Any, Union
from ocrd_utils import getLogger
from .connector import RMQConnector
from .constants import RABBIT_MQ_HOST, RABBIT_MQ_PORT, RABBIT_MQ_VHOST


class RMQConsumer(RMQConnector):
    def __init__(self, host: str = RABBIT_MQ_HOST, port: int = RABBIT_MQ_PORT, vhost: str = RABBIT_MQ_VHOST) -> None:
        self.log = getLogger("ocrd_network.rabbitmq_utils.consumer")
        super().__init__(host=host, port=port, vhost=vhost)
        self.consumer_tag = None
        self.consuming = False
        self.was_consuming = False
        self.closing = False
        self.reconnect_delay = 0

    def authenticate_and_connect(self, username: str, password: str) -> None:
        super()._authenticate_and_connect(username=username, password=password)
        RMQConnector.set_qos(self._channel)
        self.log.info("Set QoS for the consumer")

    def setup_defaults(self) -> None:
        RMQConnector.declare_and_bind_defaults(self._connection, self._channel)

    def get_one_message(self, queue_name: str, auto_ack: bool = False) -> Union[Any, None]:
        message = None
        if self._channel and self._channel.is_open:
            message = self._channel.basic_get(queue=queue_name, auto_ack=auto_ack)
        return message

    def configure_consuming(self, queue_name: str, callback_method: Any) -> None:
        self.log.debug(f"Configuring consuming from queue: {queue_name}")
        self._channel.add_on_cancel_callback(self.__on_consumer_cancelled)
        self.consumer_tag = self._channel.basic_consume(queue_name, callback_method)
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
        self.log.warning(f"The consumer was cancelled remotely in frame: {frame}")
        if self._channel:
            self._channel.close()

    def ack_message(self, delivery_tag: int) -> None:
        self.log.debug(f"Acknowledging message with delivery tag: {delivery_tag}")
        self._channel.basic_ack(delivery_tag)
