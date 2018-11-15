import click

from ocrd.cli.ocrd_tool import ocrd_tool_cli
from ocrd.cli.workspace import workspace_cli
from ocrd.cli.generate_swagger import generate_swagger_cli
from ocrd.cli.process import process_cli
# TODO server CLI disabled
#  from ocrd.cli.server import server_cli
from ocrd.cli.bashlib import bashlib_cli
from ocrd.decorators import ocrd_loglevel
from .zip import zip_cli

@click.group()
@click.version_option()
@ocrd_loglevel
def cli(**kwargs): # pylint: disable=unused-argument
    """
    CLI to OCR-D
    """

cli.add_command(ocrd_tool_cli)
cli.add_command(workspace_cli)
cli.add_command(generate_swagger_cli)
cli.add_command(process_cli)
# TODO server CLI disabled
#  cli.add_command(server_cli)
cli.add_command(bashlib_cli)
cli.add_command(zip_cli)
