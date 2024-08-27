import sys

from ocrd_utils import (
    config,
    initLogging,
    is_local_filename,
    get_local_filename,
    getLogger,
    parse_json_string_with_comments,
    set_json_key_value_overrides,
    parse_json_string_or_file,
)
from ocrd_validators import WorkspaceValidator
from ocrd_network import ProcessingWorker, ProcessorServer, AgentType

from ..resolver import Resolver
from ..processor.base import ResourceNotFoundError, run_processor

from .loglevel_option import ocrd_loglevel
from .parameter_option import parameter_option, parameter_override_option
from .ocrd_cli_options import ocrd_cli_options
from .mets_find_options import mets_find_options

SUBCOMMANDS = [AgentType.PROCESSING_WORKER, AgentType.PROCESSOR_SERVER]


def ocrd_cli_wrap_processor(
    processorClass,
    mets=None,
    mets_server_url=None,
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
    subcommand=None,
    address=None,
    queue=None,
    log_filename=None,
    database=None,
    # ocrd_network params end #
    **kwargs
):
    if not sys.argv[1:]:
        processorClass(None, show_help=True)
        sys.exit(1)
    if dump_json or dump_module_dir or help or version or show_resource or list_resources:
        processorClass(
            None,
            dump_json=dump_json,
            dump_module_dir=dump_module_dir,
            show_help=help,
            subcommand=subcommand,
            show_version=version,
            show_resource=show_resource,
            list_resources=list_resources
        )
        sys.exit()
    if subcommand:
        # Used for checking/starting network agents for the WebAPI architecture
        check_and_run_network_agent(processorClass, subcommand, address, database, queue)
    elif address or queue or database:
        raise ValueError(f"Subcommand options --address --queue and --database are only valid for subcommands: {SUBCOMMANDS}")

    initLogging()

    LOG = getLogger('ocrd.cli_wrap_processor')
    assert kwargs['input_file_grp'] is not None
    assert kwargs['output_file_grp'] is not None
    # LOG.info('kwargs=%s' % kwargs)
    if 'parameter' in kwargs:
        # Disambiguate parameter file/literal, and resolve file
        # (but avoid entering processing context of constructor)
        class DisposableSubclass(processorClass):
            def show_version(self):
                pass
        disposable = DisposableSubclass(None, show_version=True)
        def resolve(name):
            try:
                return disposable.resolve_resource(name)
            except ResourceNotFoundError:
                return None
        kwargs['parameter'] = parse_json_string_or_file(*kwargs['parameter'],
                                                        resolve_preset_file=resolve)
    else:
        kwargs['parameter'] = dict()
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
    working_dir, mets, _, mets_server_url = \
            resolver.resolve_mets_arguments(working_dir, mets, None, mets_server_url)
    workspace = resolver.workspace_from_url(mets, working_dir, mets_server_url=mets_server_url)
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
    if not profile and 'CPU' in config.OCRD_PROFILE:
        profile = True
    if not profile_file and config.is_set('OCRD_PROFILE_FILE'):
        profile_file = config.OCRD_PROFILE_FILE
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


def check_and_run_network_agent(ProcessorClass, subcommand: str, address: str, database: str, queue: str):
    """
    """
    if subcommand not in SUBCOMMANDS:
        raise ValueError(f"SUBCOMMAND can only be one of {SUBCOMMANDS}")

    if not database:
        raise ValueError(f"Option '--database' is invalid for subcommand {subcommand}")

    if subcommand == AgentType.PROCESSOR_SERVER:
        if not address:
            raise ValueError(f"Option '--address' required for subcommand {subcommand}")
        if queue:
            raise ValueError(f"Option '--queue' invalid for subcommand {subcommand}")
    if subcommand == AgentType.PROCESSING_WORKER:
        if address:
            raise ValueError(f"Option '--address' invalid for subcommand {subcommand}")
        if not queue:
            raise ValueError(f"Option '--queue' required for subcommand {subcommand}")

    processor = ProcessorClass(workspace=None)
    if subcommand == AgentType.PROCESSING_WORKER:
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
    elif subcommand == AgentType.PROCESSOR_SERVER:
        # TODO: Better validate that inside the ProcessorServer itself
        host, port = address.split(':')
        processor_server = ProcessorServer(
            mongodb_addr=database,
            processor_name=processor.ocrd_tool['executable'],
            processor_class=ProcessorClass,
        )
        processor_server.run_server(host=host, port=int(port))
    else:
        raise ValueError(f"Unknown network agent type, must be one of: {SUBCOMMANDS}")
    sys.exit(0)
