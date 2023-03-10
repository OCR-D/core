from click import ParamType
from re import split as re_split


class ProcessingServerParamType(ParamType):
    name = "Processing server string format"
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
    name = "Queue server string format"
    expected_format = 'username:password@host:port/vhost'

    def convert(self, value, param, ctx):
        try:
            elements = value.split('@')
            if len(elements) != 2:
                raise ValueError('The RabbitMQ address is in wrong format')
            credentials = elements[0].split(':')
            if len(credentials) != 2:
                raise ValueError(f'The RabbitMQ credentials are in wrong format')
            host_info = re_split(pattern=r':|/', string=elements[1])
            if len(host_info) != 3 and len(host_info) != 2:
                raise ValueError('The RabbitMQ host info is in wrong format')
            int(host_info[1])  # validate port
        except ValueError as error:
            self.fail(f'{error}, expected format: {self.expected_format}', param, ctx)
        return value


class DatabaseParamType(ParamType):
    name = "Database string format"
    expected_format = 'mongodb://host:port'

    def convert(self, value, param, ctx):
        database_prefix = 'mongodb://'
        try:
            if not value.startswith(database_prefix):
                raise ValueError(f'Wrong database prefix, expected prefix: {database_prefix}')
            address_without_prefix = value[len(database_prefix):]
            elements = address_without_prefix.split(':')
            if len(elements) != 2:
                raise ValueError(f'The database host and port are in wrong format')
            int(elements[1])  # validate port
        except ValueError as error:
            self.fail(f'{error}, expected format: {self.expected_format}', param, ctx)
        return value
