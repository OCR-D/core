import sys
from os import getcwd
from pathlib import Path

import click

from ocrd_utils import (
    initLogging,
    getLogger,
    XDG_CACHE_HOME,
    XDG_CONFIG_HOME,
    XDG_DATA_HOME
)
from ocrd_validators import OcrdZipValidator

from ..resource_manager import OcrdResourceManager

def print_resources(executable, reslist):
    print('%s' % executable)
    for resdict in reslist:
        print('- %s (%s)\n  %s' % (resdict['name'], resdict['url'], resdict['description']))
    print()

@click.group("resmgr")
def resmgr_cli():
    """
    Managing processor resources
    """
    initLogging()

@resmgr_cli.command('list-available')
@click.option('-e', '--executable', help='Show only resources for executable EXEC', metavar='EXEC')
def list_available(executable=None):
    """
    List available resources
    """
    resmgr = OcrdResourceManager()
    for executable, reslist in resmgr.list_available(executable):
        print_resources(executable, reslist)

@resmgr_cli.command('list-installed')
@click.option('-e', '--executable', help='Show only resources for executable EXEC', metavar='EXEC')
def list_installed(executable=None):
    """
    List installed resources
    """
    resmgr = OcrdResourceManager()
    ret = []
    for executable, reslist in resmgr.list_installed(executable):
        print_resources(executable, reslist)

@resmgr_cli.command('download')
@click.option('-n', '--any-url', help='Allow downloading unregistered resources', is_flag=True)
@click.option('-o', '--overwrite', help='Overwrite existing resources', is_flag=True)
@click.option('-l', '--location', help='Where to store resources', type=click.Choice(['cache', 'config', 'data', 'cwd']), default='cache', show_default=True)
@click.argument('executable', required=True)
@click.argument('url_or_name', required=True)
def download(any_url, overwrite, location, executable, url_or_name):
    """
    Download resource URL_OR_NAME for processor EXECUTABLE.

    URL_OR_NAME can either be the ``name`` or ``url`` of a registered resource.

    If ``--any-url`` is given, also accepts URL of non-registered resources for ``URL_OR_NAME``.
    """
    log = getLogger('ocrd.cli.resmgr')
    resmgr = OcrdResourceManager()
    basedir = XDG_CACHE_HOME if location == 'cache' else \
            XDG_DATA_HOME if location == 'data' else \
            XDG_CONFIG_HOME if location == 'config' else \
            getcwd()
    is_url = url_or_name.startswith('https://') or url_or_name.startswith('http://')
    find_kwargs = {'executable': executable}
    find_kwargs['url' if is_url else 'name'] = url_or_name
    reslist = resmgr.find_resources(**find_kwargs)
    if not reslist:
        log.info("No resources found in registry")
        if is_url and any_url:
            log.info("Downloading unregistered resource %s" % url_or_name)
            fpath = resmgr.download(executable, url_or_name, overwrite=overwrite, basedir=basedir)
            log.info("Downloaded %s to %s" % (url_or_name, fpath))
            log.info("Use in parameters as '%s'" % fpath.name)
        else:
            sys.exit(1)
    else:
        for _, resdict in reslist:
            fpath = resmgr.download(
                executable,
                resdict['url'],
                name=resdict['name'],
                type=resdict['type'],
                path_in_archive=resdict.get('path_in_archive', '.'),
                overwrite=overwrite,
                basedir=basedir
            )
            log.info("Downloaded %s to %s" % (resdict['url'], fpath))
            log.info("Use in parameters as '%s'" % resmgr.parameter_usage(resdict['name'], usage=resdict['parameter_usage']))

