import sys

import click

from ocrd_utils import initLogging
from ocrd_validators import OcrdZipValidator

from ..resource_manager import OcrdResourceManager

@click.group("resmgr")
def resmgr_cli():
    """
    Managing processor resources
    """
    initLogging()

# ----------------------------------------------------------------------
# ocrd zip list-available
# ----------------------------------------------------------------------

@resmgr_cli.command('list-available')
@click.option('-e', '--executable', help='Show only resources for executable EXEC', metavar='EXEC')
def list_available(executable=None):
    """
    List available resources
    """
    resmgr = OcrdResourceManager()
    for executable, reslist in resmgr.list_available(executable):
        print('%s' % executable)
        for resdict in reslist:
            print('- %s (%s)\n  %s' % (resdict['name'], resdict['url'], resdict['description']))
        print()

@resmgr_cli.command('list-installed')
@click.option('-e', '--executable', help='Show only resources for executable EXEC', metavar='EXEC')
def list_installed(executable=None):
    """
    List installed resources
    """
    resmgr = OcrdResourceManager()
    ret = []
    for executable, reslist in resmgr.list_installed(executable):
        print(executable, reslist)
