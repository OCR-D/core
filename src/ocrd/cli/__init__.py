"""
OCR-D Command-line interface

.. click:: ocrd.cli:cli
    :prog: ocrd
    :nested: short
"""
import re
import click

from ocrd_utils import config

# pylint: disable=wrong-import-position

def command_with_replaced_help(*replacements):

    class CommandWithReplacedHelp(click.Command):
        def get_help(self, ctx):
            newhelp = super().get_help(ctx)
            for replacement in replacements:
                newhelp = re.sub(*replacement, newhelp)
            # print(newhelp)
            return newhelp

    return CommandWithReplacedHelp

# pylint: enable=wrong-import-position

from ..decorators import ocrd_loglevel
from .ocrd_tool import ocrd_tool_cli
from .workspace import workspace_cli
from .process import process_cli
from .bashlib import bashlib_cli
from .validate import validate_cli
from .resmgr import resmgr_cli
from .zip import zip_cli
from .log import log_cli
from .network import network_cli


__all__ = ['cli']

_epilog = f"""

\b
Variables:
\b
  PATH
    Search path for processor executables
    (affects `ocrd process` and `ocrd resmgr`)
\b
{config.describe('HOME')}
\b
{config.describe('XDG_CONFIG_HOME')}
\b
{config.describe('XDG_DATA_HOME')}
\b
{config.describe('OCRD_DOWNLOAD_RETRIES')}
\b
{config.describe('OCRD_DOWNLOAD_TIMEOUT')}
\b
{config.describe('OCRD_DOWNLOAD_INPUT')}
\b
{config.describe('OCRD_MISSING_INPUT', wrap_text=False)}
\b
{config.describe('OCRD_MISSING_OUTPUT', wrap_text=False)}
\b
{config.describe('OCRD_EXISTING_OUTPUT', wrap_text=False)}
\b
{config.describe('OCRD_METS_CACHING')}
\b
{config.describe('OCRD_MAX_PROCESSOR_CACHE')}
\b
{config.describe('OCRD_NETWORK_CLIENT_POLLING_SLEEP')}
\b
{config.describe('OCRD_NETWORK_CLIENT_POLLING_TIMEOUT')}
\b
{config.describe('OCRD_NETWORK_SERVER_ADDR_PROCESSING')}
\b
{config.describe('OCRD_NETWORK_SERVER_ADDR_WORKFLOW')}
\b
{config.describe('OCRD_NETWORK_SERVER_ADDR_WORKSPACE')}
\b
{config.describe('OCRD_NETWORK_RABBITMQ_CLIENT_CONNECT_ATTEMPTS')}
\b
{config.describe('OCRD_NETWORK_RABBITMQ_HEARTBEAT')}
\b
{config.describe('OCRD_PROFILE_FILE')}
\b
{config.describe('OCRD_PROFILE', wrap_text=False)}
\b
{config.describe('OCRD_NETWORK_SOCKETS_ROOT_DIR')}
\b
{config.describe('OCRD_NETWORK_LOGS_ROOT_DIR')}
\b
{config.describe('OCRD_LOGGING_DEBUG')}
"""

@click.group(epilog=_epilog)
@click.version_option(package_name='ocrd')
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
cli.add_command(network_cli)
