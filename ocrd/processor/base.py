import os
import json
import subprocess
from deprecated.sphinx import deprecated
from ocrd.utils import getLogger
from ocrd.validator import ParameterValidator

log = getLogger('ocrd.processor')

def _get_workspace(workspace=None, resolver=None, mets_url=None, working_dir=None):
    if workspace is None:
        if resolver is None:
            raise Exception("Need to pass a resolver to create a workspace")
        if mets_url is None:
            raise Exception("Need to pass mets_url to create a workspace")
        workspace = resolver.workspace_from_url(mets_url, directory=working_dir)
    return workspace

def run_processor(
        processorClass,
        ocrd_tool=None,
        mets_url=None,
        resolver=None,
        workspace=None,
        group_id=None,
        log_level=None,
        input_file_grp=None,
        output_file_grp=None,
        parameter=None,
        working_dir=None,
):
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
        group_id=group_id,
        input_file_grp=input_file_grp,
        output_file_grp=output_file_grp,
        parameter=parameter
    )
    log.debug("Processor instance %s", processor)
    processor.process()
    workspace.save_mets()

# TODO not used as of 0.8.2
def run_cli(
        binary,
        mets_url=None,
        resolver=None,
        workspace=None,
        group_id=None,
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
    log.debug("Running binary '%s'", binary)
    subprocess.call([
        binary,
        '--mets', mets_url,
        '--working-dir', workspace.directory
    ])

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
            parameter={},
            input_file_grp="INPUT",
            output_file_grp="OUTPUT",
            group_id=None,
            dump_json=False,
            version=None
    ):
        if dump_json:
            print(json.dumps(ocrd_tool, indent=True))
            return
        self.version = version
        self.workspace = workspace
        self.input_file_grp = input_file_grp
        self.output_file_grp = output_file_grp
        self.group_id = None if group_id == [] or group_id is None else group_id
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
        return self.workspace.mets.find_files(fileGrp=self.input_file_grp, groupId=self.group_id)

    @deprecated(version='0.8.0', reason="Use self.workspace.add_file directly. See https://github.com/OCR-D/core/issues/166.")
    def add_output_file(self, basename=None, file_grp=None, ID=None, **kwargs):
        """
        DEPRECATED

        Add an output file.

        Args:
            basename (string) : basename of the file
            file_grp (string) : fileGrp to add this file to. Default: self.output_file_grp
            ID (string) : file@ID
        """
        if basename is None:
            raise Exception("Must give 'basename' for add_output_file")
        log.debug("Adding output file %s", basename)
        if file_grp is None:
            file_grp = self.output_file_grp
        self.workspace.add_file(file_grp, basename=basename, ID=ID, **kwargs)
