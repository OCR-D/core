import sys
from contextlib import nullcontext

from ocrd_utils import (
    config,
    initLogging,
    is_local_filename,
    get_local_filename,
    getLogger,
    parse_json_string_with_comments,
    set_json_key_value_overrides,
    parse_json_string_or_file,
    redirect_stderr_and_stdout_to_file,
)
from ocrd_validators import WorkspaceValidator

from ..resolver import Resolver
from ..processor.base import ResourceNotFoundError, run_processor

from .loglevel_option import ocrd_loglevel
from .parameter_option import parameter_option, parameter_override_option
from .ocrd_cli_options import ocrd_cli_options
from .mets_find_options import mets_find_options


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
    debug=False,
    resolve_resource=None,
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
    # init logging handlers so no imported libs can preempt ours
    initLogging()

    # FIXME: remove workspace arg entirely
    processor = processorClass(None)
    if not sys.argv[1:]:
        processor.show_help(subcommand=subcommand)
        sys.exit(1)
    if help:
        processor.show_help(subcommand=subcommand)
        sys.exit()
    if version:
        processor.show_version()
        sys.exit()
    if dump_json:
        processor.dump_json()
        sys.exit()
    if dump_module_dir:
        processor.dump_module_dir()
        sys.exit()
    if resolve_resource:
        try:
            res = processor.resolve_resource(resolve_resource)
            print(res)
            sys.exit()
        except ResourceNotFoundError as e:
            log = getLogger('ocrd.processor.base')
            log.critical(e.message)
            sys.exit(1)
    if show_resource:
        try:
            processor.show_resource(show_resource)
            sys.exit()
        except ResourceNotFoundError as e:
            log = getLogger('ocrd.processor.base')
            log.critical(e.message)
            sys.exit(1)
    if list_resources:
        processor.list_resources()
        sys.exit()
    if subcommand or address or queue or database:
        # Used for checking/starting network agents for the WebAPI architecture
        check_and_run_network_agent(processorClass, subcommand, address, database, queue)

    if 'parameter' in kwargs:
        # Disambiguate parameter file/literal, and resolve file
        def resolve(name):
            try:
                return processor.resolve_resource(name)
            except ResourceNotFoundError:
                return None
        kwargs['parameter'] = parse_json_string_or_file(*kwargs['parameter'],
                                                        resolve_preset_file=resolve)
    else:
        kwargs['parameter'] = {}
    # Merge parameter overrides and parameters
    if 'parameter_override' in kwargs:
        set_json_key_value_overrides(kwargs['parameter'], *kwargs.pop('parameter_override'))
    # Assert -I / -O
    if not kwargs['input_file_grp']:
        raise ValueError('-I/--input-file-grp is required')
    if not kwargs['output_file_grp']:
        raise ValueError('-O/--output-file-grp is required')
    resolver = Resolver()
    working_dir, mets, _, mets_server_url = \
            resolver.resolve_mets_arguments(working_dir, mets, None, mets_server_url)
    workspace = resolver.workspace_from_url(mets, working_dir, mets_server_url=mets_server_url)
    page_id = kwargs.get('page_id')
    if debug:
        config.OCRD_MISSING_INPUT = 'ABORT'
        config.OCRD_MISSING_OUTPUT = 'ABORT'
        config.OCRD_EXISTING_OUTPUT = 'ABORT'
    if overwrite:
        config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
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
        def goexit():
            pr.disable()
            print("Profiling completed")
            if profile_file:
                pr.dump_stats(profile_file)
            s = io.StringIO()
            pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats()
            print(s.getvalue())
        atexit.register(goexit)
    if log_filename:
        log_ctx = redirect_stderr_and_stdout_to_file(log_filename)
    else:
        log_ctx = nullcontext()
    with log_ctx:
        run_processor(processorClass, mets_url=mets, workspace=workspace, **kwargs)


def check_and_run_network_agent(ProcessorClass, subcommand: str, address: str, database: str, queue: str):
    """
    """
    from ocrd_network import ProcessingWorker, ProcessorServer, AgentType
    SUBCOMMANDS = [AgentType.PROCESSING_WORKER, AgentType.PROCESSOR_SERVER]

    if not subcommand:
        raise ValueError(f"Subcommand options --address --queue and --database are only valid for subcommands: {SUBCOMMANDS}")
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
