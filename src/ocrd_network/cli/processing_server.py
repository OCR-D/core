import click
from ocrd_network import ProcessingServer, ServerAddressParamType


@click.command('processing-server')
@click.argument('path_to_config', required=True, type=click.STRING)
@click.option('-a', '--address',
              default="localhost:8080",
              help='The URL of the Processing server, format: host:port',
              type=ServerAddressParamType(),
              required=True)
def processing_server_cli(path_to_config, address: str):
    """
    Start the Processing Server
    (proxy between the user and the
    Processing Worker(s) / Processor Server(s))
    """

    # Note, the address is already validated with the type field
    host, port = address.split(':')
    processing_server = ProcessingServer(path_to_config, host, port)
    processing_server.start()
