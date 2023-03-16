"""
OCR-D CLI: start the processing server

.. click:: ocrd.cli.processing_server:zip_cli
    :prog: ocrd processing-server
    :nested: full
"""
import click
import logging
from ocrd_utils import initLogging
from ocrd_network import (
    ProcessingServer,
    ProcessingServerParamType
)


@click.command('processing-server')
@click.argument('path_to_config', required=True, type=click.STRING)
@click.option('-a', '--address',
              default="localhost:8080",
              help='The URL of the Processing server, format: host:port',
              type=ProcessingServerParamType(),
              required=True)
def processing_server_cli(path_to_config, address: str):
    """
    Start and manage processing workers with the processing server

    PATH_TO_CONFIG is a yaml file to configure the server and the workers. See
    https://github.com/OCR-D/spec/pull/222/files#diff-a71bf71cbc7d9ce94fded977f7544aba4df9e7bdb8fc0cf1014e14eb67a9b273
    for further information (TODO: update path when spec is available/merged)

    """
    initLogging()
    # TODO: Remove before the release
    logging.getLogger('paramiko.transport').setLevel(logging.INFO)
    logging.getLogger('ocrd.network').setLevel(logging.DEBUG)

    # Note, the address is already validated with the type field
    host, port = address.split(':')
    processing_server = ProcessingServer(path_to_config, host, port)
    processing_server.start()
