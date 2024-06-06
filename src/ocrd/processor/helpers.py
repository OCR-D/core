"""
Helper methods for running and documenting processors
"""
from os import chdir, getcwd
from time import perf_counter, process_time
from functools import lru_cache
import json
import inspect
from subprocess import run
from typing import List

from click import wrap_text
from ocrd.workspace import Workspace
from ocrd_utils import freeze_args, getLogger, config, setOverrideLogLevel, getLevelName, sparkline


__all__ = [
    'generate_processor_help',
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
        show_resource=None,
        list_resources=False,
        parameter=None,
        parameter_override=None,
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

    Warning: Avoid setting the `instance_caching` flag to True. It may have unexpected side effects.
    This flag is used for an experimental feature we would like to adopt in future.

    Run the processor on the workspace (creating output files in the filesystem).

    Finally, write back the workspace (updating the METS in the filesystem).

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

    old_cwd = getcwd()
    processor = get_processor(
        processor_class=processorClass,
        parameter=parameter,
        workspace=None,
        page_id=page_id,
        input_file_grp=input_file_grp,
        output_file_grp=output_file_grp,
        instance_caching=instance_caching
    )
    processor.workspace = workspace
    chdir(processor.workspace.directory)

    ocrd_tool = processor.ocrd_tool
    name = '%s v%s' % (ocrd_tool['executable'], processor.version)
    otherrole = ocrd_tool['steps'][0]
    logProfile = getLogger('ocrd.process.profile')
    log.debug("Processor instance %s (%s doing %s)", processor, name, otherrole)
    t0_wall = perf_counter()
    t0_cpu = process_time()
    if any(x in config.OCRD_PROFILE for x in ['RSS', 'PSS']):
        backend = 'psutil_pss' if 'PSS' in config.OCRD_PROFILE else 'psutil'
        from memory_profiler import memory_usage
        try:
            mem_usage = memory_usage(proc=processor.process,
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
        finally:
            chdir(old_cwd)
        mem_usage_values = [mem for mem, _ in mem_usage]
        mem_output = 'memory consumption: '
        mem_output += sparkline(mem_usage_values)
        mem_output += ' max: %.2f MiB min: %.2f MiB' % (max(mem_usage_values), min(mem_usage_values))
        logProfile.info(mem_output)
    else:
        try:
            processor.process()
        except Exception as err:
            log.exception("Failure in processor '%s'" % ocrd_tool['executable'])
            raise err
        finally:
            chdir(old_cwd)

    t1_wall = perf_counter() - t0_wall
    t1_cpu = process_time() - t0_cpu
    logProfile.info("Executing processor '%s' took %fs (wall) %fs (CPU)( [--input-file-grp='%s' --output-file-grp='%s' --parameter='%s' --page-id='%s']" % (
        ocrd_tool['executable'],
        t1_wall,
        t1_cpu,
        processor.input_file_grp or '',
        processor.output_file_grp or '',
        json.dumps(processor.parameter) or '',
        processor.page_id or ''
    ))
    workspace.mets.add_agent(
        name=name,
        _type='OTHER',
        othertype='SOFTWARE',
        role='OTHER',
        otherrole=otherrole,
        notes=[({'option': 'input-file-grp'}, processor.input_file_grp or ''),
               ({'option': 'output-file-grp'}, processor.output_file_grp or ''),
               ({'option': 'parameter'}, json.dumps(processor.parameter or '')),
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
    if mets_server_url:
        args += ['--mets-server-url', mets_server_url]
    log = getLogger('ocrd.processor.helpers.run_cli')
    log.debug("Running subprocess '%s'", ' '.join(args))
    if not log_filename:
        result = run(args, check=False)
    else:
        with open(log_filename, 'a') as file_desc:
            result = run(args, check=False, stdout=file_desc, stderr=file_desc)
    return result.returncode


def generate_processor_help(ocrd_tool, processor_instance=None, subcommand=None):
    """Generate a string describing the full CLI of this processor including params.

    Args:
         ocrd_tool (dict): this processor's ``tools`` section of the module's ``ocrd-tool.json``
         processor_instance (object, optional): the processor implementation
             (for adding any module/class/function docstrings)
        subcommand (string): 'worker' or 'server'
    """
    doc_help = ''
    if processor_instance:
        module = inspect.getmodule(processor_instance)
        if module and module.__doc__:
            doc_help += '\n' + inspect.cleandoc(module.__doc__) + '\n'
        if processor_instance.__doc__:
            doc_help += '\n' + inspect.cleandoc(processor_instance.__doc__) + '\n'
        if processor_instance.process.__doc__:
            doc_help += '\n' + inspect.cleandoc(processor_instance.process.__doc__) + '\n'
        if doc_help:
            doc_help = '\n\n' + wrap_text(doc_help, width=72,
                                          initial_indent='  > ',
                                          subsequent_indent='  > ',
                                          preserve_paragraphs=True)
    subcommands = '''\
    worker      Start a processing worker rather than do local processing
    server      Start a processor server rather than do local processing
'''

    processing_worker_options = '''\
  --queue                         The RabbitMQ server address in format
                                  "amqp://{user}:{pass}@{host}:{port}/{vhost}"
                                  [amqp://admin:admin@localhost:5672]
  --database                      The MongoDB server address in format
                                  "mongodb://{host}:{port}"
                                  [mongodb://localhost:27018]
  --log-filename                  Filename to redirect STDOUT/STDERR to,
                                  if specified.
'''

    processing_server_options = '''\
  --address                       The Processor server address in format
                                  "{host}:{port}"
  --database                      The MongoDB server address in format
                                  "mongodb://{host}:{port}"
                                  [mongodb://localhost:27018]
'''

    processing_options = '''\
  -m, --mets URL-PATH             URL or file path of METS to process [./mets.xml]
  -w, --working-dir PATH          Working directory of local workspace [dirname(URL-PATH)]
  -I, --input-file-grp USE        File group(s) used as input
  -O, --output-file-grp USE       File group(s) used as output
  -g, --page-id ID                Physical page ID(s) to process instead of full document []
  --overwrite                     Remove existing output pages/images
                                  (with "--page-id", remove only those)
  --profile                       Enable profiling
  --profile-file PROF-PATH        Write cProfile stats to PROF-PATH. Implies "--profile"
  -p, --parameter JSON-PATH       Parameters, either verbatim JSON string
                                  or JSON file path
  -P, --param-override KEY VAL    Override a single JSON object key-value pair,
                                  taking precedence over --parameter
  -U, --mets-server-url URL       URL of a METS Server for parallel incremental access to METS
                                  If URL starts with http:// start an HTTP server there,
                                  otherwise URL is a path to an on-demand-created unix socket
  -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                  Override log level globally [INFO]
'''

    information_options = '''\
  -C, --show-resource RESNAME     Dump the content of processor resource RESNAME
  -L, --list-resources            List names of processor resources
  -J, --dump-json                 Dump tool description as JSON
  -D, --dump-module-dir           Show the 'module' resource location path for this processor
  -h, --help                      Show this message
  -V, --version                   Show version
'''

    parameter_help = ''
    if 'parameters' not in ocrd_tool or not ocrd_tool['parameters']:
        parameter_help = '  NONE\n'
    else:
        def wrap(s):
            return wrap_text(s, initial_indent=' '*3,
                             subsequent_indent=' '*4,
                             width=72, preserve_paragraphs=True)
        for param_name, param in ocrd_tool['parameters'].items():
            parameter_help += wrap('"%s" [%s%s]' % (
                param_name,
                param['type'],
                ' - REQUIRED' if 'required' in param and param['required'] else
                ' - %s' % json.dumps(param['default']) if 'default' in param else ''))
            parameter_help += '\n ' + wrap(param['description'])
            if 'enum' in param:
                parameter_help += '\n ' + wrap('Possible values: %s' % json.dumps(param['enum']))
            parameter_help += "\n"

    if not subcommand:
        return f'''\
Usage: {ocrd_tool['executable']} [worker|server] [OPTIONS]

  {ocrd_tool['description']}{doc_help}

Subcommands:
{subcommands}
Options for processing:
{processing_options}
Options for information:
{information_options}
Parameters:
{parameter_help}
'''
    elif subcommand == 'worker':
        return f'''\
Usage: {ocrd_tool['executable']} worker [OPTIONS]

  Run {ocrd_tool['executable']} as a processing worker.

  {ocrd_tool['description']}{doc_help}

Options:
{processing_worker_options}
'''
    elif subcommand == 'server':
        return f'''\
Usage: {ocrd_tool['executable']} server [OPTIONS]

  Run {ocrd_tool['executable']} as a processor sever.

  {ocrd_tool['description']}{doc_help}

Options:
{processing_server_options}
'''
    else:
        pass


# Taken from https://github.com/OCR-D/core/pull/884
@freeze_args
@lru_cache(maxsize=config.OCRD_MAX_PROCESSOR_CACHE)
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
        dict_params = dict(parameter) if parameter else None
        return processor_class(workspace=None, parameter=dict_params)
    return None


def get_processor(
        processor_class,
        parameter: dict,
        workspace: Workspace = None,
        page_id: str = None,
        input_file_grp: List[str] = None,
        output_file_grp: List[str] = None,
        instance_caching: bool = False,
):
    if processor_class:
        if instance_caching:
            cached_processor = get_cached_processor(
                parameter=parameter,
                processor_class=processor_class
            )
            cached_processor.workspace = workspace
            cached_processor.page_id = page_id
            cached_processor.input_file_grp = input_file_grp
            cached_processor.output_file_grp = output_file_grp
            return cached_processor
        return processor_class(
            workspace=workspace,
            page_id=page_id,
            input_file_grp=input_file_grp,
            output_file_grp=output_file_grp,
            parameter=parameter
        )
    raise ValueError("Processor class is not known")
