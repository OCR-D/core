import click
from ocrd_network import ResourceManagerServer, ServerAddressParamType


@click.command('resmgr-server')
@click.option('-a', '--address',
              help='The URL of the OCR-D resource manager server, format: host:port',
              type=ServerAddressParamType(),
              required=True)
def resource_manager_server_cli(address: str):
    """
    Start standalone REST API OCR-D Resource Manager Server
    """
    try:
        # Note, the address is already validated with the type field
        host, port = address.split(':')
        resource_manager_server = ResourceManagerServer(
            host = host,
            port = int(port)
        )
        resource_manager_server.start()
    except Exception as e:
        raise Exception("OCR-D Resource Manager Server has failed with error") from e
