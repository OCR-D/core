"""
Helper methods for running and documenting processors
"""
import os
from time import perf_counter, process_time
import json
import inspect
from subprocess import run, PIPE
from typing import List

from beanie import PydanticObjectId
from click import wrap_text

from ocrd_utils import getLogger

__all__ = [
    'generate_processor_help',
    'run_cli',
    'run_processor',
    'run_cli_from_api',
    'run_processor_from_api'
]


def _get_workspace(workspace=None, resolver=None, mets_url=None, working_dir=None):
    if workspace is None:
        if resolver is None:
            raise Exception("Need to pass a resolver to create a workspace")
        if mets_url is None:
            raise Exception("Need to pass mets_url to create a workspace")
        workspace = resolver.workspace_from_url(mets_url, dst_dir=working_dir)
    return workspace


def run_processor(
        processorClass,
        ocrd_tool=None,
        mets_url=None,
        resolver=None,
        workspace=None,
        page_id=None,
        log_level=None,  # TODO actually use this!
        input_file_grp=None,
        output_file_grp=None,
        show_resource=None,
        list_resources=False,
        parameter=None,
        parameter_override=None,
        working_dir=None,
):  # pylint: disable=too-many-locals
    """
    Instantiate a Pythonic processor, open a workspace, run the processor and save the workspace.

    If :py:attr:`workspace` is not none, reuse that. Otherwise, instantiate an
    :py:class:`~ocrd.Workspace` for :py:attr:`mets_url` (and :py:attr:`working_dir`)
    by using :py:meth:`ocrd.Resolver.workspace_from_url` (i.e. open or clone local workspace).

    Instantiate a Python object for :py:attr:`processorClass`, passing:
    - the workspace,
    - :py:attr:`ocrd_tool`
    - :py:attr:`page_id`
    - :py:attr:`input_file_grp`
    - :py:attr:`output_file_grp`
    - :py:attr:`parameter` (after applying any :py:attr:`parameter_override` settings)

    Run the processor on the workspace (creating output files in the filesystem).

    Finally, write back the workspace (updating the METS in the filesystem).

    Args:
        processorClass (object): Python class of the module processor.
    """
    workspace = _get_workspace(
        workspace,
        resolver,
        mets_url,
        working_dir
    )
    log = getLogger('ocrd.processor.helpers.run_processor')
    log.debug("Running processor %s", processorClass)
    processor = processorClass(
        workspace,
        ocrd_tool=ocrd_tool,
        page_id=page_id,
        input_file_grp=input_file_grp,
        output_file_grp=output_file_grp,
        parameter=parameter
    )
    ocrd_tool = processor.ocrd_tool
    name = '%s v%s' % (ocrd_tool['executable'], processor.version)
    otherrole = ocrd_tool['steps'][0]
    logProfile = getLogger('ocrd.process.profile')
    log.debug("Processor instance %s (%s doing %s)", processor, name, otherrole)
    t0_wall = perf_counter()
    t0_cpu = process_time()
    processor.process()
    t1_wall = perf_counter() - t0_wall
    t1_cpu = process_time() - t0_cpu
    logProfile.info(
        "Executing processor '%s' took %fs (wall) %fs (CPU)( [--input-file-grp='%s' --output-file-grp='%s' --parameter='%s' --page-id='%s']" % (
            ocrd_tool['executable'],
            t1_wall,
            t1_cpu,
            input_file_grp or '',
            output_file_grp or '',
            json.dumps(parameter) or '',
            page_id or ''
        ))
    workspace.mets.add_agent(
        name=name,
        _type='OTHER',
        othertype='SOFTWARE',
        role='OTHER',
        otherrole=otherrole,
        notes=[({'option': 'input-file-grp'}, input_file_grp or ''),
               ({'option': 'output-file-grp'}, output_file_grp or ''),
               ({'option': 'parameter'}, json.dumps(parameter or '')),
               ({'option': 'page-id'}, page_id or '')]
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
        input_file_grp=None,
        output_file_grp=None,
        parameter=None,
        working_dir=None,
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
        args += ['--log-level', log_level]
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
    log = getLogger('ocrd.processor.helpers.run_cli')
    log.debug("Running subprocess '%s'", ' '.join(args))
    result = run(args, check=False)
    return result.returncode


async def run_cli_from_api(job_id: PydanticObjectId, executable: str, workspace, page_id: str,
                           input_file_grps: List[str], output_file_grps: List[str], parameter: dict):
    # Turn input/output file groups into a comma separated string
    input_file_grps_str = ','.join(input_file_grps)
    output_file_grps_str = ','.join(output_file_grps)

    # Execute the processor
    return_code = run_cli(executable, workspace=workspace, page_id=page_id, input_file_grp=input_file_grps_str,
                          output_file_grp=output_file_grps_str, parameter=json.dumps(parameter), mets_url='')

    workspace.reload_mets()

    log = getLogger('ocrd.processor.helpers.run_cli')

    # check output file groups are in METS
    for output_file_grp in output_file_grps:
        if output_file_grp not in workspace.mets.file_groups:
            log.error(
                f'Invalid state: expected output file group "{output_file_grp}" not in METS (despite processor success)')

    log.debug('Finish processing')

    # Save the job status to the database
    from ocrd.server.models.job import Job, StateEnum
    job = await Job.get(job_id)
    if return_code != 0:
        job.state = StateEnum.failed
        log.error(f'{executable} exited with non-zero return value {return_code}.')
    else:
        job.state = StateEnum.success
    await job.save()


async def run_processor_from_api(job_id: PydanticObjectId, processor, workspace, page_id: str,
                                 input_file_grps: List[str], output_file_grps: List[str]):
    # Set up the log
    log = getLogger('ocrd.processor.helpers.run_processor')
    ocrd_tool = processor.ocrd_tool
    name = '%s v%s' % (ocrd_tool['executable'], processor.version)
    otherrole = ocrd_tool['steps'][0]
    logProfile = getLogger('ocrd.process.profile')
    log.debug("Processor instance %s (%s doing %s)", processor, name, otherrole)
    t0_wall = perf_counter()
    t0_cpu = process_time()

    # Save the current working directory
    old_cwd = os.getcwd()

    # Turn input/output file groups into a comma separated string
    input_file_grps_str = ','.join(input_file_grps)
    output_file_grps_str = ','.join(output_file_grps)

    # Set values for the processor
    processor.input_file_grp = input_file_grps_str
    processor.output_file_grp = output_file_grps_str
    processor.page_id = page_id
    processor.workspace = workspace

    # Move inside the workspace (so that files in the METS can be found)
    os.chdir(workspace.directory)

    is_success = True
    try:
        processor.process()

        # check output file groups are in METS
        for output_file_grp in output_file_grps:
            if output_file_grp not in workspace.mets.file_groups:
                log.error(
                    f'Invalid state: expected output file group "{output_file_grp}" not in METS (despite processor success)')
    except Exception as e:
        log.exception(e)
        is_success = False
    finally:
        # Move back to the old directory
        os.chdir(old_cwd)

    t1_wall = perf_counter() - t0_wall
    t1_cpu = process_time() - t0_cpu
    logProfile.info(
        "Executing processor '%s' took %fs (wall) %fs (CPU)( [--input-file-grp='%s' --output-file-grp='%s' --parameter='%s' --page-id='%s']" % (
            ocrd_tool['executable'],
            t1_wall,
            t1_cpu,
            input_file_grps_str or '',
            output_file_grps_str or '',
            json.dumps(processor.parameter) or '',
            page_id or ''
        ))

    from ocrd.server.models.job import Job, StateEnum
    job = await Job.get(job_id)
    if is_success:
        workspace.mets.add_agent(
            name=name,
            _type='OTHER',
            othertype='SOFTWARE',
            role='OTHER',
            otherrole=otherrole,
            notes=[({'option': 'input-file-grp'}, input_file_grps_str or ''),
                   ({'option': 'output-file-grp'}, output_file_grps_str or ''),
                   ({'option': 'parameter'}, json.dumps(processor.parameter or '')),
                   ({'option': 'page-id'}, page_id or '')]
        )
        workspace.save_mets()

        # Save the job status to the database
        job.state = StateEnum.success
    else:
        job.state = StateEnum.failed
    await job.save()


def generate_processor_help(ocrd_tool, processor_instance=None):
    """Generate a string describing the full CLI of this processor including params.
    
    Args:
         ocrd_tool (dict): this processor's ``tools`` section of the module's ``ocrd-tool.json``
         processor_instance (object, optional): the processor implementation
             (for adding any module/class/function docstrings)
    """
    parameter_help = ''
    if 'parameters' not in ocrd_tool or not ocrd_tool['parameters']:
        parameter_help = '  NONE\n'
    else:
        def wrap(s):
            return wrap_text(s, initial_indent=' ' * 3,
                             subsequent_indent=' ' * 4,
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
    doc_help = ''
    if processor_instance:
        module = inspect.getmodule(processor_instance)
        if module and module.__doc__:
            doc_help += '\n' + inspect.cleandoc(module.__doc__)
        if processor_instance.__doc__:
            doc_help += '\n' + inspect.cleandoc(processor_instance.__doc__)
        if processor_instance.process.__doc__:
            doc_help += '\n' + inspect.cleandoc(processor_instance.process.__doc__)
        if doc_help:
            doc_help = '\n\n' + wrap_text(doc_help, width=72,
                                          initial_indent='  > ',
                                          subsequent_indent='  > ',
                                          preserve_paragraphs=True)
    return '''
Usage: %s [OPTIONS]

  %s%s

Options:
  -I, --input-file-grp USE        File group(s) used as input
  -O, --output-file-grp USE       File group(s) used as output
  -g, --page-id ID                Physical page ID(s) to process
  --overwrite                     Remove existing output pages/images
                                  (with --page-id, remove only those)
  -p, --parameter JSON-PATH       Parameters, either verbatim JSON string
                                  or JSON file path
  --server-ip IP                  Host name/IP to listen at. When this value is set,
                                  --server-port must be set as well.
  --server-port NUMBER            TCP port to listen at. When this value is set,
                                  --server-ip must be set as well.
  --mongo-url URL                 Connection string to a Mongo database. If the processor runs as a server,
                                  this value must be set.
  -P, --param-override KEY VAL    Override a single JSON object key-value pair,
                                  taking precedence over --parameter
  -m, --mets URL-PATH             URL or file path of METS to process
  -w, --working-dir PATH          Working directory of local workspace
  -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                  Log level
  -C, --show-resource RESNAME     Dump the content of processor resource RESNAME
  -L, --list-resources            List names of processor resources
  -J, --dump-json                 Dump tool description as JSON and exit
  -h, --help                      This help message
  -V, --version                   Show version

Parameters:
%s
Default Wiring:
  %s -> %s

''' % (
        ocrd_tool['executable'],
        ocrd_tool['description'],
        doc_help,
        parameter_help,
        ocrd_tool.get('input_file_grp', 'NONE'),
        ocrd_tool.get('output_file_grp', 'NONE')
    )
