"""
OCR-D CLI: start the processing broker

.. click:: ocrd.cli.processing_broker:zip_cli
    :prog: ocrd processing-broker
    :nested: full
"""
import click
from ocrd_utils import initLogging
from ocrd.network import ProcessingBroker


@click.command('processing-broker')
@click.argument('path_to_config', required=True, type=click.STRING)
@click.option('-a', '--address', help='Host name/IP, port to bind the Processing-Broker to')
def processing_broker_cli(path_to_config, address: str):
    """
    Start and manage processing servers (workers) with the processing broker
    """
    initLogging()
    try:
        host, port = address.split(":")
        port_int = int(port)
    except ValueError:
        raise click.UsageError('The --adddress option must have the format IP:PORT')
    processing_broker = ProcessingBroker(path_to_config, host, port_int)
    # Start the Processing Broker aka the Processing Server (the new name)
    processing_broker.start()
