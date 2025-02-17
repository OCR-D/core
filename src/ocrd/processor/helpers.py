"""
Helper methods for running and documenting processors
"""
from time import perf_counter, process_time
from os import times
from functools import lru_cache
import json
import inspect
from subprocess import run
from typing import List, Optional

from ..workspace import Workspace
from ocrd_utils import freeze_args, getLogger, config, setOverrideLogLevel, getLevelName, sparkline


__all__ = [
    'run_cli',
    'run_processor'
]


def _get_workspace(workspace=None, resolver=None, mets_url=None, working_dir=None, mets_server_url=None):
    if workspace is None:
        if resolver is None:
            raise Exception("Need to pass a resolver to create a workspace")
        if mets_url is None:
            raise Exception("Need to pass mets_url to create a workspace")
        workspace = resolver.workspace_from_url(mets_url, dst_dir=working_dir, mets_server_url=mets_server_url)
    return workspace

def run_processor(
        processorClass,
        mets_url=None,
        resolver=None,
        workspace=None,
        page_id=None,
        log_level=None,
        input_file_grp=None,
        output_file_grp=None,
        parameter=None,
        working_dir=None,
        mets_server_url=None,
        instance_caching=False
): # pylint: disable=too-many-locals
    """
    Instantiate a Pythonic processor, open a workspace, run the processor and save the workspace.

    If :py:attr:`workspace` is not none, reuse that. Otherwise, instantiate an
    :py:class:`~ocrd.Workspace` for :py:attr:`mets_url` (and :py:attr:`working_dir`)
    by using :py:meth:`ocrd.Resolver.workspace_from_url` (i.e. open or clone local workspace).

    Instantiate a Python object for :py:attr:`processorClass`, passing:
    - the workspace,
    - :py:attr:`page_id`
    - :py:attr:`input_file_grp`
    - :py:attr:`output_file_grp`
    - :py:attr:`parameter` (after applying any :py:attr:`parameter_override` settings)

    Run the processor on the workspace (creating output files in the filesystem).

    Finally, write back the workspace (updating the METS in the filesystem).

    If :py:attr:`instance_caching` is True, then processor instances (for the same set
    of :py:attr:`parameter` values) will be cached internally. Thus, these objects (and
    all their memory resources, like loaded models) get re-used instead of re-instantiated
    when a match occurs - as long as the program is being run. They only get deleted (and
    their resources freed) when as many as :py:data:`~ocrd_utils.config.OCRD_MAX_PROCESSOR_CACHE`
    instances have already been cached while this particular parameter set was re-used
    least frequently. (See :py:class:`~ocrd_network.ProcessingWorker` and
    :py:class:`~ocrd_network.ProcessorServer` for use-cases.)

    Args:
        processorClass (object): Python class of the module processor.
    """
    if log_level:
        setOverrideLogLevel(log_level)
    workspace = _get_workspace(
        workspace,
        resolver,
        mets_url,
        working_dir,
        mets_server_url
    )
    log = getLogger('ocrd.processor.helpers.run_processor')
    log.debug("Running processor %s", processorClass)

    processor = get_processor(
        processorClass,
        parameter=parameter,
        workspace=None,
        page_id=page_id,
        input_file_grp=input_file_grp,
        output_file_grp=output_file_grp,
        instance_caching=instance_caching
    )

    ocrd_tool = processor.ocrd_tool
    name = '%s v%s' % (ocrd_tool['executable'], processor.version)
    otherrole = ocrd_tool.get('steps', [''])[0]
    logProfile = getLogger('ocrd.process.profile')
    log.debug("Processor instance %s (%s doing %s)", processor, name, otherrole)
    t0_wall = perf_counter()
    t0_cpu = process_time()
    t0_os = times()
    if any(x in config.OCRD_PROFILE for x in ['RSS', 'PSS']):
        backend = 'psutil_pss' if 'PSS' in config.OCRD_PROFILE else 'psutil'
        from memory_profiler import memory_usage # pylint: disable=import-outside-toplevel
        try:
            mem_usage = memory_usage(proc=(processor.process_workspace, [workspace], {}),
                                     # only run process once
                                     max_iterations=1,
                                     interval=.1, timeout=None, timestamps=True,
                                     # include sub-processes
                                     multiprocess=True, include_children=True,
                                     # get proportional set size instead of RSS
                                     backend=backend)
        except Exception as err:
            log.exception("Failure in processor '%s'" % ocrd_tool['executable'])
            raise err
        mem_usage_values = [mem for mem, _ in mem_usage]
        mem_output = 'memory consumption: '
        mem_output += sparkline(mem_usage_values)
        mem_output += ' max: %.2f MiB min: %.2f MiB' % (max(mem_usage_values), min(mem_usage_values))
        logProfile.info(mem_output)
    else:
        try:
            processor.process_workspace(workspace)
        except Exception as err:
            log.exception("Failure in processor '%s'" % ocrd_tool['executable'])
            raise err

    t1_wall = perf_counter() - t0_wall
    t1_cpu = process_time() - t0_cpu
    t1_os = times()
    # add CPU time from child processes (page worker etc)
    t1_cpu += t1_os.children_user - t0_os.children_user
    t1_cpu += t1_os.children_system - t0_os.children_system
    logProfile.info(
        "Executing processor '%s' took %fs (wall) %fs (CPU)( "
        "[--input-file-grp='%s' --output-file-grp='%s' --parameter='%s' --page-id='%s']",
        ocrd_tool['executable'],
        t1_wall,
        t1_cpu,
        processor.input_file_grp or '',
        processor.output_file_grp or '',
        json.dumps(dict(processor.parameter or {})),
        processor.page_id or ''
    )
    workspace.mets.add_agent(
        name=name,
        _type='OTHER',
        othertype='SOFTWARE',
        role='OTHER',
        otherrole=otherrole,
        notes=[({'option': 'input-file-grp'}, processor.input_file_grp or ''),
               ({'option': 'output-file-grp'}, processor.output_file_grp or ''),
               ({'option': 'parameter'}, json.dumps(dict(processor.parameter or {}))),
               ({'option': 'page-id'}, processor.page_id or '')]
    )
    workspace.save_mets()
    return processor


def run_cli(
        executable,
        mets_url=None,
        resolver=None,
        workspace=None,
        page_id=None,
        overwrite=None,
        debug=None,
        log_level=None,
        log_filename=None,
        input_file_grp=None,
        output_file_grp=None,
        parameter=None,
        working_dir=None,
        mets_server_url=None,
):
    """
    Open a workspace and run a processor on the command line.

    If :py:attr:`workspace` is not none, reuse that. Otherwise, instantiate an
    :py:class:`~ocrd.Workspace` for :py:attr:`mets_url` (and :py:attr:`working_dir`)
    by using :py:meth:`ocrd.Resolver.workspace_from_url` (i.e. open or clone local workspace).

    Run the processor CLI :py:attr:`executable` on the workspace, passing:
    - the workspace,
    - :py:attr:`page_id`
    - :py:attr:`input_file_grp`
    - :py:attr:`output_file_grp`
    - :py:attr:`parameter` (after applying any :py:attr:`parameter_override` settings)

    (Will create output files and update the in the filesystem).

    Args:
        executable (string): Executable name of the module processor.
    """
    workspace = _get_workspace(workspace, resolver, mets_url, working_dir)
    args = [executable, '--working-dir', workspace.directory]
    args += ['--mets', mets_url]
    if log_level:
        args += ['--log-level', log_level if isinstance(log_level, str) else getLevelName(log_level)]
    if page_id:
        args += ['--page-id', page_id]
    if input_file_grp:
        args += ['--input-file-grp', input_file_grp]
    if output_file_grp:
        args += ['--output-file-grp', output_file_grp]
    if parameter:
        args += ['--parameter', parameter]
    if overwrite:
        args += ['--overwrite']
    if debug:
        args += ['--debug']
    if mets_server_url:
        args += ['--mets-server-url', mets_server_url]
    log = getLogger('ocrd.processor.helpers.run_cli')
    log.debug("Running subprocess '%s'", ' '.join(args))
    if not log_filename:
        result = run(args, check=False)
    else:
        with open(log_filename, 'a', encoding='utf-8') as file_desc:
            result = run(args, check=False, stdout=file_desc, stderr=file_desc)
    return result.returncode



# not decorated here but at runtime (on first use)
#@freeze_args
#@lru_cache(maxsize=config.OCRD_MAX_PROCESSOR_CACHE)
def get_cached_processor(parameter: dict, processor_class):
    """
    Call this function to get back an instance of a processor.
    The results are cached based on the parameters.
    Args:
        parameter (dict): a dictionary of parameters.
        processor_class: the concrete `:py:class:~ocrd.Processor` class.
    Returns:
        When the concrete class of the processor is unknown, `None` is returned.
        Otherwise, an instance of the `:py:class:~ocrd.Processor` is returned.
    """
    if processor_class:
        processor = processor_class(None, parameter=dict(parameter))
        return processor
    return None

def get_processor(
        processor_class,
        parameter: Optional[dict] = None,
        workspace: Optional[Workspace] = None,
        page_id: Optional[str] = None,
        input_file_grp: Optional[List[str]] = None,
        output_file_grp: Optional[List[str]] = None,
        instance_caching: bool = False,
):
    if processor_class:
        if parameter is None:
            parameter = {}
        if instance_caching:
            global get_cached_processor
            if not hasattr(get_cached_processor, '__wrapped__'):
                # first call: wrap
                if processor_class.max_instances < 0:
                    maxsize = config.OCRD_MAX_PROCESSOR_CACHE
                else:
                    maxsize = min(config.OCRD_MAX_PROCESSOR_CACHE, processor_class.max_instances)
                # wrapping in call cache
                # wrapping dict into frozendict (from https://github.com/OCR-D/core/pull/884)
                get_cached_processor = freeze_args(lru_cache(maxsize=maxsize)(get_cached_processor))
            processor = get_cached_processor(parameter, processor_class)
        else:
            # avoid passing workspace already (deprecated chdir behaviour)
            processor = processor_class(None, parameter=parameter)
        assert processor
        # set current processing parameters
        processor.workspace = workspace
        processor.page_id = page_id
        processor.input_file_grp = input_file_grp
        processor.output_file_grp = output_file_grp
        return processor
    raise ValueError("Processor class is not known")
