# The RabbitMQ utils are directly copied from the OCR-D WebAPI implementation repo
# https://github.com/OCR-D/ocrd-webapi-implementation/tree/main/ocrd_webapi/rabbitmq

__all__ = [
  'RMQConsumer',
  'RMQConnector',
  'RMQPublisher',
  'OcrdProcessingMessage',
  'OcrdResultMessage'
]

from .consumer import RMQConsumer
from .connector import RMQConnector
from .publisher import RMQPublisher
from .ocrd_messages import (
  OcrdProcessingMessage,
  OcrdResultMessage
)
