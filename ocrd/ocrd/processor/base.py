import os
import json
from click import wrap_text
import subprocess
from ocrd_utils import getLogger
from ocrd_validators import ParameterValidator

log = getLogger('ocrd.processor')

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
        log_level=None,         # TODO actually use this!
        input_file_grp=None,
        output_file_grp=None,
        parameter=None,
        working_dir=None,
): # pylint: disable=too-many-locals
    """
    Create a workspace for mets_url and run processor through it

    Args:
        parameter (string): URL to the parameter
    """
    workspace = _get_workspace(
        workspace,
        resolver,
        mets_url,
        working_dir
    )
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
    log.debug("Processor instance %s (%s doing %s)", processor, name, otherrole)
    processor.process()
    workspace.mets.add_agent(
        name=name,
        _type='OTHER',
        othertype='SOFTWARE',
        role='OTHER',
        otherrole=otherrole
    )
    workspace.save_mets()
    return processor

def run_cli(
        executable,
        mets_url=None,
        resolver=None,
        workspace=None,
        page_id=None,
        log_level=None,
        input_file_grp=None,
        output_file_grp=None,
        parameter=None,
        working_dir=None,
):
    """
    Create a workspace for mets_url and run MP CLI through it
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
    log.debug("Running subprocess '%s'", ' '.join(args))
    return subprocess.call(args)

def generate_processor_help(ocrd_tool):
    parameter_help = ''
    if 'parameters' not in ocrd_tool or not ocrd_tool['parameters']:
        parameter_help = '  NONE\n'
    else:
        for param_name, param in ocrd_tool['parameters'].items():
            parameter_help += wrap_text('  "%s" [%s%s] %s' % (
                param_name,
                param['type'],
                ' - REQUIRED' if 'required' in param and param['required'] else
                ' - %s' % param['default'] if 'default' in param else '',
                param['description']
            ), subsequent_indent='    ', width=72, preserve_paragraphs=True)
            parameter_help += "\n"
    return '''
Usage: %s [OPTIONS]

  %s

Options:
  -V, --version                   Show version
  -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                  Log level
  -J, --dump-json                 Dump tool description as JSON and exit
  -p, --parameter TEXT            Parameters, either JSON string or path 
                                  JSON file
  -g, --page-id TEXT              ID(s) of the pages to process
  -O, --output-file-grp TEXT      File group(s) used as output.
  -I, --input-file-grp TEXT       File group(s) used as input.
  -w, --working-dir TEXT          Working Directory
  -m, --mets TEXT                 METS to process
  -h, --help                      This help message

Parameters:
%s
Default Wiring:
  %s -> %s

''' % (
    ocrd_tool['executable'],
    ocrd_tool['description'],
    parameter_help,
    ocrd_tool['input_file_grp'],
    ocrd_tool.get('output_file_grp', 'NONE')
)


class Processor():
    """
    A processor runs an algorithm based on the workspace, the mets.xml in the
    workspace (and the input files defined therein) as well as optional
    parameter.
    """

    def __init__(
            self,
            workspace,
            ocrd_tool=None,
            parameter=None,
            input_file_grp="INPUT",
            output_file_grp="OUTPUT",
            page_id=None,
            show_help=False,
            dump_json=False,
            version=None
    ):
        if parameter is None:
            parameter = {}
        if dump_json:
            print(json.dumps(ocrd_tool, indent=True))
            return
        self.ocrd_tool = ocrd_tool
        if show_help:
            self.show_help()
            return
        self.version = version
        self.workspace = workspace
        # FIXME HACK would be better to use pushd_popd(self.workspace.directory)
        # but there is no way to do that in process here since it's an
        # overridden method. chdir is almost always an anti-pattern.
        if self.workspace:
            os.chdir(self.workspace.directory)
        self.input_file_grp = input_file_grp
        self.output_file_grp = output_file_grp
        self.page_id = None if page_id == [] or page_id is None else page_id
        parameterValidator = ParameterValidator(ocrd_tool)
        report = parameterValidator.validate(parameter)
        if not report.is_valid:
            raise Exception("Invalid parameters %s" % report.errors)
        self.parameter = parameter

    def show_help(self):
        print(generate_processor_help(self.ocrd_tool))

    def verify(self):
        """
        Verify that the input fulfills the processor's requirements.
        """
        return True

    def process(self):
        """
        Process the workspace
        """
        raise Exception("Must be implemented")

    @property
    def input_files(self):
        """
        List the input files
        """
        return self.workspace.mets.find_files(fileGrp=self.input_file_grp, pageId=self.page_id)
