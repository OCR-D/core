"""
OCR-D CLI: start the processing broker

.. click:: ocrd.cli.processing_broker:zip_cli
    :prog: ocrd processing-broker
    :nested: full
"""
import click
from ocrd_utils import initLogging
from ocrd.network import ProcessingBroker
import sys


@click.command('processing-broker')
@click.argument('path_to_config', required=True, type=click.STRING)
def processing_broker_cli(path_to_config, stop=False):
    """
    Start and manage processing servers (workers) with the processing broker
    """
    initLogging()
    res = ProcessingBroker.validate_config(path_to_config)
    if res:
        print(f"config is invalid: {res}")
        sys.exit(1)
    app = ProcessingBroker(path_to_config)
    app.start()
