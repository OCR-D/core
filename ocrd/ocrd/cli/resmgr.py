"""
OCR-D CLI: management of processor resources

.. click:: ocrd.cli.resmgr:resmgr_cli
    :prog: ocrd resmgr
    :nested: full
"""
import sys
from pathlib import Path
from distutils.spawn import find_executable as which

import requests
import click

from ocrd_utils import (
    initLogging,
    getLogger,
    RESOURCE_LOCATIONS
)

from ..resource_manager import OcrdResourceManager

def print_resources(executable, reslist, resmgr):
    print('%s' % executable)
    for resdict in reslist:
        print('- %s %s (%s)\n  %s' % (
            resdict['name'],
            '@ %s' % resmgr.resource_dir_to_location(resdict['path']) if 'path' in resdict else '',
            resdict['url'],
            resdict['description']
        ))
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
        print_resources(executable, reslist, resmgr)

@resmgr_cli.command('list-installed')
@click.option('-e', '--executable', help='Show only resources for executable EXEC', metavar='EXEC')
def list_installed(executable=None):
    """
    List installed resources
    """
    resmgr = OcrdResourceManager()
    ret = []
    for executable, reslist in resmgr.list_installed(executable):
        print_resources(executable, reslist, resmgr)

@resmgr_cli.command('download')
@click.option('-n', '--any-url', help='Allow downloading/copying unregistered resources', is_flag=True)
@click.option('-a', '--allow-uninstalled', help="Allow installing resources for uninstalled processors", is_flag=True)
@click.option('-o', '--overwrite', help='Overwrite existing resources', is_flag=True)
@click.option('-l', '--location', help='Where to store resources', type=click.Choice(RESOURCE_LOCATIONS), default='data', show_default=True)
@click.argument('executable', required=True)
@click.argument('url_or_name', required=False)
def download(any_url, allow_uninstalled, overwrite, location, executable, url_or_name):
    """
    Download resource URL_OR_NAME for processor EXECUTABLE.

    URL_OR_NAME can either be the ``name`` or ``url`` of a registered resource.

    If URL_OR_NAME is '*' (asterisk), download all known resources for this processor

    If ``--any-url`` is given, also accepts URL or filenames of non-registered resources for ``URL_OR_NAME``.
    """
    log = getLogger('ocrd.cli.resmgr')
    resmgr = OcrdResourceManager()
    basedir = resmgr.location_to_resource_dir(location)
    if executable != '*' and not url_or_name:
        log.error("Unless EXECUTABLE ('%s') is the '*' wildcard, URL_OR_NAME is required" % executable)
        sys.exit(1)
    elif executable == '*':
        executable = None
    is_url = (url_or_name.startswith('https://') or url_or_name.startswith('http://')) if url_or_name else False
    is_filename = Path(url_or_name).exists() if url_or_name else False
    if executable and not which(executable):
        if not allow_uninstalled:
            log.error("Executable %s is not installed. Is there a typo in the executable? " \
                "To install resources for uninstalled processor, use the -a/--allow-uninstalled flag" % executable)
            sys.exit(1)
        else:
            log.warning("Executable %s is not installed but -a/--allow-uninstalled was given, so proceeding" % executable)
    find_kwargs = {'executable': executable}
    if url_or_name and url_or_name != '*':
        find_kwargs['url' if is_url else 'name'] = url_or_name
    reslist = resmgr.find_resources(**find_kwargs)
    if not reslist:
        log.info("No resources found in registry")
        if any_url and (is_url or is_filename):
            log.info("%s unregistered resource %s" % ("Downloading" if is_url else "Copying", url_or_name))
            if is_url:
                with requests.get(url_or_name, stream=True) as r:
                    content_length = int(r.headers.get('content-length'))
            else:
                url_or_name = str(Path(url_or_name).resolve())
                content_length = Path(url_or_name).stat().st_size
            with click.progressbar(length=content_length, label="Downloading" if is_url else "Copying") as bar:
                fpath = resmgr.download(
                    executable,
                    url_or_name,
                    overwrite=overwrite,
                    basedir=basedir,
                    no_subdir=location == 'cwd',
                    progress_cb=lambda delta: bar.update(delta))
            log.info("%s resource '%s' (%s) not a known resource, creating stub in %s'" % (executable, fpath.name, url_or_name, resmgr.user_list))
            resmgr.add_to_user_database(executable, fpath, url_or_name)
            log.info("%s %s to %s" % ("Downloaded" if is_url else "Copied", url_or_name, fpath))
            log.info("Use in parameters as '%s'" % fpath.name)
        else:
            sys.exit(1)
    else:
        for executable, resdict in reslist:
            if not allow_uninstalled and not which(executable):
                log.info("Skipping installing resources for %s as it is not installed. (Use -a/--allow-uninstalled to force)")
                continue
            if resdict['url'] == '???':
                log.info("Cannot download user resource %s" % (resdict['name'])),
                continue
            log.info("Downloading resource %s" % resdict)
            with click.progressbar(length=resdict['size']) as bar:
                fpath = resmgr.download(
                    executable,
                    resdict['url'],
                    name=resdict['name'],
                    resource_type=resdict['type'],
                    path_in_archive=resdict.get('path_in_archive', '.'),
                    overwrite=overwrite,
                    size=resdict['size'],
                    no_subdir=location == 'cwd',
                    basedir=basedir,
                    progress_cb=lambda delta: bar.update(delta)
                )
            log.info("Downloaded %s to %s" % (resdict['url'], fpath))
            log.info("Use in parameters as '%s'" % resmgr.parameter_usage(resdict['name'], usage=resdict['parameter_usage']))

