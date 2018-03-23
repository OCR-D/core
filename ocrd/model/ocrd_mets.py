from ocrd.constants import NAMESPACES as NS

from .ocrd_xml_base import OcrdXmlBase

class OcrdMetsFile(object):

    def __init__(self, el):
        self.mimetype = el.get('MIMETYPE')
        self.ID = el.get('ID')
        self.url = el.find('mets:FLocat', NS).get("{%s}href" % NS["xlink"])

    def __str__(self):
        return 'OcrdMetsFile[%s @ %s]' % (self.mimetype, self.url)

class OcrdMets(OcrdXmlBase):

    def files_in_group(self, use):
        return [OcrdMetsFile(el) for el in self._tree.getroot().findall(".//mets:fileGrp[@USE='%s']/mets:file" % (use), NS)]
