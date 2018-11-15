import os

import click

from ocrd.constants import VERSION as OCRD_VERSION
from ocrd.resolver import Resolver
from ocrd.processor.base import run_processor
from ocrd.logging import setOverrideLogLevel

def _set_root_logger_version(ctx, param, value):    # pylint: disable=unused-argument
    setOverrideLogLevel(value)
    return value

loglevel_option = click.option('-l', '--log-level', help="Log level",
                               type=click.Choice(['OFF', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']),
                               default=None, callback=_set_root_logger_version)

def ocrd_cli_wrap_processor(processorClass, ocrd_tool=None, mets=None, working_dir=None, dump_json=False, version=False, **kwargs):
    if dump_json:
        processorClass(workspace=None, dump_json=True)
    elif version:
        p = processorClass(workspace=None)
        print("Version %s, ocrd/core %s" % (p.version, OCRD_VERSION))
    elif mets is None:
        raise Exception('Error: Missing option "-m" / "--mets".')
    else:
        if mets.find('://') == -1:
            mets = 'file://' + os.path.abspath(mets)
        if mets.startswith('file://') and not os.path.exists(mets[len('file://'):]):
            raise Exception("File does not exist: %s" % mets)
        resolver = Resolver()
        workspace = resolver.workspace_from_url(mets, working_dir)
        run_processor(processorClass, ocrd_tool, mets, workspace=workspace, **kwargs)

def ocrd_loglevel(f):
    """
    Add an option '--log-level' to set the log level.
    """
    loglevel_option(f)
    return f

def ocrd_cli_options(f):
    """
    Implement MP CLI.

    Usage::

        import ocrd_click_cli from ocrd.utils

        @click.command()
        @ocrd_click_cli
        def cli(mets_url):
            print(mets_url)
    """
    params = [
        click.option('-m', '--mets', help="METS URL to validate"),
        click.option('-w', '--working-dir', help="Working Directory"),
        click.option('-I', '--input-file-grp', help='File group(s) used as input.', default='INPUT'),
        click.option('-O', '--output-file-grp', help='File group(s) used as output.', default='OUTPUT'),
        click.option('-g', '--group-id', help="mets:file GROUPID"),
        click.option('-p', '--parameter', type=click.Path()),
        click.option('-J', '--dump-json', help="Dump tool description as JSON and exit", is_flag=True, default=False),
        loglevel_option,
        click.option('-V', '--version', help="Show version", is_flag=True, default=False)
    ]
    for param in params:
        param(f)
    return f
