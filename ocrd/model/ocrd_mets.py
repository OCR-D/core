from ocrd.constants import NAMESPACES as NS

from .ocrd_xml_base import OcrdXmlBase
from .ocrd_mets_file import OcrdMetsFile

class OcrdMets(OcrdXmlBase):

    def files_in_group(self, use):
        return [OcrdMetsFile(el) for el in self._tree.getroot().findall(".//mets:fileGrp[@USE='%s']/mets:file" % (use), NS)]
