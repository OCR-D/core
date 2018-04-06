from ocrd.constants import NAMESPACES as NS, TAG_METS_FILE, TAG_METS_FILEGRP, IDENTIFIER_PRIORITY

from .ocrd_xml_base import OcrdXmlDocument, ET
from .ocrd_file import OcrdFile

class OcrdMets(OcrdXmlDocument):

    def __init__(self, *args, **kwargs):
        super(OcrdMets, self).__init__(*args, **kwargs)
        self._file_by_id = {}

    def __str__(self):
        return 'OcrdMets[fileGrps=%s,files=%s]' % (self.file_groups, self.file_by_id)

    @property
    def unique_identifier(self):
        for t in IDENTIFIER_PRIORITY:
            found = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            if found is not None:
                return found.text

    @property
    def file_by_id(self):
        return self._file_by_id

    @property
    def file_groups(self):
        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_files(self, fileGrp=None):
        """
        List files.

        Args:
            fileGrp (string) : USE of the fileGrp to list files of

        Return:
            List of files.
        """
        ret = []
        if fileGrp is not None:
            file_els = self._tree.getroot().findall(".//mets:fileGrp[@USE='%s']/mets:file" % (fileGrp), NS)
        else:
            file_els = self._tree.getroot().findall(".//mets:fileGrp/mets:file", NS)
        for el in file_els:
            file_id = el.get('ID')
            if file_id not in self._file_by_id:
                self._file_by_id[file_id] = OcrdFile(el)
            ret.append(self._file_by_id[file_id])
        return ret

    def add_file_group(self, use):
        el_fileGrp = ET.SubElement(self._tree.getroot().find('.//mets:fileSec', NS), TAG_METS_FILEGRP)
        el_fileGrp.set('USE', use)
        return el_fileGrp

    def add_file(self, use, mimetype=None, url=None, ID=None, local_filename=None):
        el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (use), NS)
        if el_fileGrp is None:
            el_fileGrp = self.add_file_group(use)
        mets_file = OcrdFile(ET.SubElement(el_fileGrp, TAG_METS_FILE))
        mets_file.url = url
        mets_file.mimetype = mimetype
        mets_file.ID = ID
        mets_file.local_filename = local_filename
        return mets_file
