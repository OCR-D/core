from os.path import isfile
from os import environ
import sys
from contextlib import redirect_stdout
from io import StringIO

import click

from ocrd_utils import (
    is_local_filename,
    get_local_filename,
    set_json_key_value_overrides,
)

from ocrd_utils import getLogger, initLogging, parse_json_string_with_comments
from ocrd_validators import WorkspaceValidator

from ocrd_network import ProcessingWorker, ProcessorServer

from ..resolver import Resolver
from ..processor.base import run_processor

from .loglevel_option import ocrd_loglevel
from .parameter_option import parameter_option, parameter_override_option
from .ocrd_cli_options import ocrd_cli_options
from .mets_find_options import mets_find_options

def ocrd_cli_wrap_processor(
    processorClass,
    mets=None,
    working_dir=None,
    dump_json=False,
    dump_module_dir=False,
    help=False, # pylint: disable=redefined-builtin
    profile=False,
    profile_file=None,
    version=False,
    overwrite=False,
    show_resource=None,
    list_resources=False,
    # ocrd_network params start #
    agent_type=None,
    agent_address=None,
    queue=None,
    database=None,
    # ocrd_network params end #
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

    initLogging()

    # Used for checking/starting network agents for the WebAPI architecture
    # Has no side effects if neither of the 4 ocrd_network parameters are passed
    check_and_run_network_agent(processorClass, agent_type, agent_address, database, queue)

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
    # Set up profiling behavior from environment variables/flags
    if not profile and 'OCRD_PROFILE' in environ:
        if 'CPU' in environ['OCRD_PROFILE']:
            profile = True
    if not profile_file and 'OCRD_PROFILE_FILE' in environ:
        profile_file = environ['OCRD_PROFILE_FILE']
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
    run_processor(processorClass, mets_url=mets, workspace=workspace, **kwargs)


def check_and_run_network_agent(ProcessorClass, agent_type: str, agent_address: str, database: str, queue: str):
    if not agent_type and (agent_address or database or queue):
        raise ValueError("Options '--database', '--queue', and 'agent_address' are valid only with '--agent_type'")
    if agent_type:
        if not database:
            raise ValueError("Options '--agent_type' and '--database' are mutually inclusive")
        allowed_agent_types = ['server', 'worker']
        if agent_type not in allowed_agent_types:
            agents_str = ', '.join(allowed_agent_types)
            raise ValueError(f"Wrong agent type parameter. Allowed agent types: {agents_str}")
        if agent_type == 'server':
            if not agent_address:
                raise ValueError("Options '--agent_type=server' and '--agent_address' are mutually inclusive")
            if queue:
                raise ValueError("Options '--agent_type=server' and '--queue' are mutually exclusive")
        if agent_type == 'worker':
            if not queue:
                raise ValueError("Options '--agent_type=worker' and '--queue' are mutually inclusive")
            if agent_address:
                raise ValueError("Options '--agent_type=worker' and '--agent_address' are mutually exclusive")

        processor = ProcessorClass(workspace=None, dump_json=True)
        if agent_type == 'worker':
            try:
                # TODO: Passing processor_name and ocrd_tool is reduntant
                processing_worker = ProcessingWorker(
                    rabbitmq_addr=queue,
                    mongodb_addr=database,
                    processor_name=processor.ocrd_tool['executable'],
                    ocrd_tool=processor.ocrd_tool,
                    processor_class=ProcessorClass,
                )
                # The RMQConsumer is initialized and a connection to the RabbitMQ is performed
                processing_worker.connect_consumer()
                # Start consuming from the queue with name `processor_name`
                processing_worker.start_consuming()
            except Exception as e:
                sys.exit(f"Processing worker has failed with error: {e}")
        if agent_type == 'server':
            try:
                # TODO: Better validate that inside the ProcessorServer itself
                host, port = agent_address.split(':')
                processor_server = ProcessorServer(
                    mongodb_addr=database,
                    processor_name=processor.ocrd_tool['executable'],
                    processor_class=ProcessorClass,
                )
                processor_server.run_server(host=host, port=int(port))
            except Exception as e:
                sys.exit(f"Processor server has failed with error: {e}")
