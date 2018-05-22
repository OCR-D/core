import click

from ocrd.webservice.processor import create as create_processor_ws
from ocrd.webservice.wrap_executable import create as create_wrap_executable
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
@click.option('-d', '--debug', help="Whether to run in debug mode", is_flag=True, default=True)
def _start_processor(port, debug):
    """
    Start a server exposing the processors as webservices
    """
    create_processor_ws().run(port=port, debug=debug)

@server_cli.command('wrap-executable')
@click.option('-p', '--port', help="Port to run processor webservice on", default=5010)
@click.option('-d', '--debug', help="Whether to run in debug mode", is_flag=True, default=True)
@click.argument('executable')
def _wrap_executable(port, debug, executable):
    """
    Start a server wrapping the MP CLI
    """
    create_wrap_executable(executable).run(port=port, debug=debug)

@server_cli.command('repository')
@click.option('-p', '--port', help="Port to run repository webservice on", default=5000)
@click.option('-d', '--debug', help="Whether to run in debug mode", is_flag=True, default=True)
def _start_repository(port, debug):
    """
    Start a minimal repository.
    """
    create_repository_ws().run(port=port, debug=debug)
