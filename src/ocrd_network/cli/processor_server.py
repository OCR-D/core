import click
from ocrd_network import DatabaseParamType, ProcessorServer, ServerAddressParamType


@click.command('processor-server')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('-a', '--address',
              help='The URL of the processor server, format: host:port',
              type=ServerAddressParamType(),
              required=True)
@click.option('-d', '--database',
              default="mongodb://localhost:27018",
              help='The URL of the MongoDB, format: mongodb://host:port',
              type=DatabaseParamType(),
              required=True)
def processor_server_cli(processor_name: str, address: str, database: str):
    """
    Start Processor Server
    (standalone REST API OCR-D processor)
    """
    try:
        # Note, the address is already validated with the type field
        host, port = address.split(':')
        processor_server = ProcessorServer(
            mongodb_addr=database,
            processor_name=processor_name,
            processor_class=None  # For readability purposes assigned here
        )
        processor_server.run_server(host=host, port=int(port))
    except Exception as e:
        raise Exception("Processor server has failed with error") from e
