"""
OCR-D CLI: management of processor resources

.. click:: ocrd.cli.resmgr:resmgr_cli
    :prog: ocrd resmgr
    :nested: full
"""
import sys
from os import environ
from pathlib import Path
from distutils.spawn import find_executable as which
from yaml import safe_load, safe_dump

import requests
import click

from ocrd_utils import (
    initLogging,
    directory_size,
    getLogger,
    get_ocrd_tool_json,
    get_moduledir,
    RESOURCE_LOCATIONS,
)
from ocrd.constants import RESOURCE_USER_LIST_COMMENT

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
@click.option('-D', '--no-dynamic', is_flag=True, default=False, help="Whether to skip looking into each processor's --dump-{json,module-dir} for module-level resources")
@click.option('-e', '--executable', help='Show only resources for executable beginning with EXEC', metavar='EXEC', default='ocrd-*')
def list_available(executable, no_dynamic):
    """
    List available resources
    """
    resmgr = OcrdResourceManager()
    for executable, reslist in resmgr.list_available(executable=executable, dynamic=not no_dynamic):
        print_resources(executable, reslist, resmgr)

@resmgr_cli.command('list-installed')
@click.option('-e', '--executable', help='Show only resources for executable EXEC', metavar='EXEC')
def list_installed(executable=None):
    """
    List installed resources
    """
    resmgr = OcrdResourceManager()
    for executable, reslist in resmgr.list_installed(executable):
        print_resources(executable, reslist, resmgr)

@resmgr_cli.command('download')
@click.option('-n', '--any-url', help='URL of unregistered resource to download/copy from', default='')
@click.option('-D', '--no-dynamic', is_flag=True, default=False, help="Whether to skip looking into each processor's --dump-{json,module-dir} for module-level resources")
@click.option('-t', '--resource-type', help='Type of resource', type=click.Choice(['file', 'directory', 'archive']), default='file')
@click.option('-P', '--path-in-archive', help='Path to extract in case of archive type', default='.')
@click.option('-a', '--allow-uninstalled', help="Allow installing resources for uninstalled processors", is_flag=True)
@click.option('-o', '--overwrite', help='Overwrite existing resources', is_flag=True)
@click.option('-l', '--location', help="Where to store resources - defaults to first location in processor's 'resource_locations' list or finally 'data'", type=click.Choice(RESOURCE_LOCATIONS))
@click.argument('executable', required=True)
@click.argument('name', required=False)
def download(any_url, no_dynamic, resource_type, path_in_archive, allow_uninstalled, overwrite, location, executable, name):
    """
    Download resource NAME for processor EXECUTABLE.

    NAME is the name of the resource made available by downloading or copying.

    If NAME is '*' (asterisk), then download all known registered resources for this processor.

    If ``--any-url=URL`` or ``-n URL`` is given, then URL is accepted regardless of registered resources for ``NAME``.
    (This can be used for unknown resources or for replacing registered resources.)

    If ``--resource-type`` is set to `archive`, then that archive gets unpacked after download,
    and its ``--path-in-archive`` will subsequently be renamed to NAME.
    """
    log = getLogger('ocrd.cli.resmgr')
    resmgr = OcrdResourceManager()
    if executable != '*' and not name:
        log.error("Unless EXECUTABLE ('%s') is the '*' wildcard, NAME is required" % executable)
        sys.exit(1)
    elif executable == '*':
        executable = None
    if name == '*':
        name = None
    is_url = (any_url.startswith('https://') or any_url.startswith('http://')) if any_url else False
    is_filename = Path(any_url).exists() if any_url else False
    if executable and not which(executable):
        if not allow_uninstalled:
            log.error("Executable '%s' is not installed. " \
                      "To download resources anyway, use the -a/--allow-uninstalled flag", executable)
            sys.exit(1)
        else:
            log.info("Executable %s is not installed, but " \
                     "downloading resources anyway", executable)
    reslist = resmgr.list_available(executable=executable, dynamic=not no_dynamic, name=name)
    if not any(r[1] for r in reslist):
        log.info(f"No resources {name} found in registry for executable {executable}")
        if executable and name:
            reslist = [(executable, [{'url': any_url or '???', 'name': name,
                                     'type': resource_type,
                                     'path_in_archive': path_in_archive}])]
    for this_executable, this_reslist in reslist:
        for resdict in this_reslist:
            if 'size' in resdict:
                registered = "registered"
            else:
                registered = "unregistered"
            if any_url:
                resdict['url'] = any_url
            if resdict['url'] == '???':
                log.warning("Cannot download user resource %s", resdict['name'])
                continue
            if resdict['url'].startswith('https://') or resdict['url'].startswith('http://'):
                log.info("Downloading %s resource '%s' (%s)", registered, resdict['name'], resdict['url'])
                if 'size' not in resdict:
                    with requests.head(resdict['url']) as r:
                        resdict['size'] = int(r.headers.get('content-length', 0))
            else:
                log.info("Copying %s resource '%s' (%s)", registered, resdict['name'], resdict['url'])
                urlpath = Path(resdict['url'])
                resdict['url'] = str(urlpath.resolve())
                if Path(urlpath).is_dir():
                    resdict['size'] = directory_size(urlpath)
                else:
                    resdict['size'] = urlpath.stat().st_size
            if not location:
                location = get_ocrd_tool_json(this_executable)['resource_locations'][0]
            elif location not in get_ocrd_tool_json(this_executable)['resource_locations']:
                log.error("The selected --location {location} is not in the {this_executable}'s resource search path, refusing to install to invalid location")
                sys.exit(1)
            if location != 'module':
                basedir = resmgr.location_to_resource_dir(location)
            else:
                basedir = get_moduledir(this_executable)
                if not basedir:
                    basedir = resmgr.location_to_resource_dir('data')

            try:
                with click.progressbar(length=resdict['size']) as bar:
                    fpath = resmgr.download(
                        this_executable,
                        resdict['url'],
                        name=resdict['name'],
                        resource_type=resdict.get('type', resource_type),
                        path_in_archive=resdict.get('path_in_archive', path_in_archive),
                        overwrite=overwrite,
                        no_subdir=location in ['cwd', 'module'],
                        basedir=basedir,
                        progress_cb=lambda delta: bar.update(delta)
                    )
                if registered == 'unregistered':
                    log.info("%s resource '%s' (%s) not a known resource, creating stub in %s'", this_executable, name, any_url, resmgr.user_list)
                    resmgr.add_to_user_database(this_executable, fpath, url=any_url)
                resmgr.save_user_list()
                log.info("Installed resource %s under %s", resdict['url'], fpath)
            except FileExistsError as exc:
                log.info(str(exc))
            log.info("Use in parameters as '%s'", resmgr.parameter_usage(resdict['name'], usage=resdict.get('parameter_usage', 'as-is')))

@resmgr_cli.command('migrate')
@click.argument('migration', type=click.Choice(['2.37.0']))
def migrate(migration):
    """
    Update the configuration after updating core to MIGRATION
    """
    resmgr = OcrdResourceManager(skip_init=True)
    log = getLogger('ocrd.resmgr.migrate')
    if not resmgr.user_list.exists():
        log.info(f'No configuration file found at {resmgr.user_list}, nothing to do')
    if migration == '2.37.0':
        backup_file = resmgr.user_list.with_suffix(f'.yml.before-{migration}')
        yaml_in_str = resmgr.user_list.read_text()
        log.info(f'Backing {resmgr.user_list} to {backup_file}')
        backup_file.write_text(yaml_in_str)
        log.info(f'Applying migration {migration} to {resmgr.user_list}')
        yaml_in = safe_load(yaml_in_str)
        yaml_out = {}
        for executable, reslist_in in yaml_in.items():
            yaml_out[executable] = []
            for resdict_in in reslist_in:
                resdict_out = {}
                for k_in, v_in in resdict_in.items():
                    k_out, v_out = k_in, v_in
                    if k_in == 'type' and v_in in ['github-dir', 'tarball']:
                        if v_in == 'github-dir':
                            v_out = 'directory'
                        elif v_in == 'tarball':
                            v_out = 'directory'
                    resdict_out[k_out] = v_out
                yaml_out[executable].append(resdict_out)
        resmgr.user_list.write_text(RESOURCE_USER_LIST_COMMENT +
                '\n# migrated with ocrd resmgr migrate {migration}\n' +
                safe_dump(yaml_out))
        log.info(f'Applied migration {migration} to {resmgr.user_list}')
