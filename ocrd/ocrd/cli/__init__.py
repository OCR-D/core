"""
OCR-D Command-line interface

.. click:: ocrd.cli:cli
    :prog: ocrd
    :nested: short
"""
import re
import click

__all__ = ['cli']

_epilog = """

\b            
Variables:
  PATH    Search path for processor executables
          (affects `ocrd process` and `ocrd resmgr`)
  HOME    Directory to look for `ocrd_logging.conf`,
          fallback for unset XDG variables.

\b
  XDG_CONFIG_HOME
    Directory to look for `./ocrd/resources.yml`
    (i.e. `ocrd resmgr` user database) - defaults to
    `$HOME/.config`.
  XDG_DATA_HOME
    Directory to look for `./ocrd-resources/*`
    (i.e. `ocrd resmgr` data location) - defaults to
    `$HOME/.local/share`.

\b
  OCRD_DOWNLOAD_RETRIES
    Number of times to retry failed attempts
    for downloads of workspace files.
  OCRD_DOWNLOAD_TIMEOUT
    Timeout in seconds for connecting or reading
    (comma-separated) when downloading.

\b
  OCRD_METS_CACHING
    Whether to enable in-memory storage of OcrdMets
    data structures for speedup during processing or
    workspace operations.

\b
  OCRD_MAX_PROCESSOR_CACHE
    Maximum number of processor instances
    (for each set of parameters) to be kept
    in memory (including loaded models) for
    processing workers or processor servers.

\b
  OCRD_NETWORK_SERVER_ADDR_PROCESSING
    Default address of Processing Server to connect to
    (for `ocrd network client processing`).
  OCRD_NETWORK_SERVER_ADDR_WORKFLOW
    Default address of Workflow Server to connect to
    (for `ocrd network client workflow`).
  OCRD_NETWORK_SERVER_ADDR_WORKSPACE
    Default address of Workspace Server to connect to
    (for `ocrd network client workspace`).

\b
  OCRD_PROFILE
    Whether to enable gathering runtime statistics
    on the `ocrd.profile` logger:
    - non-empty: yields CPU and wall-time,
    - `RSS`: also yields peak memory (resident set size)
    - `PSS`: also yields peak memory (proportional set size)
  OCRD_PROFILE_FILE
    When profiling is enabled, file to write to
    (instead of standard log handler).
"""

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
from .network import network_cli


@click.group(epilog=_epilog)
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
cli.add_command(network_cli)
