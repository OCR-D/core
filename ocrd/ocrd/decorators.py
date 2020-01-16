from os.path import isfile

import click

from ocrd_utils import (
    is_local_filename,
    get_local_filename,
    setOverrideLogLevel,
    parse_json_string_or_file,

    VERSION as OCRD_VERSION
)

from ocrd_utils import getLogger
from .resolver import Resolver
from .processor.base import run_processor
from ocrd_validators import WorkspaceValidator

def _set_root_logger_version(ctx, param, value):    # pylint: disable=unused-argument
    setOverrideLogLevel(value)
    return value

loglevel_option = click.option('-l', '--log-level', help="Log level",
                               type=click.Choice(['OFF', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']),
                               default=None, callback=_set_root_logger_version)

parameter_option = click.option('-p', '--parameter',
                                help="Parameters, either JSON string or path to JSON file",
                                default='{}',
                                callback=lambda ctx, param, value: parse_json_string_or_file(value))

def ocrd_cli_wrap_processor(processorClass, ocrd_tool=None, mets=None, working_dir=None, dump_json=False, help=False, version=False, **kwargs):
    LOG = getLogger('ocrd_cli_wrap_processor')
    if dump_json:
        processorClass(workspace=None, dump_json=True)
    elif help:
        processorClass(workspace=None, show_help=True)
    elif version:
        try:
            p = processorClass(workspace=None)
        except Exception: # pylint: disable=bare-except
            pass
        print("Version %s, ocrd/core %s" % (p.version, OCRD_VERSION))
    elif mets is None:
        msg = 'Error: Missing option "-m" / "--mets".'
        LOG.error(msg)
        raise Exception(msg)
    else:
        if is_local_filename(mets) and not isfile(get_local_filename(mets)):
            msg = "File does not exist: %s" % mets
            LOG.error(msg)
            raise Exception(msg)
        resolver = Resolver()
        workspace = resolver.workspace_from_url(mets, working_dir)
        # TODO once we implement 'overwrite' CLI option and mechanism, disable the
        # `output_file_grp_ check by setting to False-y value if 'overwrite' is set
        report = WorkspaceValidator.check_file_grp(workspace, kwargs['input_file_grp'], kwargs['output_file_grp'])
        if not report.is_valid:
            raise Exception("Invalid input/output file grps:\n\t%s" % '\n\t'.join(report.errors))
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
        click.option('-m', '--mets', help="METS to process", default="mets.xml"),
        click.option('-w', '--working-dir', help="Working Directory"),
        click.option('-I', '--input-file-grp', help='File group(s) used as input.', default='INPUT'),
        click.option('-O', '--output-file-grp', help='File group(s) used as output.', default='OUTPUT'),
        click.option('-g', '--page-id', help="ID(s) of the pages to process"),
        parameter_option,
        click.option('-J', '--dump-json', help="Dump tool description as JSON and exit", is_flag=True, default=False),
        loglevel_option,
        click.option('-V', '--version', help="Show version", is_flag=True, default=False),
        click.option('-h', '--help', help="This help message", is_flag=True, default=False),
    ]
    for param in params:
        param(f)
    return f
