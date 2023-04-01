from click import ParamType

from .utils import (
    verify_database_uri,
    verify_and_parse_mq_uri
)


class ServerAddressParamType(ParamType):
    name = 'Server address string format'
    expected_format = 'host:port'

    def convert(self, value, param, ctx):
        try:
            elements = value.split(':')
            if len(elements) != 2:
                raise ValueError('The processing server address is in wrong format')
            int(elements[1])  # validate port
        except ValueError as error:
            self.fail(f'{error}, expected format: {self.expected_format}', param, ctx)
        return value


class QueueServerParamType(ParamType):
    name = 'Message queue server string format'

    def convert(self, value, param, ctx):
        try:
            # perform validation check only
            verify_and_parse_mq_uri(value)
        except Exception as error:
            self.fail(f'{error}', param, ctx)
        return value


class DatabaseParamType(ParamType):
    name = 'Database string format'

    def convert(self, value, param, ctx):
        try:
            # perform validation check only
            verify_database_uri(value)
        except Exception as error:
            self.fail(f'{error}', param, ctx)
        return value
