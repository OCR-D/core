"""
API to METS
"""
from datetime import datetime
from re import fullmatch
from lxml import etree as ET

from ocrd_utils import is_local_filename, getLogger, VERSION, REGEX_PREFIX, REGEX_FILE_ID

from .constants import (
    NAMESPACES as NS,
    TAG_METS_AGENT,
    TAG_METS_DIV,
    TAG_METS_FILE,
    TAG_METS_FILEGRP,
    TAG_METS_FILESEC,
    TAG_METS_FPTR,
    TAG_METS_METSHDR,
    TAG_METS_STRUCTMAP,
    IDENTIFIER_PRIORITY,
    TAG_MODS_IDENTIFIER,
    METS_XML_EMPTY,
)

from .ocrd_xml_base import OcrdXmlDocument, ET
from .ocrd_file import OcrdFile
from .ocrd_agent import OcrdAgent

REGEX_PREFIX_LEN = len(REGEX_PREFIX)

class OcrdMets(OcrdXmlDocument):
    """
    API to a single METS file
    """

    @staticmethod
    def empty_mets(now=None):
        """
        Create an empty METS file from bundled template.
        """
        if not now:
            now = datetime.now().isoformat()
        tpl = METS_XML_EMPTY.decode('utf-8')
        tpl = tpl.replace('{{ VERSION }}', VERSION)
        tpl = tpl.replace('{{ NOW }}', '%s' % now)
        return OcrdMets(content=tpl.encode('utf-8'))

    def __init__(self, **kwargs):
        """

        """
        super(OcrdMets, self).__init__(**kwargs)

    def __str__(self):
        """
        String representation
        """
        return 'OcrdMets[fileGrps=%s,files=%s]' % (self.file_groups, list(self.find_files()))

    @property
    def unique_identifier(self):
        """
        Get the unique identifier by looking through ``mods:identifier``

        See `specs <https://ocr-d.github.io/mets#unique-id-for-the-document-processed>`_ for details.
        """
        for t in IDENTIFIER_PRIORITY:
            found = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            if found is not None:
                return found.text

    @unique_identifier.setter
    def unique_identifier(self, purl):
        """
        Set the unique identifier by looking through ``mods:identifier``

        See `specs <https://ocr-d.github.io/mets#unique-id-for-the-document-processed>`_ for details.
        """
        id_el = None
        for t in IDENTIFIER_PRIORITY:
            id_el = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            if id_el is not None:
                break
        if id_el is None:
            mods = self._tree.getroot().find('.//mods:mods', NS)
            id_el = ET.SubElement(mods, TAG_MODS_IDENTIFIER)
            id_el.set('type', 'purl')
        id_el.text = purl

    @property
    def agents(self):
        """
        List all `OcrdAgent </../../ocrd_models/ocrd_models.ocrd_agent.html>`_
        """
        return [OcrdAgent(el_agent) for el_agent in self._tree.getroot().findall('mets:metsHdr/mets:agent', NS)]

    def add_agent(self, *args, **kwargs):
        """
        Add an `OcrdAgent </../../ocrd_models/ocrd_models.ocrd_agent.html>`_ to the list of agents in the metsHdr.
        """
        el_metsHdr = self._tree.getroot().find('.//mets:metsHdr', NS)
        if el_metsHdr is None:
            el_metsHdr = ET.Element(TAG_METS_METSHDR)
            self._tree.getroot().insert(0, el_metsHdr)
        #  assert(el_metsHdr is not None)
        el_agent = ET.SubElement(el_metsHdr, TAG_METS_AGENT)
        #  print(ET.tostring(el_metsHdr))
        return OcrdAgent(el_agent, *args, **kwargs)

    @property
    def file_groups(self):
        """
        List the ``USE`` attributes of all ``mets:fileGrp``.
        """
        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_all_files(self, *args, **kwargs):
        """
        Like find_files but return a list of all results.

        Equivalent to ``list(self.find_files(...))``
        """
        return list(self.find_files(*args, **kwargs))

    # pylint: disable=multiple-statements
    def find_files(self, ID=None, fileGrp=None, pageId=None, mimetype=None, url=None, local_only=False):
        """
        Search ``mets:file`` in this METS document and yield results.


        The ``ID``, ``fileGrp``, ``url`` and ``mimetype`` parameters can be
        either a literal string or a regular expression if the string starts
        with ``//`` (double slash). If it is a regex, the leading ``//`` is removed
        and candidates are matched against the regex with ``re.fullmatch``. If it is
        a literal string, comparison is done with string equality.

        Args:
            ID (string) : ID of the file
            fileGrp (string) : USE of the fileGrp to list files of
            pageId (string) : ID of physical page manifested by matching files
            url (string) : @xlink:href of mets:Flocat of mets:file
            mimetype (string) : MIMETYPE of matching files
            local (boolean) : Whether to restrict results to local files

        Return:
            List of files.
        """
        ret = []
        if pageId:
            if pageId.startswith(REGEX_PREFIX):
                raise Exception("find_files does not support regex search for pageId")
            pageIds, pageId = pageId.split(','), list()
            for page in self._tree.getroot().xpath(
                '//mets:div[@TYPE="page"]', namespaces=NS):
                if page.get('ID') in pageIds:
                    pageId.extend(
                        [fptr.get('FILEID') for fptr in page.findall('mets:fptr', NS)])
        for cand in self._tree.getroot().xpath('//mets:file', namespaces=NS):
            if ID:
                if ID.startswith(REGEX_PREFIX):
                    if not fullmatch(ID[REGEX_PREFIX_LEN:], cand.get('ID')): continue
                else:
                    if not ID == cand.get('ID'): continue

            if pageId is not None and cand.get('ID') not in pageId:
                continue

            if fileGrp:
                if fileGrp.startswith(REGEX_PREFIX):
                    if not fullmatch(fileGrp[REGEX_PREFIX_LEN:], cand.getparent().get('USE')): continue
                else:
                    if cand.getparent().get('USE') != fileGrp: continue

            if mimetype:
                if mimetype.startswith(REGEX_PREFIX):
                    if not fullmatch(mimetype[REGEX_PREFIX_LEN:], cand.get('MIMETYPE') or ''): continue
                else:
                    if cand.get('MIMETYPE') != mimetype: continue

            if url:
                cand_locat = cand.find('mets:FLocat', namespaces=NS)
                if cand_locat is None:
                    continue
                cand_url = cand_locat.get('{%s}href' % NS['xlink'])
                if url.startswith(REGEX_PREFIX):
                    if not fullmatch(url[REGEX_PREFIX_LEN:], cand_url): continue
                else:
                    if cand_url != url: continue

            f = OcrdFile(cand, mets=self)

            # If only local resources should be returned and f is not a file path: skip the file
            if local_only and not is_local_filename(f.url):
                continue
            yield f

    def add_file_group(self, fileGrp):
        """
        Add a new ``mets:fileGrp``.

        Arguments:
            fileGrp (string): ``USE`` attribute of the new filegroup.
        """
        if ',' in fileGrp:
            raise Exception('fileGrp must not contain commas')
        el_fileSec = self._tree.getroot().find('mets:fileSec', NS)
        if el_fileSec is None:
            el_fileSec = ET.SubElement(self._tree.getroot(), TAG_METS_FILESEC)
        el_fileGrp = el_fileSec.find('mets:fileGrp[@USE="%s"]' % fileGrp, NS)
        if el_fileGrp is None:
            el_fileGrp = ET.SubElement(el_fileSec, TAG_METS_FILEGRP)
            el_fileGrp.set('USE', fileGrp)
        return el_fileGrp

    def remove_file_group(self, USE, recursive=False, force=False):
        """
        Remove a fileGrp (fixed ``USE``) or fileGrps (regex ``USE``)

        Arguments:
            USE (string): USE attribute of the fileGrp to delete. Can be a regex if prefixed with //
            recursive (boolean): Whether to recursively delete all files in the group
            force (boolean): Do not raise an exception if file group doesn't exist
        """
        log = getLogger('ocrd_models.ocrd_mets.remove_file_group')
        el_fileSec = self._tree.getroot().find('mets:fileSec', NS)
        if el_fileSec is None:
            raise Exception("No fileSec!")
        if isinstance(USE, str):
            if USE.startswith(REGEX_PREFIX):
                for cand in el_fileSec.findall('mets:fileGrp', NS):
                    if fullmatch(USE[REGEX_PREFIX_LEN:], cand.get('USE')):
                        self.remove_file_group(cand, recursive=recursive)
                return
            else:
                el_fileGrp = el_fileSec.find('mets:fileGrp[@USE="%s"]' % USE, NS)
        else:
            el_fileGrp = USE
        if el_fileGrp is None:   # pylint: disable=len-as-condition
            msg = "No such fileGrp: %s" % USE
            if force:
                log.warning(msg)
                return
            raise Exception(msg)
        files = el_fileGrp.findall('mets:file', NS)
        if files:
            if not recursive:
                raise Exception("fileGrp %s is not empty and recursive wasn't set" % USE)
            for f in files:
                self.remove_one_file(f.get('ID'))
        el_fileGrp.getparent().remove(el_fileGrp)

    def add_file(self, fileGrp, mimetype=None, url=None, ID=None, pageId=None, force=False, local_filename=None, ignore=False, **kwargs):
        """
        Add a `OcrdFile </../../ocrd_models/ocrd_models.ocrd_file.html>`_.

        Arguments:
            fileGrp (string): Add file to ``mets:fileGrp`` with this ``USE`` attribute
            mimetype (string):
            url (string):
            ID (string):
            pageId (string):
            force (boolean): Whether to add the file even if a ``mets:file`` with the same ``ID`` already exists.
            ignore (boolean): Don't look for existing files. Shift responsibility for preventing errors from duplicate ID to the user.
            local_filename (string):
            mimetype (string):
        """
        if not ID:
            raise Exception("Must set ID of the mets:file")
        elif not REGEX_FILE_ID.fullmatch(ID):
            raise Exception("Invalid syntax for mets:file/@ID %s" % ID)
        el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (fileGrp), NS)
        if el_fileGrp is None:
            el_fileGrp = self.add_file_group(fileGrp)
        if ID and not ignore and next(self.find_files(ID=ID), None):
            if not force:
                raise Exception("File with ID='%s' already exists" % ID)
            mets_file = next(self.find_files(ID=ID))
        else:
            mets_file = OcrdFile(ET.SubElement(el_fileGrp, TAG_METS_FILE), mets=self)
        mets_file.url = url
        mets_file.mimetype = mimetype
        mets_file.ID = ID
        mets_file.pageId = pageId
        mets_file.local_filename = local_filename

        return mets_file

    def remove_file(self, *args, **kwargs):
        """
        Delete all files matching the query. Same arguments as ``OcrdMets.find_files``
        """
        files = list(self.find_files(*args, **kwargs))
        if files:
            for f in files:
                self.remove_one_file(f)
            if len(files) > 1:
                return files
            else:
                return files[0] # for backwards-compatibility
        raise FileNotFoundError("File not found: %s %s" % (args, kwargs))

    def remove_one_file(self, ID):
        """
        Delete a `OcrdFile </../../ocrd_models/ocrd_models.ocrd_file.html>`_.
        """
        log = getLogger('ocrd_models.ocrd_mets.remove_one_file')
        log.info("remove_one_file(%s)" % ID)
        if isinstance(ID, OcrdFile):
            ocrd_file = ID
            ID = ocrd_file.ID
        else:
            ocrd_file = next(self.find_files(ID=ID), None)

        if not ocrd_file:
            raise FileNotFoundError("File not found: %s" % ID)

        # Delete the physical page ref
        for fptr in self._tree.getroot().findall('.//mets:fptr[@FILEID="%s"]' % ID, namespaces=NS):
            log.info("Delete fptr element %s for page '%s'", fptr, ID)
            page_div = fptr.getparent()
            page_div.remove(fptr)
            # delete empty pages
            if not page_div.getchildren():
                log.info("Delete empty page %s", page_div)
                page_div.getparent().remove(page_div)

        # Delete the file reference
        # pylint: disable=protected-access
        ocrd_file._el.getparent().remove(ocrd_file._el)

        return ocrd_file

    @property
    def physical_pages(self):
        """
        List all page IDs
        """
        return self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/@ID',
            namespaces=NS)

    def get_physical_pages(self, for_fileIds=None):
        """
        List all page IDs (optionally for a subset of file IDs)
        """
        if for_fileIds is None:
            return self.physical_pages
        ret = [None] * len(for_fileIds)
        for page in self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]',
                namespaces=NS):
            for fptr in page.findall('mets:fptr', NS):
                if fptr.get('FILEID') in for_fileIds:
                    ret[for_fileIds.index(fptr.get('FILEID'))] = page.get('ID')
        return ret

    def set_physical_page_for_file(self, pageId, ocrd_file, order=None, orderlabel=None):
        """
        Create a new physical page
        """
        #  print(pageId, ocrd_file)
        # delete any page mapping for this file.ID
        for el_fptr in self._tree.getroot().findall(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' %
                ocrd_file.ID, namespaces=NS):
            el_fptr.getparent().remove(el_fptr)

        # find/construct as necessary
        el_structmap = self._tree.getroot().find('mets:structMap[@TYPE="PHYSICAL"]', NS)
        if el_structmap is None:
            el_structmap = ET.SubElement(self._tree.getroot(), TAG_METS_STRUCTMAP)
            el_structmap.set('TYPE', 'PHYSICAL')
        el_seqdiv = el_structmap.find('mets:div[@TYPE="physSequence"]', NS)
        if el_seqdiv is None:
            el_seqdiv = ET.SubElement(el_structmap, TAG_METS_DIV)
            el_seqdiv.set('TYPE', 'physSequence')
        el_pagediv = el_seqdiv.find('mets:div[@ID="%s"]' % pageId, NS)
        if el_pagediv is None:
            el_pagediv = ET.SubElement(el_seqdiv, TAG_METS_DIV)
            el_pagediv.set('TYPE', 'page')
            el_pagediv.set('ID', pageId)
            if order:
                el_pagediv.set('ORDER', order)
            if orderlabel:
                el_pagediv.set('ORDERLABEL', orderlabel)
        el_fptr = ET.SubElement(el_pagediv, TAG_METS_FPTR)
        el_fptr.set('FILEID', ocrd_file.ID)

    def get_physical_page_for_file(self, ocrd_file):
        """
        Get the pageId for a ocrd_file
        """
        ret = self._tree.getroot().xpath(
            '/mets:mets/mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][./mets:fptr[@FILEID="%s"]]/@ID' %
            ocrd_file.ID, namespaces=NS)
        if ret:
            return ret[0]

    def remove_physical_page(self, ID):
        mets_div = self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][@ID="%s"]' % ID,
            namespaces=NS)
        if mets_div:
            mets_div[0].getparent().remove(mets_div[0])
