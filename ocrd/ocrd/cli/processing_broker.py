"""
OCR-D CLI: start the processing broker

.. click:: ocrd.cli.processing_broker:zip_cli
    :prog: ocrd processing-broker
    :nested: full
"""
import click
from ocrd_utils import initLogging
from ocrd.web.processing_broker import ProcessingBroker


@click.command('processing-broker')
@click.argument('path_to_config', required=True, type=click.STRING)
def processing_broker_cli(path_to_config, stop=False):
    """
    Start and manage processing servers with the processing broker
    """
    initLogging()
    # Start the broker
    app = ProcessingBroker(path_to_config)
    app.start()
