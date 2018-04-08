from ocrd.constants import NAMESPACES as NS, TAG_METS_FILE, TAG_METS_FILEGRP, IDENTIFIER_PRIORITY

from .ocrd_xml_base import OcrdXmlDocument, ET
from .ocrd_file import OcrdFile

class OcrdMets(OcrdXmlDocument):

    def __init__(self, file_by_id=None, *args, **kwargs):
        super(OcrdMets, self).__init__(*args, **kwargs)
        if file_by_id is None:
            file_by_id = {}
        self._file_by_id = file_by_id

    def __str__(self):
        return 'OcrdMets[fileGrps=%s,files=%s]' % (self.file_groups, self.find_files())

    @property
    def unique_identifier(self):
        for t in IDENTIFIER_PRIORITY:
            found = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            if found is not None:
                return found.text

    @property
    def file_groups(self):
        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_files(self, fileGrp=None, groupId=None, mimetype=None):
        """
        List files.

        Args:
            fileGrp (string) : USE of the fileGrp to list files of
            groupId (string) : GROUPID of matching files
            mimetype (string) : MIMETYPE of matching files

        Return:
            List of files.
        """
        ret = []
        fileGrp_clause = '' if fileGrp is None else '[@USE="%s"]' % fileGrp
        file_clause = ''
        if groupId is not None:
            file_clause += '[@GROUPID="%s"]' % groupId
        if mimetype is not None:
            file_clause += '[@MIMETYPE="%s"]' % mimetype

        file_els = self._tree.getroot().findall(".//mets:fileGrp%s/mets:file%s" % (fileGrp_clause, file_clause), NS)
        for el in file_els:
            file_id = el.get('ID')
            if file_id not in self._file_by_id:
                self._file_by_id[file_id] = OcrdFile(el)
            ret.append(self._file_by_id[file_id])
        return ret

    def add_file_group(self, fileGrp):
        el_fileGrp = ET.SubElement(self._tree.getroot().find('.//mets:fileSec', NS), TAG_METS_FILEGRP)
        el_fileGrp.set('USE', fileGrp)
        return el_fileGrp

    def add_file(self, fileGrp, mimetype=None, url=None, ID=None, local_filename=None):
        el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (fileGrp), NS)
        if el_fileGrp is None:
            el_fileGrp = self.add_file_group(fileGrp)
        mets_file = OcrdFile(ET.SubElement(el_fileGrp, TAG_METS_FILE))
        mets_file.url = url
        mets_file.mimetype = mimetype
        mets_file.ID = ID
        mets_file.local_filename = local_filename
        return mets_file
