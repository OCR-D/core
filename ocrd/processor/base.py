import subprocess
from ocrd.utils import getLogger
log = getLogger('ocrd.processor')

def _get_workspace(workspace=None, resolver=None, mets_url=None, working_dir=None):
    if workspace is None:
        if resolver is None:
            raise Exception("Need to pass a resolver to create a workspace")
        if mets_url is None:
            raise Exception("Need to pass mets_url to create a workspace")
        workspace = resolver.workspace_from_url(mets_url, directory=working_dir)
    return workspace

# pylint: disable=unused-argument
def run_processor(
        processorClass,
        mets_url=None,
        resolver=None,
        workspace=None,
        group_id=None,
        input_filegrp=None,
        output_filegrp=None,
        output_mets=None,
        parameter=None,
        working_dir=None,
):
    """
    Create a workspace for mets_url and run processor through it
    """
    workspace = _get_workspace(workspace, resolver, mets_url, working_dir)
    log.debug("Running processor %s", processorClass)
    processor = processorClass(workspace, input_filegrp=input_filegrp, output_filegrp=output_filegrp)
    log.debug("Processor instance %s", processor)
    processor.process()
    #  workspace.persist()

def run_cli(
        binary,
        mets_url=None,
        resolver=None,
        workspace=None,
        group_id=None,
        input_filegrp=None,
        output_filegrp=None,
        output_mets=None,
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
        '-m', mets_url,
        '-w', workspace.directory
    ])
    #  workspace.persist()

class Processor(object):
    """
    A processor runs an algorithm based on the workspace, the mets.xml in the
    workspace (and the input files defined therein) as well as optional
    parameters.
    """

    def __init__(self, workspace, parameters=None, input_filegrp="INPUT", output_filegrp="OUTPUT"):
        self.workspace = workspace
        self.input_filegrp = input_filegrp
        self.output_filegrp = output_filegrp
        self.parameters = parameters if parameters is not None else {}

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
        return self.workspace.mets.find_files(fileGrp=self.input_filegrp)

    def add_output_file(self, input_file=None, basename=None, ID=None, **kwargs):
        """
        Add an output file.
        """
        log.debug("Adding output file %s", input_file)
        if basename is None and input_file is not None:
            basename = input_file.basename_without_extension + '.xml'
        #  if ID is None and input_file is not None:
        #      basename = input_file.ID + self.output_filegrp
        self.workspace.add_file(self.output_filegrp, basename=basename, ID=ID, **kwargs)
