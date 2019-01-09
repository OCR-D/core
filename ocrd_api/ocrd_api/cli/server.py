import click

from ocrd.webservice.processor import create as create_processor_ws
from ocrd.webservice.repository import create as create_repository_ws

# ----------------------------------------------------------------------
# ocrd server
# ----------------------------------------------------------------------

@click.group('server')
def server_cli():
    """
    Start OCR-D web services
    """

@server_cli.command('process')
@click.option('-p', '--port', help="Port to run processor webservice on", default=5010)
def _start_processor(port):
    """
    Start a server exposing the processors as webservices
    """
    create_processor_ws().run(port=port)

@server_cli.command('repository')
@click.option('-p', '--port', help="Port to run repository webservice on", default=5000)
def _start_repository(port):
    """
    Start a minimal repository.
    """
    create_repository_ws().run(port=port)
