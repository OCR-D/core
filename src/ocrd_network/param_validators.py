from click import ParamType

from .database import verify_database_uri
from .rabbitmq_utils import verify_and_parse_mq_uri


class ServerAddressParamType(ParamType):
    name = "Server address string format"
    expected_format = "host:port"

    def convert(self, value, param, ctx):
        try:
            elements = value.split(':')
            if len(elements) != 2:
                raise ValueError("The processing server address is in wrong format")
            int(elements[1])  # validate port
        except ValueError as error:
            message = f"Expected format: {self.expected_format}, error: {error}"
            self.fail(message, param, ctx)
        return value


class QueueServerParamType(ParamType):
    name = "Message queue server string format"

    def convert(self, value, param, ctx):
        try:
            # perform validation check only
            verify_and_parse_mq_uri(value)
        except Exception as error:
            message = f"Failed to validate the RabbitMQ address, error: {error}"
            self.fail(message, param, ctx)
        return value


class DatabaseParamType(ParamType):
    name = "Database string format"

    def convert(self, value, param, ctx):
        try:
            # perform validation check only
            verify_database_uri(value)
        except Exception as error:
            message = f"Failed to validate the MongoDB address, error: {error}"
            self.fail(message, param, ctx)
        return value
