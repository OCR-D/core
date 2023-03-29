"""
OCR-D CLI: start the processor server

.. click:: ocrd.cli.processor_server:processor_server_cli
    :prog: ocrd processor-server
    :nested: full
"""
import click
import logging
from ocrd_utils import initLogging
from ocrd_network import (
    DatabaseParamType,
    ProcessingServerParamType,
    ProcessorServer,
)


@click.command('processor-server')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('--agent_address',
              help='The URL of the processor server, format: host:port',
              type=ProcessingServerParamType(),
              required=True)
@click.option('-d', '--database',
              default="mongodb://localhost:27018",
              help='The URL of the MongoDB, format: mongodb://host:port',
              type=DatabaseParamType(),
              required=True)
def processor_server_cli(processor_name: str, agent_type: str, agent_address: str, database: str):
    """
    Start ocr-d processor as a server
    """
    initLogging()
    # TODO: Remove before the release
    logging.getLogger('ocrd.network').setLevel(logging.DEBUG)

    try:
        # TODO: Better validate that inside the ProcessorServer itself
        host, port = agent_address.split(':')
        processor_server = ProcessorServer(
            mongodb_addr=database,
            processor_name=processor_name,
            processor_class=None,  # For readability purposes assigned here
        )
        processor_server.run_server(host=host, port=int(port))
    except Exception as e:
        raise Exception("Processor server has failed with error") from e
