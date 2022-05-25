from os.path import isfile
import sys
from typing import Type

import click

from ocrd_utils import (
    is_local_filename,
    get_local_filename,
    set_json_key_value_overrides,
)

from ocrd_utils import getLogger, initLogging
from ocrd_validators import WorkspaceValidator

from ..resolver import Resolver
from ..processor.base import run_processor, Processor

from .loglevel_option import ocrd_loglevel
from .parameter_option import parameter_option, parameter_override_option
from .ocrd_cli_options import ocrd_cli_options
from .mets_find_options import mets_find_options
from ..server.config import Config


def ocrd_cli_wrap_processor(
    processorClass: Type[Processor],
    ocrd_tool=None,
    mets=None,
    working_dir=None,
    server_ip=None,
    server_port=None,
    mongo_url=None,
    dump_json=False,
    help=False, # pylint: disable=redefined-builtin
    version=False,
    overwrite=False,
    show_resource=None,
    list_resources=False,
    **kwargs
):
    if not sys.argv[1:]:
        processorClass(workspace=None, show_help=True)
        sys.exit(1)
    if dump_json or help or version or show_resource or list_resources:
        processorClass(
            workspace=None,
            dump_json=dump_json,
            show_help=help,
            show_version=version,
            show_resource=show_resource,
            list_resources=list_resources
        )
        sys.exit()
    if server_ip or server_port:
        # IP provided without port
        if server_ip and not server_port:
            raise click.UsageError('--server-port is missing.')

        # Port is provided without IP
        if server_port and not server_ip:
            raise click.UsageError('--server-ip is missing.')

        # IP and port but without database
        if server_ip and server_port and not mongo_url:
            raise click.UsageError('--mongo-url is missing.')

        # Proceed when both IP and port are provided
        initLogging()

        # Init a processor instance to get access to its information
        processor = processorClass(workspace=None)

        # Set collection name to the processor name
        Config.collection_name = processor.ocrd_tool['executable']

        # Set other meta-data
        Config.processor_class = processorClass
        Config.title = processor.ocrd_tool['executable']
        Config.description = processor.ocrd_tool['description']
        Config.version = processor.version
        Config.ocrd_tool = processor.ocrd_tool
        Config.db_url = mongo_url

        # Start the server
        from ocrd.server.main import app
        import uvicorn
        uvicorn.run(app, host=server_ip, port=server_port, access_log=False)
    else:
        initLogging()
        LOG = getLogger('ocrd_cli_wrap_processor')
        # LOG.info('kwargs=%s' % kwargs)
        # Merge parameter overrides and parameters
        if 'parameter_override' in kwargs:
            set_json_key_value_overrides(kwargs['parameter'], *kwargs['parameter_override'])
        # TODO OCR-D/core#274
        # Assert -I / -O
        # if not kwargs['input_file_grp']:
        #     raise ValueError('-I/--input-file-grp is required')
        # if not kwargs['output_file_grp']:
        #     raise ValueError('-O/--output-file-grp is required')
        resolver = Resolver()
        working_dir, mets, _ = resolver.resolve_mets_arguments(working_dir, mets, None)
        workspace = resolver.workspace_from_url(mets, working_dir)
        page_id = kwargs.get('page_id')
        # XXX not possible while processors do not adhere to # https://github.com/OCR-D/core/issues/505
        # if overwrite
        #     if 'output_file_grp' not in kwargs or not kwargs['output_file_grp']:
        #         raise Exception("--overwrite requires --output-file-grp")
        #     LOG.info("Removing files because of --overwrite")
        #     for grp in kwargs['output_file_grp'].split(','):
        #         if page_id:
        #             for one_page_id in kwargs['page_id'].split(','):
        #                 LOG.debug("Removing files in output file group %s with page ID %s", grp, one_page_id)
        #                 for file in workspace.mets.find_files(pageId=one_page_id, fileGrp=grp):
        #                     workspace.remove_file(file, force=True, keep_file=False, page_recursive=True)
        #         else:
        #             LOG.debug("Removing all files in output file group %s ", grp)
        #             # TODO: can be reduced to `page_same_group=True` as soon as core#505 has landed (in all processors)
        #             workspace.remove_file_group(grp, recursive=True, force=True, keep_files=False, page_recursive=True, page_same_group=False)
        #     workspace.save_mets()
        # XXX While https://github.com/OCR-D/core/issues/505 is open, set 'overwrite_mode' globally on the workspace
        if overwrite:
            workspace.overwrite_mode = True
        report = WorkspaceValidator.check_file_grp(workspace, kwargs['input_file_grp'], '' if overwrite else kwargs['output_file_grp'], page_id)
        if not report.is_valid:
            raise Exception("Invalid input/output file grps:\n\t%s" % '\n\t'.join(report.errors))
        run_processor(processorClass, ocrd_tool, mets, workspace=workspace, **kwargs)
