from datetime import datetime

from ocrd.constants import (
    NAMESPACES as NS,
    TAG_METS_FILE,
    TAG_METS_FILEGRP,
    IDENTIFIER_PRIORITY,
    TAG_MODS_IDENTIFIER,
    METS_XML_EMPTY,
    VERSION
)

from .ocrd_xml_base import OcrdXmlDocument, ET
from .ocrd_file import OcrdFile

class OcrdMets(OcrdXmlDocument):

    @staticmethod
    def empty_mets():
        tpl = METS_XML_EMPTY.decode('utf-8')
        tpl = tpl.replace('{{ VERSION }}', VERSION)
        tpl = tpl.replace('{{ NOW }}', '%s' % datetime.now())
        return OcrdMets(content=tpl.encode('utf-8'))

    def __init__(self, file_by_id=None, **kwargs):
        super(OcrdMets, self).__init__(**kwargs)
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

    @unique_identifier.setter
    def unique_identifier(self, purl):
        for t in IDENTIFIER_PRIORITY:
            id_el = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            break
        if id_el is None:
            mods = self._tree.getroot().find('.//mods:mods', NS)
            id_el = ET.SubElement(mods, TAG_MODS_IDENTIFIER)
            id_el.set('type', 'purl')
        id_el.text = purl

    @property
    def file_groups(self):
        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_files(self, ID=None, fileGrp=None, groupId=None, mimetype=None, local_only=False):
        """
        List files.

        Args:
            ID (string) : ID of the file
            fileGrp (string) : USE of the fileGrp to list files of
            groupId (string) : GROUPID of matching files
            mimetype (string) : MIMETYPE of matching files
            local (boolean) : Whether to restrict results to local files, i.e. file://-URL

        Return:
            List of files.
        """
        ret = []
        fileGrp_clause = '' if fileGrp is None else '[@USE="%s"]' % fileGrp
        file_clause = ''
        if ID is not None:
            file_clause += '[@ID="%s"]' % ID
        if groupId is not None:
            file_clause += '[@GROUPID="%s"]' % groupId
        if mimetype is not None:
            file_clause += '[@MIMETYPE="%s"]' % mimetype
        # TODO lxml says invalid predicate. I disagree
        #  if local_only:
        #      file_clause += "[mets:FLocat[starts-with(@xlink:href, 'file://')]]"

        file_els = self._tree.getroot().findall(".//mets:fileGrp%s/mets:file%s" % (fileGrp_clause, file_clause), NS)
        for el in file_els:
            file_id = el.get('ID')
            if file_id not in self._file_by_id:
                self._file_by_id[file_id] = OcrdFile(el)
            if local_only:
                url = el.find('mets:FLocat', NS).get('{%s}href' % NS['xlink'])
                if not url.startswith('file://'):
                    continue
            ret.append(self._file_by_id[file_id])
        return ret

    def add_file_group(self, fileGrp):
        el_fileGrp = ET.SubElement(self._tree.getroot().find('.//mets:fileSec', NS), TAG_METS_FILEGRP)
        el_fileGrp.set('USE', fileGrp)
        return el_fileGrp

    def add_file(self, fileGrp, mimetype=None, url=None, ID=None, groupId=None, force=False, local_filename=None):
        el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (fileGrp), NS)
        if el_fileGrp is None:
            el_fileGrp = self.add_file_group(fileGrp)
        if ID is not None and self.find_files(ID=ID) != []:
            if not force:
                raise Exception("File with ID='%s' already exists" % ID)
            mets_file = self.find_files(ID=ID)[0]
        else:
            mets_file = OcrdFile(ET.SubElement(el_fileGrp, TAG_METS_FILE))
        mets_file.url = url
        mets_file.groupId = groupId
        mets_file.mimetype = mimetype
        mets_file.ID = ID
        mets_file.local_filename = local_filename
        return mets_file
