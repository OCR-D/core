from ocrd.constants import NAMESPACES as NS

from .ocrd_xml_base import OcrdXmlBase
from .ocrd_mets_file import OcrdMetsFile


class OcrdMets(OcrdXmlBase):

    def __init__(self, *args, **kwargs):
        super(OcrdMets, self).__init__(*args, **kwargs)
        self._fileGrp = {}

    def files_in_group(self, use):
        if use not in self._fileGrp:
            self._fileGrp[use] = [
                OcrdMetsFile(el) for
                el in
                self._tree.getroot().findall(".//mets:fileGrp[@USE='%s']/mets:file" % (use), NS)
            ]
        return self._fileGrp[use]
