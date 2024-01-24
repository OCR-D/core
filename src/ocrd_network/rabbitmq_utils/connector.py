"""
The source code in this file is adapted by reusing
some part of the source code from the official
RabbitMQ documentation.
"""
from typing import Any, Optional, Union
from pika import BasicProperties, BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from .constants import (
    DEFAULT_EXCHANGER_NAME,
    DEFAULT_EXCHANGER_TYPE,
    DEFAULT_QUEUE,
    DEFAULT_ROUTER,
    RABBIT_MQ_HOST as HOST,
    RABBIT_MQ_PORT as PORT,
    RABBIT_MQ_VHOST as VHOST,
    PREFETCH_COUNT
)


class RMQConnector:
    def __init__(self, host: str = HOST, port: int = PORT, vhost: str = VHOST) -> None:
        self._host = host
        self._port = port
        self._vhost = vhost

        # According to the documentation, Pika blocking
        # connections are not thread-safe!
        self._connection = None
        self._channel = None

        # Should try reconnecting again
        self._try_reconnecting = False
        # If the module has been stopped with a
        # keyboard interruption, i.e., CTRL + C
        self._gracefully_stopped = False

    @staticmethod
    def declare_and_bind_defaults(connection: BlockingConnection, channel: BlockingChannel) -> None:
        if connection and connection.is_open:
            if channel and channel.is_open:
                # Declare the default exchange agent
                RMQConnector.exchange_declare(
                    channel=channel,
                    exchange_name=DEFAULT_EXCHANGER_NAME,
                    exchange_type=DEFAULT_EXCHANGER_TYPE,
                )
                # Declare the default queue
                RMQConnector.queue_declare(channel, queue_name=DEFAULT_QUEUE)
                # Bind the default queue to the default exchange
                RMQConnector.queue_bind(
                    channel,
                    queue_name=DEFAULT_QUEUE,
                    exchange_name=DEFAULT_EXCHANGER_NAME,
                    routing_key=DEFAULT_ROUTER
                )

    # Connection related methods
    @staticmethod
    def open_blocking_connection(
            credentials: PlainCredentials,
            host: str = HOST,
            port: int = PORT,
            vhost: str = VHOST
    ) -> BlockingConnection:
        blocking_connection = BlockingConnection(
            parameters=ConnectionParameters(
                host=host,
                port=port,
                virtual_host=vhost,
                credentials=credentials,
                # TODO: The heartbeat should not be disabled (0)!
                heartbeat=0
            ),
        )
        return blocking_connection

    @staticmethod
    def open_blocking_channel(connection: BlockingConnection) -> Union[BlockingChannel, None]:
        if connection and connection.is_open:
            channel = connection.channel()
            return channel
        return None

    @staticmethod
    def exchange_bind(
            channel: BlockingChannel,
            destination_exchange: str,
            source_exchange: str,
            routing_key: str,
            arguments: Optional[Any] = None
    ) -> None:
        if arguments is None:
            arguments = {}
        if channel and channel.is_open:
            channel.exchange_bind(
                destination=destination_exchange,
                source=source_exchange,
                routing_key=routing_key,
                arguments=arguments
            )

    @staticmethod
    def exchange_declare(
            channel: BlockingChannel,
            exchange_name: str,
            exchange_type: str,
            passive: bool = False,
            durable: bool = False,
            auto_delete: bool = False,
            internal: bool = False,
            arguments: Optional[Any] = None
    ) -> None:
        if arguments is None:
            arguments = {}
        if channel and channel.is_open:
            exchange = channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                # Only check to see if the exchange exists
                passive=passive,
                # Survive a reboot of RabbitMQ
                durable=durable,
                # Remove when no more queues are bound to it
                auto_delete=auto_delete,
                # Can only be published to by other exchanges
                internal=internal,
                # Custom key/value pair arguments for the exchange
                arguments=arguments
            )
            return exchange

    @staticmethod
    def exchange_delete(
            channel: BlockingChannel,
            exchange_name: str,
            if_unused: bool = False
    ) -> None:
        # Deletes queue only if unused
        if channel and channel.is_open:
            channel.exchange_delete(exchange=exchange_name, if_unused=if_unused)

    @staticmethod
    def exchange_unbind(
            channel: BlockingChannel,
            destination_exchange: str,
            source_exchange: str,
            routing_key: str,
            arguments: Optional[Any] = None
    ) -> None:
        if arguments is None:
            arguments = {}
        if channel and channel.is_open:
            channel.exchange_unbind(
                destination=destination_exchange,
                source=source_exchange,
                routing_key=routing_key,
                arguments=arguments
            )

    @staticmethod
    def queue_bind(
            channel: BlockingChannel,
            queue_name: str,
            exchange_name: str,
            routing_key: str,
            arguments: Optional[Any] = None
    ) -> None:
        if arguments is None:
            arguments = {}
        if channel and channel.is_open:
            channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key, arguments=arguments)

    @staticmethod
    def queue_declare(
            channel: BlockingChannel,
            queue_name: str,
            passive: bool = False,
            durable: bool = False,
            exclusive: bool = False,
            auto_delete: bool = False,
            arguments: Optional[Any] = None
    ) -> None:
        if arguments is None:
            arguments = {}
        if channel and channel.is_open:
            queue = channel.queue_declare(
                queue=queue_name,
                # Only check to see if the queue exists and
                # raise ChannelClosed exception if it does not
                passive=passive,
                # Survive reboots of the server
                durable=durable,
                # Only allow access by the current connection
                exclusive=exclusive,
                # Delete after consumer cancels or disconnects
                auto_delete=auto_delete,
                # Custom key/value pair arguments for the queue
                arguments=arguments
            )
            return queue

    @staticmethod
    def queue_delete(
            channel: BlockingChannel,
            queue_name: str,
            if_unused: bool = False,
            if_empty: bool = False
    ) -> None:
        if channel and channel.is_open:
            channel.queue_delete(
                queue=queue_name,
                # Only delete if the queue is unused
                if_unused=if_unused,
                # Only delete if the queue is empty
                if_empty=if_empty
            )

    @staticmethod
    def queue_purge(channel: BlockingChannel, queue_name: str) -> None:
        if channel and channel.is_open:
            channel.queue_purge(queue=queue_name)

    @staticmethod
    def queue_unbind(
            channel: BlockingChannel,
            queue_name: str,
            exchange_name: str,
            routing_key: str,
            arguments: Optional[Any] = None
    ) -> None:
        if arguments is None:
            arguments = {}
        if channel and channel.is_open:
            channel.queue_unbind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key,
                arguments=arguments
            )

    @staticmethod
    def set_qos(
            channel: BlockingChannel,
            prefetch_size: int = 0,
            prefetch_count: int = PREFETCH_COUNT,
            global_qos: bool = False
    ) -> None:
        if channel and channel.is_open:
            channel.basic_qos(
                # No specific limit if set to 0
                prefetch_size=prefetch_size,
                prefetch_count=prefetch_count,
                # Should the qos apply to all channels of the connection
                global_qos=global_qos
            )

    @staticmethod
    def confirm_delivery(channel: BlockingChannel) -> None:
        if channel and channel.is_open:
            channel.confirm_delivery()

    @staticmethod
    def basic_publish(
            channel: BlockingChannel,
            exchange_name: str,
            routing_key: str,
            message_body: bytes,
            properties: BasicProperties
    ) -> None:
        if channel and channel.is_open:
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message_body,
                properties=properties
            )
