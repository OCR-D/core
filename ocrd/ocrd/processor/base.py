import os
import json
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
        log_level=None,
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
    if parameter is not None:
        if not '://' in parameter:
            fname = os.path.abspath(parameter)
        else:
            fname = workspace.download_url(parameter)
        with open(fname, 'r') as param_json_file:
            parameter = json.load(param_json_file)
    else:
        parameter = {}
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

class Processor(object):
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
            dump_json=False,
            version=None
    ):
        if parameter is None:
            parameter = {}
        if dump_json:
            print(json.dumps(ocrd_tool, indent=True))
            return
        self.ocrd_tool = ocrd_tool
        self.version = version
        self.workspace = workspace
        self.input_file_grp = input_file_grp
        self.output_file_grp = output_file_grp
        self.page_id = None if page_id == [] or page_id is None else page_id
        parameterValidator = ParameterValidator(ocrd_tool)
        parameterValidator.validate(parameter)
        self.parameter = parameter

    def verify(self):
        """
        Verify that the input is fulfills the processor's requirements.
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
