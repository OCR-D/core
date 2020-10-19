from ocrd_models import OcrdFile

class MockOcrdFile(OcrdFile):
    """
    OcrdFile with mocked fileGrp access
    """
    @property
    def fileGrp(self):
        return self.__filegrp
    @fileGrp.setter
    def fileGrp(self, fileGrp):
        self.__filegrp = fileGrp
    def __init__(self, *args, fileGrp=None, ocrd_mets=None, **kwargs):
        super(MockOcrdFile, self).__init__(*args, **kwargs)
        self.fileGrp = fileGrp if fileGrp else None
        self.ocrd_mets = ocrd_mets if ocrd_mets else None


