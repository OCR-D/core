class Processor(object):
    """
    A processor runs an algorithm based on the workspace, the mets.xml in the
    workspace (and the input files defined therein) as well as optional
    parameters.
    """

    def __init__(self, workspace, parameters=None, inputGrp="INPUT", outputGrp="OUTPUT"):
        self.workspace = workspace
        self.inputGrp = inputGrp
        self.outputGrp = outputGrp
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
        pass
