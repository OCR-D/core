"""
OCR-D CLI: management of network components

.. click:: ocrd.cli.network:network_cli
    :prog: ocrd network
    :nested: full
"""

import click
import logging
from ocrd_utils import initLogging
from ocrd_network.cli import (
    client_cli,
    processing_server_cli,
    processing_worker_cli,
    processor_server_cli,
)


@click.group("network")
def network_cli():
    """
    Managing network components
    """
    initLogging()
    # TODO: Remove after the logging fix in core
    logging.getLogger('paramiko.transport').setLevel(logging.INFO)
    logging.getLogger('ocrd.network').setLevel(logging.DEBUG)


network_cli.add_command(client_cli)
network_cli.add_command(processing_server_cli)
network_cli.add_command(processing_worker_cli)
network_cli.add_command(processor_server_cli)
