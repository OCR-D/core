import sys
from contextlib import redirect_stdout
from io import StringIO
from typing import Type

import click
import uvicorn

from ocrd.server.main import ProcessorAPI
from ocrd_utils import getLogger, initLogging
from ocrd_utils import (
    set_json_key_value_overrides, parse_json_string_with_comments,
)
from ocrd_validators import WorkspaceValidator
from ocrd.decorators.loglevel_option import ocrd_loglevel
from ocrd.decorators.mets_find_options import mets_find_options
from ocrd.decorators.ocrd_cli_options import ocrd_cli_options
from ocrd.decorators.parameter_option import parameter_option, parameter_override_option
from ocrd.helpers import parse_server_input, parse_version_string
from ocrd.processor.base import run_processor, Processor
from ocrd.resolver import Resolver


def ocrd_cli_wrap_processor(
        processorClass: Type[Processor],
        ocrd_tool=None,
        mets=None,
        working_dir=None,
        server=None,
        dump_json=False,
        dump_module_dir=False,
        help=False,  # pylint: disable=redefined-builtin
        profile=False,
        profile_file=None,
        version=False,
        overwrite=False,
        show_resource=None,
        list_resources=False,
        **kwargs
):
    if not sys.argv[1:]:
        processorClass(workspace=None, show_help=True)
        sys.exit(1)
    if dump_json or dump_module_dir or help or version or show_resource or list_resources:
        processorClass(
            workspace=None,
            dump_json=dump_json,
            dump_module_dir=dump_module_dir,
            show_help=help,
            show_version=version,
            show_resource=show_resource,
            list_resources=list_resources
        )
        sys.exit()
    if server:
        try:
            ip, port, mongo_url = parse_server_input(server)
        except ValueError:
            raise click.UsageError('The --server option must have the format IP:PORT:MONGO_URL')

        initLogging()

        # Read the ocrd_tool object
        f1 = StringIO()
        with redirect_stdout(f1):
            processorClass(workspace=None, dump_json=True)
        ocrd_tool = parse_json_string_with_comments(f1.getvalue())

        # Read the version string
        f2 = StringIO()
        with redirect_stdout(f2):
            processorClass(workspace=None, show_version=True)
        version = parse_version_string(f2.getvalue())

        # Start the server
        app = ProcessorAPI(
            title=ocrd_tool['executable'],
            description=ocrd_tool['description'],
            version=version,
            ocrd_tool=ocrd_tool,
            db_url=mongo_url,
            processor_class=processorClass
        )

        uvicorn.run(app, host=ip, port=port, access_log=False)
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
        report = WorkspaceValidator.check_file_grp(workspace, kwargs['input_file_grp'],
                                                   '' if overwrite else kwargs['output_file_grp'], page_id)
        if not report.is_valid:
            raise Exception("Invalid input/output file grps:\n\t%s" % '\n\t'.join(report.errors))
        if profile or profile_file:
            import cProfile
            import pstats
            import io
            import atexit
            print("Profiling...")
            pr = cProfile.Profile()
            pr.enable()

            def exit():
                pr.disable()
                print("Profiling completed")
                if profile_file:
                    with open(profile_file, 'wb') as f:
                        pr.dump_stats(profile_file)
                s = io.StringIO()
                pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats()
                print(s.getvalue())

            atexit.register(exit)
        run_processor(processorClass, ocrd_tool, mets, workspace=workspace, **kwargs)
