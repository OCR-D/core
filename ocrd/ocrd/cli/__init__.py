"""
OCR-D Command-line interface

.. click:: ocrd.cli:cli
    :prog: ocrd
    :nested: short
"""
import re
import click

__all__ = ['cli']

def command_with_replaced_help(*replacements):

    class CommandWithReplacedHelp(click.Command):
        def get_help(self, ctx):
            help = super().get_help(ctx)
            for replacement in replacements:
                help = re.sub(*replacement, help)
            # print(help)
            return help

    return CommandWithReplacedHelp

from ocrd.cli.ocrd_tool import ocrd_tool_cli
from ocrd.cli.workspace import workspace_cli
from ocrd.cli.process import process_cli
from ocrd.cli.bashlib import bashlib_cli
from ocrd.cli.validate import validate_cli
from ocrd.cli.resmgr import resmgr_cli
from ocrd.decorators import ocrd_loglevel
from .zip import zip_cli
from .log import log_cli

@click.group()
@click.version_option()
@ocrd_loglevel
def cli(**kwargs): # pylint: disable=unused-argument
    """
    Entry-point of multi-purpose CLI for OCR-D
    """

cli.add_command(ocrd_tool_cli)
cli.add_command(workspace_cli)
cli.add_command(process_cli)
cli.add_command(bashlib_cli)
cli.add_command(zip_cli)
cli.add_command(validate_cli)
cli.add_command(log_cli)
cli.add_command(resmgr_cli)
