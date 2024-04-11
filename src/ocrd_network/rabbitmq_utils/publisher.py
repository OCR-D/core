"""
The source code in this file is adapted by reusing
some part of the source code from the official
RabbitMQ documentation.
"""
from typing import Optional
from pika import BasicProperties
from ocrd_utils import getLogger
from .connector import RMQConnector
from .constants import DEFAULT_EXCHANGER_NAME, RABBIT_MQ_HOST, RABBIT_MQ_PORT, RABBIT_MQ_VHOST


class RMQPublisher(RMQConnector):
    def __init__(self, host: str = RABBIT_MQ_HOST, port: int = RABBIT_MQ_PORT, vhost: str = RABBIT_MQ_VHOST) -> None:
        self.log = getLogger("ocrd_network.rabbitmq_utils.publisher")
        super().__init__(host=host, port=port, vhost=vhost)
        self.message_counter = 0
        self.deliveries = {}
        self.acked_counter = 0
        self.nacked_counter = 0
        self.running = True

    def authenticate_and_connect(self, username: str, password: str) -> None:
        super()._authenticate_and_connect(username=username, password=password)

    def setup_defaults(self) -> None:
        RMQConnector.declare_and_bind_defaults(self._connection, self._channel)

    def publish_to_queue(
        self, queue_name: str, message: bytes, exchange_name: Optional[str] = DEFAULT_EXCHANGER_NAME,
        properties: Optional[BasicProperties] = None
    ) -> None:
        if properties is None:
            headers = {"ocrd_network default header": "ocrd_network default header value"}
            properties = BasicProperties(
                app_id="ocrd_network default app id",
                content_type="application/json",
                headers=headers
            )

        # Note: There is no way to publish to a queue directly.
        # Publishing happens through an exchange agent with
        # a routing key - specified when binding the queue to the exchange
        RMQConnector.basic_publish(
            self._channel,
            exchange_name=exchange_name,
            # The routing key and the queue name must match!
            routing_key=queue_name,
            message_body=message,
            properties=properties
        )

        self.message_counter += 1
        self.deliveries[self.message_counter] = True
        self.log.debug(f"Published message #{self.message_counter} to queue: {queue_name}")

    def enable_delivery_confirmations(self) -> None:
        self.log.debug("Enabling delivery confirmations (Confirm.Select RPC)")
        RMQConnector.confirm_delivery(channel=self._channel)
