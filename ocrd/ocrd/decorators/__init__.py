from os.path import isfile
import sys

import click

from ocrd_utils import (
    is_local_filename,
    get_local_filename,
    set_json_key_value_overrides,
)

from ocrd_utils import getLogger, initLogging
from ocrd_validators import WorkspaceValidator

from ..resolver import Resolver
from ..processor.base import run_processor

from .loglevel_option import ocrd_loglevel
from .parameter_option import parameter_option, parameter_override_option
from .ocrd_cli_options import ocrd_cli_options

def ocrd_cli_wrap_processor(
    processorClass,
    ocrd_tool=None,
    mets=None,
    working_dir=None,
    dump_json=False,
    help=False, # pylint: disable=redefined-builtin
    version=False,
    overwrite=False,
    **kwargs
):
    if not sys.argv[1:]:
        processorClass(workspace=None, show_help=True)
        sys.exit(1)
    if dump_json or help or version:
        processorClass(workspace=None, dump_json=dump_json, show_help=help, show_version=version)
        sys.exit()
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
        if is_local_filename(mets) and not isfile(get_local_filename(mets)):
            msg = "File does not exist: %s" % mets
            LOG.error(msg)
            raise Exception(msg)
        resolver = Resolver()
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
