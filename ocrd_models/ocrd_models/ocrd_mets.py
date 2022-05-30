"""
API to METS
"""
from datetime import datetime
import re
from lxml import etree as ET
from copy import deepcopy

from ocrd_utils import (
    is_local_filename,
    getLogger,
    generate_range,
    VERSION,
    REGEX_PREFIX,
    REGEX_FILE_ID
)

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
    def empty_mets(now=None, cache_flag=False):
        """
        Create an empty METS file from bundled template.
        """
        if not now:
            now = datetime.now().isoformat()
        tpl = METS_XML_EMPTY.decode('utf-8')
        tpl = tpl.replace('{{ VERSION }}', VERSION)
        tpl = tpl.replace('{{ NOW }}', '%s' % now)
        return OcrdMets(content=tpl.encode('utf-8'), cache_flag=cache_flag)

    def __init__(self, **kwargs):
        """

        """
        super(OcrdMets, self).__init__(**kwargs)

        # If cache is enabled
        if self._cache_flag:
            # Cache for the fileGrps (mets:fileGrp) - a dictionary with Key and Value pair:
            # Key: 'fileGrp.USE'
            # Value: a 'fileGrp' object at some memory location 
            self._fileGrp_cache = {}

            # Cache for the files (mets:file) - two nested dictionaries
            # The outer dictionary's Key: 'fileGrp.USE'
            # The outer dictionary's Value: Inner dictionary
            # The inner dictionary's Key: 'file.ID'
            # The inner dictionary's Value: a 'file' object at some memory location
            self._file_cache = {}

            # Note, if the empty_mets() function is used to instantiate OcrdMets
            # Then the cache is empty even after this operation
            self._fill_caches()

    def __exit__(self):
        if self._cache_flag:
            self._clear_caches()

    def __str__(self):
        """
        String representation
        """
        return 'OcrdMets[fileGrps=%s,files=%s]' % (self.file_groups, list(self.find_files()))

    def _fill_caches(self):
        """
        Fills the caches with fileGrps and FileIDs
        """

        tree_root = self._tree.getroot()
        el_fileGrp_list = tree_root.find(".//mets:fileSec", NS)
        if el_fileGrp_list is None or len(el_fileGrp_list) == 0:
            return

        for el_fileGrp in el_fileGrp_list:
            fileGrp_use = el_fileGrp.get('USE')

            # NOTE: For some reason the el_fileGrp_list contains None values
            # when testing with the SBB0000F29300010000/data/mets.xml
            if fileGrp_use is None:
                continue

            self._fileGrp_cache[fileGrp_use] = el_fileGrp
            print("_fill_caches> file group added to the cache: %s" % fileGrp_use)

            # Assign an empty dictionary that will hold the files of the added fileGrp
            self._file_cache[fileGrp_use] = {}

            for el_file in el_fileGrp:
                file_id = el_file.get('ID')
                self._file_cache[fileGrp_use].update({file_id : el_file})
                print("_fill_caches> file added to the cache: %s" % file_id)

        print("_fill_caches> total fileGrp cache elements: %s" % len(self._fileGrp_cache))

    def _clear_caches(self):
        """
        Deallocates the caches
        """

        fileGrp_counter = 0

        for key in list(self._fileGrp_cache):
            del self._fileGrp_cache[key]
            fileGrp_counter += 1

        # print("_clear_caches> total cleared fileGrp cache elements: %d" % fileGrp_counter)

        for key in list(self._file_cache):
            for inner_key in list(self._file_cache[key]):
                del self._file_cache[key][inner_key]
            del self._file_cache[key]

    @property
    def unique_identifier(self):
        """
        Get the unique identifier by looking through ``mods:identifier``

        See `specs <https://ocr-d.de/en/spec/mets#unique-id-for-the-document-processed>`_ for details.
        """
        for t in IDENTIFIER_PRIORITY:
            found = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            if found is not None:
                return found.text

    @unique_identifier.setter
    def unique_identifier(self, purl):
        """
        Set the unique identifier by looking through ``mods:identifier``

        See `specs <https://ocr-d.de/en/spec/mets#unique-id-for-the-document-processed>`_ for details.
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
        List all :py:class:`ocrd_models.ocrd_agent.OcrdAgent`s
        """
        return [OcrdAgent(el_agent) for el_agent in self._tree.getroot().findall('mets:metsHdr/mets:agent', NS)]

    def add_agent(self, *args, **kwargs):
        """
        Add an :py:class:`ocrd_models.ocrd_agent.OcrdAgent` to the list of agents in the ``metsHdr``.
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
        List the `@USE` of all `mets:fileGrp` entries.
        """
        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_all_files(self, *args, **kwargs):
        """
        Like :py:meth:`find_files` but return a list of all results.

        Equivalent to ``list(self.find_files(...))``
        """

        # NOTE: This code gets complex with the REGEX.
        # Having two separate funcitons: with REGEX and without REGEX would simplify things
        if self._cache_flag:
            matches = []

            # If only both the fileGrp and ID parameters have been passed
            # Faster search in the cache
            if 'ID' in kwargs and 'fileGrp' in kwargs and 'pageId' not in kwargs and 'mimetype' not in kwargs and 'url' not in kwargs:
                fileGrp = kwargs['fileGrp']
                fileID = kwargs['ID']

                if fileID.startswith(REGEX_PREFIX):
                    fileID = re.compile(fileID[REGEX_PREFIX_LEN:])
                if fileGrp.startswith(REGEX_PREFIX):
                    fileGrp = re.compile(fileGrp[REGEX_PREFIX_LEN:])

                # Case where no regex pattern is given and
                # exact match could be obtained
                if (isinstance(fileID, str) and isinstance(fileGrp, str)):
                    if fileGrp in self._file_cache:  
                        if fileID in self._file_cache[fileGrp]:
                            matches.append(OcrdFile(self._file_cache[fileGrp][fileID], mets=self))
                elif isinstance(fileGrp, str):
                    # fileGrp is str and fileID is regex
                    if fileGrp in self._file_cache:
                        for fileID_str in self._file_cache[fileGrp]:
                            if fileID.fullmatch(fileID_str):
                                matches.append(OcrdFile(self._file_cache[fileGrp_str][fileID_str], mets=self))

                elif isinstance(fileID, str):
                    # fileID is str and fileGrp is regex
                    for fileGrp_str in self._file_cache:
                        if fileGrp.fullmatch(fileGrp_str):
                            if fileID in self._file_cache[fileGrp_str]:
                                matches.append(OcrdFile(self._file_cache[fileGrp_str][fileID], mets=self))

                else:
                    # both are regex: this has a really bad performance since
                    # we have to iterate all groups and all files to check for matches
                    for fileGrp_str in self._file_cache:
                        if fileGrp.fullmatch(fileGrp_str):
                            for fileID_str in self._file_cache[fileGrp_str]:
                                if fileID.fullmatch(fileID_str):
                                    matches.append(OcrdFile(self._file_cache[fileGrp_str][fileID_str], mets=self))

                return matches

            # If only the fileGrp parameter has been passed
            # Return a list with all files of that fileGrp from the cache
            if 'fileGrp' in kwargs and 'ID' not in kwargs and 'pageId' not in kwargs and 'mimetype' not in kwargs and 'url' not in kwargs:
                fileGrp = kwargs['fileGrp']

                if fileGrp.startswith(REGEX_PREFIX):
                    fileGrp = re.compile(fileGrp[REGEX_PREFIX_LEN:])

                    for fileGrp_str in self._file_cache:
                        print("Type(fileGrp): %s, Type(fileGrp_str): %s" % (type(fileGrp), type(fileGrp_str)))
                        if fileGrp.fullmatch(fileGrp_str):
                            for fileID in self._file_cache[fileGrp_str]:
                                matches.append(OcrdFile(self._file_cache[fileGrp_str][fileID], mets=self))
                else:
                    if fileGrp in self._file_cache:
                        for fileID in self._file_cache[fileGrp]:
                            matches.append(OcrdFile(self._file_cache[fileGrp][fileID], mets=self))

                return matches

            # If only the ID parameter has been passed
            # Return a list with that fileID inside or an empty list if not in cache
            if 'ID' in kwargs and 'fileGrp' not in kwargs and 'pageId' not in kwargs and 'mimetype' not in kwargs and 'url' not in kwargs:
                fileID = kwargs['ID']

                if fileID.startswith(REGEX_PREFIX):
                    fileID = re.compile(fileID[REGEX_PREFIX_LEN:])
                    for fileGrp_str in self._file_cache:
                        for fileID_str in self._file_cache[fileGrp_str]:
                            if fileID.fullmatch(fileID_str):
                                matches.append(OcrdFile(self._file_cache[fileGrp_str][fileID_str], mets=self))

                else:
                    for fileGrp_str in self._file_cache:
                        if fileID in self._file_cache[fileGrp_str]:
                            matches.append(OcrdFile(self._file_cache[fileGrp_str][fileID], mets=self))

                return matches

        # Run the old routine if cache is not enabled
        # or search based on parameters other than fileGrp and fileID are used
        return list(self.find_files(*args, **kwargs))

    # pylint: disable=multiple-statements
    def find_files(self, ID=None, fileGrp=None, pageId=None, mimetype=None, url=None, local_only=False):
        """
        Search ``mets:file`` entries in this METS document and yield results.


        The :py:attr:`ID`, :py:attr:`pageId`, :py:attr:`fileGrp`,
        :py:attr:`url` and :py:attr:`mimetype` parameters can each be either a
        literal string, or a regular expression if the string starts with
        ``//`` (double slash).

        If it is a regex, the leading ``//`` is removed and candidates are matched
        against the regex with `re.fullmatch`. If it is a literal string, comparison
        is done with string equality.

        The :py:attr:`pageId` parameter supports the numeric range operator ``..``. For
        example, to find all files in pages ``PHYS_0001`` to ``PHYS_0003``,
        ``PHYS_0001..PHYS_0003`` will be expanded to ``PHYS_0001,PHYS_0002,PHYS_0003``.

        Keyword Args:
            ID (string) : ``@ID`` of the ``mets:file``
            fileGrp (string) : ``@USE`` of the ``mets:fileGrp`` to list files of
            pageId (string) : ``@ID`` of the corresponding physical ``mets:structMap`` entry (physical page)
            url (string) : ``@xlink:href`` (URL or path) of ``mets:Flocat`` of ``mets:file``
            mimetype (string) : ``@MIMETYPE`` of ``mets:file``
            local (boolean) : Whether to restrict results to local files in the filesystem

        Yields:
            :py:class:`ocrd_models:ocrd_file:OcrdFile` instantiations
        """
        if pageId:
            if pageId.startswith(REGEX_PREFIX):
                pageIds, pageId = re.compile(pageId[REGEX_PREFIX_LEN:]), list()
            else:
                pageIds, pageId = pageId.split(','), list()
                pageIds_expanded = []
                for pageId_ in pageIds:
                    if '..' in pageId_:
                        pageIds_expanded += generate_range(*pageId_.split('..', 2))
                pageIds += pageIds_expanded
            for page in self._tree.getroot().xpath(
                '//mets:div[@TYPE="page"]', namespaces=NS):
                if (page.get('ID') in pageIds if isinstance(pageIds, list) else
                    pageIds.fullmatch(page.get('ID'))):
                    pageId.extend(
                        [fptr.get('FILEID') for fptr in page.findall('mets:fptr', NS)])
        if ID and ID.startswith(REGEX_PREFIX):
            ID = re.compile(ID[REGEX_PREFIX_LEN:])
        if fileGrp and fileGrp.startswith(REGEX_PREFIX):
            fileGrp = re.compile(fileGrp[REGEX_PREFIX_LEN:])
        if mimetype and mimetype.startswith(REGEX_PREFIX):
            mimetype = re.compile(mimetype[REGEX_PREFIX_LEN:])
        if url and url.startswith(REGEX_PREFIX):
            url = re.compile(url[REGEX_PREFIX_LEN:])

        for cand in self._tree.getroot().xpath('//mets:file', namespaces=NS):
            if ID:
                if isinstance(ID, str):
                    if not ID == cand.get('ID'): continue
                else:
                    if not ID.fullmatch(cand.get('ID')): continue

            if pageId is not None and cand.get('ID') not in pageId:
                continue

            if fileGrp:
                if isinstance(fileGrp, str):
                    if cand.getparent().get('USE') != fileGrp: continue
                else:
                    if not fileGrp.fullmatch(cand.getparent().get('USE')): continue

            if mimetype:
                if isinstance(mimetype, str):
                    if cand.get('MIMETYPE') != mimetype: continue
                else:
                    if not mimetype.fullmatch(cand.get('MIMETYPE') or ''): continue

            if url:
                cand_locat = cand.find('mets:FLocat', namespaces=NS)
                if cand_locat is None:
                    continue
                cand_url = cand_locat.get('{%s}href' % NS['xlink'])
                if isinstance(url, str):
                    if cand_url != url: continue
                else:
                    if not url.fullmatch(cand_url): continue

            f = OcrdFile(cand, mets=self)

            # If only local resources should be returned and f is not a file path: skip the file
            if local_only and not is_local_filename(f.url):
                continue
            yield f

    def add_file_group(self, fileGrp):
        """
        Add a new ``mets:fileGrp``.

        Arguments:
            fileGrp (string): ``@USE`` of the new ``mets:fileGrp``.
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

            # Add the fileGrp to both caches
            if self._cache_flag:
                self._fileGrp_cache[fileGrp] = el_fileGrp 
                # Assign an empty dictionary that will hold the files of the added fileGrp
                self._file_cache[fileGrp] = {}

        return el_fileGrp

    def rename_file_group(self, old, new):
        """
        Rename a ``mets:fileGrp`` by changing the ``@USE`` from :py:attr:`old` to :py:attr:`new`.
        """
        el_fileGrp = self._tree.getroot().find('mets:fileSec/mets:fileGrp[@USE="%s"]' % old, NS)
        if el_fileGrp is None:
            raise FileNotFoundError("No such fileGrp '%s'" % old)
        el_fileGrp.set('USE', new)

        # Rename the fileGrp in both caches
        if self._cache_flag:
            self._fileGrp_cache[new] = self._fileGrp_cache.pop(old)
            self._file_cache[new] = deepcopy(self._file_cache.pop(old))

    def remove_file_group(self, USE, recursive=False, force=False):
        """
        Remove a ``mets:fileGrp`` (single fixed ``@USE`` or multiple regex ``@USE``)

        Arguments:
            USE (string): ``@USE`` of the ``mets:fileGrp`` to delete. Can be a regex if prefixed with ``//``
            recursive (boolean): Whether to recursively delete each ``mets:file`` in the group
            force (boolean): Do not raise an exception if ``mets:fileGrp`` does not exist
        """
        log = getLogger('ocrd_models.ocrd_mets.remove_file_group')
        el_fileSec = self._tree.getroot().find('mets:fileSec', NS)
        if el_fileSec is None:
            raise Exception("No fileSec!")
        if isinstance(USE, str):
            if USE.startswith(REGEX_PREFIX):
                use = re.compile(USE[REGEX_PREFIX_LEN:])
                for cand in el_fileSec.findall('mets:fileGrp', NS):
                    if use.fullmatch(cand.get('USE')):
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

        # Remove the fileGrp from the caches
        if self._cache_flag:
            del self._fileGrp_cache[el_fileGrp.get('USE')]

            # Note: Since the files inside the group are removed
            # with the 'remove_one_file method' above, 
            # we should not take care of that again.
            # We just remove the fileGrp.
            del self._file_cache[el_fileGrp.get('USE')]

        el_fileGrp.getparent().remove(el_fileGrp)

    def add_file(self, fileGrp, mimetype=None, url=None, ID=None, pageId=None, force=False, local_filename=None, ignore=False, **kwargs):
        """
        Instantiate and add a new :py:class:`ocrd_models.ocrd_file.OcrdFile`.

        Arguments:
            fileGrp (string): ``@USE`` of ``mets:fileGrp`` to add to
        Keyword Args:
            mimetype (string): ``@MIMETYPE`` of the ``mets:file`` to use
            url (string): ``@xlink:href`` (URL or path) of the ``mets:file`` to use
            ID (string): ``@ID`` of the ``mets:file`` to use
            pageId (string): ``@ID`` in the physical ``mets:structMap`` to link to
            force (boolean): Whether to add the file even if a ``mets:file`` with the same ``@ID`` already exists.
            ignore (boolean): Do not look for existing files at all. Shift responsibility for preventing errors from duplicate ID to the user.
            local_filename (string):
        """
        if not ID:
            raise ValueError("Must set ID of the mets:file")
        if not fileGrp:
            raise ValueError("Must set fileGrp of the mets:file")
        if not REGEX_FILE_ID.fullmatch(ID):
            raise ValueError("Invalid syntax for mets:file/@ID %s (not an xs:ID)" % ID)
        if not REGEX_FILE_ID.fullmatch(fileGrp):
            raise ValueError("Invalid syntax for mets:fileGrp/@USE %s (not an xs:ID)" % fileGrp)

        el_fileGrp = None

        # If cache is enabled, check there
        if self._cache_flag: 
            if fileGrp in self._fileGrp_cache:
                el_fileGrp = self._fileGrp_cache[fileGrp]

        # cache is not enabled or fileGrp not in the cache
        if el_fileGrp is None:
            el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (fileGrp), NS)

        # the fileGrp is not in the XML tree as well
        if el_fileGrp is None:
            el_fileGrp = self.add_file_group(fileGrp)

        # Since we are sure that fileGrp parameter is set,
        # we could send that parameter to find_files for direct search
        mets_file = next(self.find_files(ID=ID, fileGrp=fileGrp), None)
        if mets_file and not ignore:
            if not force:
                raise Exception("File with ID='%s' already exists" % ID)
            mets_file.url = url
            mets_file.mimetype = mimetype
            mets_file.ID = ID
            mets_file.pageId = pageId
            mets_file.local_filename = local_filename
        else:
            kwargs = {k: v for k, v in locals().items() if k in ['url', 'ID', 'mimetype', 'pageId', 'local_filename'] and v}
            el_mets_file = ET.SubElement(el_fileGrp, TAG_METS_FILE)
            mets_file = OcrdFile(el_mets_file, mets=self, **kwargs)

            # Add the file to the cache
            if self._cache_flag:
                # print("add_file> Adding to the cache.[%s]" % ID)
                self._file_cache[fileGrp].update({ID: el_mets_file})

        return mets_file

    def remove_file(self, *args, **kwargs):
        """
        Delete each ``ocrd:file`` matching the query. Same arguments as :py:meth:`find_files`
        """
        files = list(self.find_files(*args, **kwargs))
        if files:
            for f in files:
                self.remove_one_file(f)
            if len(files) > 1:
                return files
            else:
                return files[0] # for backwards-compatibility
        if any(1 for kwarg in kwargs
               if isinstance(kwarg, str) and kwarg.startswith(REGEX_PREFIX)):
            # allow empty results if filter criteria involve a regex
            return []
        raise FileNotFoundError("File not found: %s %s" % (args, kwargs))

    def remove_one_file(self, ID):
        """
        Delete an existing :py:class:`ocrd_models.ocrd_file.OcrdFile`.

        Arguments:
            ID (string): ``@ID`` of the ``mets:file`` to delete

        Returns:
            The old :py:class:`ocrd_models.ocrd_file.OcrdFile` reference.
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

        # Remove the file from the file cache
        if self._cache_flag:
            parent_use = ocrd_file._el.getparent().get('USE')
            # Note: if the file is in the XML tree,
            # it should alse be in the file cache.
            # Anyway, we perform the checks, then remove
            if parent_use in self._file_cache:
                if ocrd_file.ID in self._file_cache[parent_use]:
                    del self._file_cache[parent_use][ocrd_file.ID]

        # Delete the file reference
        # pylint: disable=protected-access
        ocrd_file._el.getparent().remove(ocrd_file._el)

        return ocrd_file

    @property
    def physical_pages(self):
        """
        List all page IDs (the ``@ID`` of each physical ``mets:structMap`` ``mets:div``)
        """
        return self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/@ID',
            namespaces=NS)

    def get_physical_pages(self, for_fileIds=None):
        """
        List all page IDs (the ``@ID`` of each physical ``mets:structMap`` ``mets:div``),
        optionally for a subset of ``mets:file`` ``@ID`` :py:attr:`for_fileIds`.
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
        Set the physical page ID (``@ID`` of the physical ``mets:structMap`` ``mets:div`` entry)
        corresponding to the ``mets:file`` :py:attr:`ocrd_file`, creating all structures if necessary.

        Arguments:
            pageId (string): ``@ID`` of the physical ``mets:structMap`` entry to use
            ocrd_file (object): existing :py:class:`ocrd_models.ocrd_file.OcrdFile` object
        Keyword Args:
            order (string): ``@ORDER`` to use
            orderlabel (string): ``@ORDERLABEL`` to use
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
        Get the physical page ID (``@ID`` of the physical ``mets:structMap`` ``mets:div`` entry)
        corresponding to the ``mets:file`` :py:attr:`ocrd_file`.
        """
        ret = self._tree.getroot().xpath(
            '/mets:mets/mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][./mets:fptr[@FILEID="%s"]]/@ID' %
            ocrd_file.ID, namespaces=NS)
        if ret:
            return ret[0]

    def remove_physical_page(self, ID):
        """
        Delete page (physical ``mets:structMap`` ``mets:div`` entry ``@ID``) :py:attr:`ID`.
        """
        mets_div = self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][@ID="%s"]' % ID,
            namespaces=NS)
        if mets_div:
            mets_div[0].getparent().remove(mets_div[0])

    def remove_physical_page_fptr(self, fileId):
        """
        Delete all ``mets:fptr[@FILEID = fileId]`` to ``mets:file[@ID == fileId]`` for :py:attr:`fileId` from all ``mets:div`` entries in the physical ``mets:structMap``.
        Returns:
            List of pageIds that mets:fptrs were deleted from
        """
        mets_fptrs = self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' % fileId,
            namespaces=NS)
        ret = []
        for mets_fptr in mets_fptrs:
            mets_div = mets_fptr.getparent()
            ret.append(mets_div.get('ID'))
            mets_div.remove(mets_fptr)
        return ret

    def merge(self, other_mets, fileGrp_mapping=None, after_add_cb=None, **kwargs):
        """
        Add all files from other_mets.

        Accepts the same kwargs as :py:func:`find_files`

        Keyword Args:
            fileGrp_mapping (dict): Map :py:attr:`other_mets` fileGrp to fileGrp in this METS
            after_add_cb (function): Callback received after file is added to the METS
        """
        if not fileGrp_mapping:
            fileGrp_mapping = {}
        for f_src in other_mets.find_files(**kwargs):
            f_dest = self.add_file(
                    fileGrp_mapping.get(f_src.fileGrp, f_src.fileGrp),
                    mimetype=f_src.mimetype,
                    url=f_src.url,
                    ID=f_src.ID,
                    pageId=f_src.pageId)
            if after_add_cb:
                after_add_cb(f_dest)
