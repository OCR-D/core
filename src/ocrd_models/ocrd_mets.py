"""
API to METS
"""
from datetime import datetime
import re
from lxml import etree as ET
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ocrd_utils import (
    getLogger,
    generate_range,
    VERSION,
    REGEX_PREFIX,
    REGEX_FILE_ID
)

from ocrd_utils.config import config

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
    METS_PAGE_DIV_ATTRIBUTE
)

from .ocrd_xml_base import OcrdXmlDocument, ET      # type: ignore
from .ocrd_file import OcrdFile
from .ocrd_agent import OcrdAgent

REGEX_PREFIX_LEN = len(REGEX_PREFIX)

class OcrdMets(OcrdXmlDocument):
    """
    API to a single METS file
    """
    _cache_flag : bool
    # Cache for the pages (mets:div)
    # The dictionary's Key: 'div.ID'
    # The dictionary's Value: a 'div' object at some memory location
    _page_cache : Dict[METS_PAGE_DIV_ATTRIBUTE, Dict[str, ET._Element]]
    # Cache for the files (mets:file) - two nested dictionaries
    # The outer dictionary's Key: 'fileGrp.USE'
    # The outer dictionary's Value: Inner dictionary
    # The inner dictionary's Key: 'file.ID'
    # The inner dictionary's Value: a 'file' object at some memory location
    _file_cache : Dict[str, Dict[str, ET._Element]]
    # Cache for the file pointers (mets:fptr) - two nested dictionaries
    # The outer dictionary's Key: 'div.ID'
    # The outer dictionary's Value: Inner dictionary
    # The inner dictionary's Key: 'fptr.FILEID'
    # The inner dictionary's Value: a 'fptr' object at some memory location
    _fptr_cache : Dict[str, Dict[str, ET._Element]]

    @staticmethod
    def empty_mets(now : Optional[str] = None, cache_flag : bool = False):
        """
        Create an empty METS file from bundled template.
        """
        if not now:
            now = datetime.now().isoformat()
        tpl = METS_XML_EMPTY
        tpl = tpl.replace('{{ VERSION }}', VERSION)
        tpl = tpl.replace('{{ NOW }}', '%s' % now)
        return OcrdMets(content=tpl.encode('utf-8'), cache_flag=cache_flag)

    def __init__(self, **kwargs) -> None:
        """
        """
        super(OcrdMets, self).__init__(**kwargs)

        # XXX If the environment variable OCRD_METS_CACHING is set to "true",
        # then enable caching, if "false", disable caching, overriding the
        # kwarg to the constructor
        if config.is_set('OCRD_METS_CACHING'):
            getLogger('ocrd.models.ocrd_mets').debug('METS Caching %s because OCRD_METS_CACHING is %s',
                    'enabled' if config.OCRD_METS_CACHING else 'disabled', config.raw_value('OCRD_METS_CACHING'))
            self._cache_flag = config.OCRD_METS_CACHING


        # If cache is enabled
        if self._cache_flag:
            self._initialize_caches()
            self._refresh_caches()

    def __str__(self) -> str:
        """
        String representation
        """
        return 'OcrdMets[cached=%s,fileGrps=%s,files=%s]' % (
        self._cache_flag, self.file_groups, list(self.find_files()))

    def _fill_caches(self) -> None:
        """
        Fills the caches with fileGrps and FileIDs
        """

        tree_root = self._tree.getroot()

        # Fill with files
        el_fileSec = tree_root.find("mets:fileSec", NS)
        if el_fileSec is None:
            return

        log = getLogger('ocrd.models.ocrd_mets._fill_caches-files')

        for el_fileGrp in el_fileSec.findall('mets:fileGrp', NS):
            fileGrp_use = el_fileGrp.get('USE')

            # Assign an empty dictionary that will hold the files of the added fileGrp
            self._file_cache[fileGrp_use] = {}

            for el_file in el_fileGrp:
                file_id = el_file.get('ID')
                self._file_cache[fileGrp_use].update({file_id: el_file})
                # log.info("File added to the cache: %s" % file_id)

        # Fill with pages
        el_div_list = tree_root.findall(".//mets:div[@TYPE='page']", NS)
        if len(el_div_list) == 0:
            return
        log = getLogger('ocrd.models.ocrd_mets._fill_caches-pages')

        for el_div in el_div_list:
            div_id = el_div.get('ID')
            log.debug("DIV_ID: %s" % el_div.get('ID'))

            for attr in METS_PAGE_DIV_ATTRIBUTE:
                self._page_cache[attr][str(el_div.get(attr.name))] = el_div

            # Assign an empty dictionary that will hold the fptr of the added page (div)
            self._fptr_cache[div_id] = {}

            # log.info("Page_id added to the cache: %s" % div_id)

            for el_fptr in el_div:
                self._fptr_cache[div_id].update({el_fptr.get('FILEID'): el_fptr})
                # log.info("Fptr added to the cache: %s" % el_fptr.get('FILEID'))

        # log.info("Len of page_cache: %s" % len(self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID]))
        # log.info("Len of fptr_cache: %s" % len(self._fptr_cache))

    def _initialize_caches(self) -> None:
        self._file_cache = {}
        # NOTE we can only guarantee uniqueness for @ID and @ORDER
        self._page_cache = {k : {} for k in METS_PAGE_DIV_ATTRIBUTE}
        self._fptr_cache = {}

    def _refresh_caches(self) -> None:
        if self._cache_flag:
            self._initialize_caches()

            # Note, if the empty_mets() function is used to instantiate OcrdMets
            # Then the cache is empty even after this operation
            self._fill_caches()

    @property
    def unique_identifier(self) -> Optional[str]:
        """
        Get the unique identifier by looking through ``mods:identifier``
        See `specs <https://ocr-d.de/en/spec/mets#unique-id-for-the-document-processed>`_ for details.
        """
        for t in IDENTIFIER_PRIORITY:
            found = self._tree.getroot().find('.//mods:identifier[@type="%s"]' % t, NS)
            if found is not None:
                return found.text

    @unique_identifier.setter
    def unique_identifier(self, purl : str) -> None:
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
            assert mods is not None
            id_el = ET.SubElement(mods, TAG_MODS_IDENTIFIER)
            id_el.set('type', 'purl')
        id_el.text = purl

    @property
    def agents(self) -> List[OcrdAgent]:
        """
        List all :py:class:`ocrd_models.ocrd_agent.OcrdAgent`s
        """
        return [OcrdAgent(el_agent) for el_agent in self._tree.getroot().findall('mets:metsHdr/mets:agent', NS)]

    def add_agent(self, *args, **kwargs) -> OcrdAgent:
        """
        Add an :py:class:`ocrd_models.ocrd_agent.OcrdAgent` to the list of agents in the ``metsHdr``.
        """
        el_metsHdr = self._tree.getroot().find('.//mets:metsHdr', NS)
        if el_metsHdr is None:
            el_metsHdr = ET.Element(TAG_METS_METSHDR)
            self._tree.getroot().insert(0, el_metsHdr)
        #  assert(el_metsHdr is not None)
        el_agent = ET.Element(TAG_METS_AGENT)
        try:
            el_agent_last = next(el_metsHdr.iterchildren(tag=TAG_METS_AGENT, reversed=True))
            el_agent_last.addnext(el_agent)
        except StopIteration:
            el_metsHdr.insert(0, el_agent)
        return OcrdAgent(el_agent, *args, **kwargs)

    @property
    def file_groups(self) -> List[str]:
        """
        List the `@USE` of all `mets:fileGrp` entries.
        """

        # WARNING: Actually we cannot return strings in place of elements!
        if self._cache_flag:
            return list(self._file_cache.keys())

        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_all_files(self, *args, **kwargs) -> List[OcrdFile]:
        """
        Like :py:meth:`find_files` but return a list of all results.
        Equivalent to ``list(self.find_files(...))``
        """
        return list(self.find_files(*args, **kwargs))

    # pylint: disable=multiple-statements
    def find_files(
        self,
        ID : Optional[str] = None,
        fileGrp : Optional[str] = None,
        pageId : Optional[str] = None,
        mimetype : Optional[str] = None,
        url : Optional[str] = None,
        local_filename : Optional[str] = None,
        local_only : bool = False,
        include_fileGrp : Optional[List[str]] = None,
        exclude_fileGrp : Optional[List[str]] = None,
    ) -> Iterator[OcrdFile]:
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
            url (string) : ``@xlink:href`` remote/original URL of ``mets:Flocat`` of ``mets:file``
            local_filename (string) : ``@xlink:href`` local/cached filename of ``mets:Flocat`` of ``mets:file``
            mimetype (string) : ``@MIMETYPE`` of ``mets:file``
            local (boolean) : Whether to restrict results to local files in the filesystem
            include_fileGrp (list[str]) : List of allowed file groups
            exclude_fileGrp (list[str]) : List of disallowd file groups
        Yields:
            :py:class:`ocrd_models:ocrd_file:OcrdFile` instantiations
        """
        pageId_list = []
        if pageId:
            # returns divs instead of strings of ids
            physical_pages = self.get_physical_pages(for_pageIds=pageId, return_divs=True)
            for div in physical_pages:
                if self._cache_flag:
                    pageId_list += self._fptr_cache[div.get('ID')]
                else:
                    pageId_list += [fptr.get('FILEID') for fptr in div.findall('mets:fptr', NS)]

        if ID and ID.startswith(REGEX_PREFIX):
            ID = re.compile(ID[REGEX_PREFIX_LEN:])
        if fileGrp and fileGrp.startswith(REGEX_PREFIX):
            fileGrp = re.compile(fileGrp[REGEX_PREFIX_LEN:])
        if mimetype and mimetype.startswith(REGEX_PREFIX):
            mimetype = re.compile(mimetype[REGEX_PREFIX_LEN:])
        if url and url.startswith(REGEX_PREFIX):
            url = re.compile(url[REGEX_PREFIX_LEN:])

        candidates = []
        if self._cache_flag:
            if fileGrp:
                if isinstance(fileGrp, str):
                    candidates += self._file_cache.get(fileGrp, {}).values()
                else:
                    candidates = [x for fileGrp_needle, el_file_list in self._file_cache.items() if
                                  fileGrp.match(fileGrp_needle) for x in el_file_list.values()]
            else:
                candidates = [el_file for id_to_file in self._file_cache.values() for el_file in id_to_file.values()]
        else:
            candidates = self._tree.getroot().xpath('//mets:file', namespaces=NS)

        for cand in candidates:
            if ID:
                if isinstance(ID, str):
                    if not ID == cand.get('ID'): continue
                else:
                    if not ID.fullmatch(cand.get('ID')): continue

            if pageId is not None and cand.get('ID') not in pageId_list:
                continue

            if not self._cache_flag and fileGrp:
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
                cand_locat = cand.find('mets:FLocat[@LOCTYPE="URL"]', namespaces=NS)
                if cand_locat is None:
                    continue
                cand_url = cand_locat.get('{%s}href' % NS['xlink'])
                if isinstance(url, str):
                    if cand_url != url: continue
                else:
                    if not url.fullmatch(cand_url): continue

            if local_filename:
                cand_locat = cand.find('mets:FLocat[@LOCTYPE="OTHER"][@OTHERLOCTYPE="FILE"]', namespaces=NS)
                if cand_locat is None:
                    continue
                cand_local_filename = cand_locat.get('{%s}href' % NS['xlink'])
                if isinstance(local_filename, str):
                    if cand_local_filename != local_filename: continue
                else:
                    if not local_filename.fullmatch(cand_local_filename): continue

            if local_only:
                # deprecation_warning("'local_only' is deprecated, use 'local_filename=\"//.+\"' instead")
                is_local = cand.find('mets:FLocat[@LOCTYPE="OTHER"][@OTHERLOCTYPE="FILE"][@xlink:href]', namespaces=NS)
                if is_local is None:
                    continue

            ret = OcrdFile(cand, mets=self)

            # XXX include_fileGrp is redundant to fileGrp but for completeness
            if exclude_fileGrp and ret.fileGrp in exclude_fileGrp:
                continue
            if include_fileGrp and ret.fileGrp not in include_fileGrp:
                continue

            yield ret

    def add_file_group(self, fileGrp: str) -> ET._Element:
        """
        Add a new ``mets:fileGrp``.
        Arguments:
            fileGrp (string): ``@USE`` of the new ``mets:fileGrp``.
        """
        if ',' in fileGrp:
            raise ValueError('fileGrp must not contain commas')
        el_fileSec = self._tree.getroot().find('mets:fileSec', NS)
        if el_fileSec is None:
            el_fileSec = ET.SubElement(self._tree.getroot(), TAG_METS_FILESEC)
        el_fileGrp = el_fileSec.find('mets:fileGrp[@USE="%s"]' % fileGrp, NS)
        if el_fileGrp is None:
            el_fileGrp = ET.SubElement(el_fileSec, TAG_METS_FILEGRP)
            el_fileGrp.set('USE', fileGrp)

            if self._cache_flag:
                # Assign an empty dictionary that will hold the files of the added fileGrp
                self._file_cache[fileGrp] = {}

        return el_fileGrp

    def rename_file_group(self, old: str, new: str) -> None:
        """
        Rename a ``mets:fileGrp`` by changing the ``@USE`` from :py:attr:`old` to :py:attr:`new`.
        """
        el_fileGrp = self._tree.getroot().find('mets:fileSec/mets:fileGrp[@USE="%s"]' % old, NS)
        if el_fileGrp is None:
            raise FileNotFoundError("No such fileGrp '%s'" % old)
        el_fileGrp.set('USE', new)

        if self._cache_flag:
            self._file_cache[new] = self._file_cache.pop(old)

    def remove_file_group(self, USE: str, recursive : bool = False, force : bool = False) -> None:
        """
        Remove a ``mets:fileGrp`` (single fixed ``@USE`` or multiple regex ``@USE``)
        Arguments:
            USE (string): ``@USE`` of the ``mets:fileGrp`` to delete. Can be a regex if prefixed with ``//``
            recursive (boolean): Whether to recursively delete each ``mets:file`` in the group
            force (boolean): Do not raise an exception if ``mets:fileGrp`` does not exist
        """
        log = getLogger('ocrd.models.ocrd_mets.remove_file_group')
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
        if el_fileGrp is None:  # pylint: disable=len-as-condition
            msg = "No such fileGrp: %s" % USE
            if force:
                log.warning(msg)
                return
            raise Exception(msg)

        # The cache should also be used here
        if self._cache_flag:
            files = self._file_cache.get(el_fileGrp.get('USE'), {}).values()
        else:
            files = el_fileGrp.findall('mets:file', NS)

        if files:
            if not recursive:
                raise Exception("fileGrp %s is not empty and recursive wasn't set" % USE)
            for f in list(files):
                self.remove_one_file(ID=f.get('ID'), fileGrp=f.getparent().get('USE'))

        if self._cache_flag:
            # Note: Since the files inside the group are removed
            # with the 'remove_one_file' method above, 
            # we should not take care of that again.
            # We just remove the fileGrp.
            del self._file_cache[el_fileGrp.get('USE')]

        el_fileGrp.getparent().remove(el_fileGrp)

    def add_file(self, fileGrp : str, mimetype : Optional[str] = None, url : Optional[str] = None, 
                 ID : Optional[str] = None, pageId : Optional[str] = None, force : bool = False, 
                 local_filename : Optional[str] = None, ignore : bool = False, **kwargs) -> OcrdFile:
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

        el_fileGrp = self.add_file_group(fileGrp)
        if not ignore:
            mets_file = next(self.find_files(ID=ID, fileGrp=fileGrp), None)
            if mets_file:
                if mets_file.fileGrp == fileGrp and \
                        mets_file.pageId == pageId and \
                        mets_file.mimetype == mimetype:
                    if not force:
                        raise FileExistsError(
                            f"A file with ID=={ID} already exists {mets_file} and neither force nor ignore are set")
                    self.remove_file(ID=ID, fileGrp=fileGrp)
                else:
                    raise FileExistsError(
                        f"A file with ID=={ID} already exists {mets_file} but unrelated - cannot mitigate")

        # To get rid of Python's FutureWarning - checking if v is not None
        kwargs = {k: v for k, v in locals().items() if
                  k in ['url', 'ID', 'mimetype', 'pageId', 'local_filename'] and v is not None}
        # This separation is needed to reuse the same el_mets_file element in the caching if block
        el_mets_file = ET.SubElement(el_fileGrp, TAG_METS_FILE)
        # The caching of the physical page is done in the OcrdFile constructor
        mets_file = OcrdFile(el_mets_file, mets=self, **kwargs)

        if self._cache_flag:
            # Add the file to the file cache
            self._file_cache[fileGrp].update({ID: el_mets_file})

        return mets_file

    def remove_file(self, *args, **kwargs) -> Union[List[OcrdFile],OcrdFile]:
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
                return files[0]  # for backwards-compatibility
        if any(1 for kwarg in kwargs
               if isinstance(kwarg, str) and kwarg.startswith(REGEX_PREFIX)):
            # allow empty results if filter criteria involve a regex
            return []
        raise FileNotFoundError("File not found: %s %s" % (args, kwargs))

    def remove_one_file(self, ID : Union[str, OcrdFile], fileGrp : str = None) -> OcrdFile:
        """
        Delete an existing :py:class:`ocrd_models.ocrd_file.OcrdFile`.
        Arguments:
            ID (string|OcrdFile): ``@ID`` of the ``mets:file`` to delete  Can also be an :py:class:`ocrd_models.ocrd_file.OcrdFile` to avoid search via ``ID``.
            fileGrp (string): ``@USE`` of the ``mets:fileGrp`` containing the ``mets:file``. Used only for optimization.
        Returns:
            The old :py:class:`ocrd_models.ocrd_file.OcrdFile` reference.
        """
        log = getLogger('ocrd.models.ocrd_mets.remove_one_file')
        log.debug("remove_one_file(%s %s)" % (ID, fileGrp))
        if isinstance(ID, OcrdFile):
            ocrd_file = ID
            ID = ocrd_file.ID
        else:
            ocrd_file = next(self.find_files(ID=ID, fileGrp=fileGrp), None)

        if not ocrd_file:
            raise FileNotFoundError("File not found: %s (fileGr=%s)" % (ID, fileGrp))

        # Delete the physical page ref
        fptrs = []
        if self._cache_flag:
            for page in self._fptr_cache.keys():
                if ID in self._fptr_cache[page]:
                    fptrs.append(self._fptr_cache[page][ID])
        else:
            fptrs = self._tree.getroot().findall('.//mets:fptr[@FILEID="%s"]' % ID, namespaces=NS)

        # Delete the physical page ref
        for fptr in fptrs:
            log.debug("Delete fptr element %s for page '%s'", fptr, ID)
            page_div = fptr.getparent()
            page_div.remove(fptr)
            # Remove the fptr from the cache as well
            if self._cache_flag:
                del self._fptr_cache[page_div.get('ID')][ID]
            # delete empty pages
            if not list(page_div):
                log.debug("Delete empty page %s", page_div)
                page_div.getparent().remove(page_div)
                # Delete the empty pages from caches as well
                if self._cache_flag:
                    for attr in METS_PAGE_DIV_ATTRIBUTE:
                        if attr.name in page_div.attrib:
                            del self._page_cache[attr][page_div.attrib[attr.name]]

        # Delete the file reference from the cache
        if self._cache_flag:
            parent_use = ocrd_file._el.getparent().get('USE')
            del self._file_cache[parent_use][ocrd_file.ID]

        # Delete the file reference
        # pylint: disable=protected-access
        ocrd_file._el.getparent().remove(ocrd_file._el)

        return ocrd_file

    @property
    def physical_pages(self) -> List[str]:
        """
        List all page IDs (the ``@ID`` of each physical ``mets:structMap`` ``mets:div``)
        """
        if self._cache_flag:
            return list(self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID].keys())

        return [str(x) for x in self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/@ID',
            namespaces=NS)]

    def get_physical_pages(self, for_fileIds : Optional[List[str]] = None, for_pageIds : Optional[str] = None, 
                           return_divs : bool = False) -> List[Union[str, ET._Element]]:
        """
        List all page IDs (the ``@ID`` of each physical ``mets:structMap`` ``mets:div``),
        optionally for a subset of ``mets:file`` ``@ID`` :py:attr:`for_fileIds`,
        or for a subset selector expression (comma-separated, range, and/or regex) :py:attr:`for_pageIds`.
        If return_divs is set, returns div memory objects instead of strings of ids
        """
        if for_fileIds is None and for_pageIds is None:
            return self.physical_pages
        # log = getLogger('ocrd.models.ocrd_mets.get_physical_pages')
        if for_pageIds is not None:
            ret = []
            page_attr_patterns = []
            page_attr_patterns_raw = re.split(r',', for_pageIds)
            for pageId_token in page_attr_patterns_raw:
                if pageId_token.startswith(REGEX_PREFIX):
                    page_attr_patterns.append((None, re.compile(pageId_token[REGEX_PREFIX_LEN:])))
                elif '..' in pageId_token:
                    val_range = generate_range(*pageId_token.split('..', 1))
                    page_attr_patterns.append(val_range)
                else:
                    page_attr_patterns.append(pageId_token)
            if not page_attr_patterns:
                return []
            range_patterns_first_last = [(x[0], x[-1]) if isinstance(x, list) else None for x in page_attr_patterns]
            page_attr_patterns_copy = list(page_attr_patterns)
            if self._cache_flag:
                for pat in page_attr_patterns:
                    try:
                        attr : METS_PAGE_DIV_ATTRIBUTE
                        if isinstance(pat, str):
                            attr = next(a for a in list(METS_PAGE_DIV_ATTRIBUTE) if pat in self._page_cache[a])
                            cache_keys = [pat]
                        elif isinstance(pat, list):
                            attr = next(a for a in list(METS_PAGE_DIV_ATTRIBUTE) if any(x in self._page_cache[a] for x in pat))
                            cache_keys = [v for v in pat if v in self._page_cache[attr]]
                            for k in cache_keys:
                                pat.remove(k)
                        elif isinstance(pat, tuple):
                            _, re_pat = pat
                            attr = next(a for a in list(METS_PAGE_DIV_ATTRIBUTE) for v in self._page_cache[a] if re_pat.fullmatch(v))
                            cache_keys = [v for v in self._page_cache[attr] if re_pat.fullmatch(v)]
                        else:
                            raise ValueError
                        if return_divs:
                            ret += [self._page_cache[attr][v] for v in cache_keys]
                        else:
                            ret += [self._page_cache[attr][v].get('ID') for v in cache_keys]
                    except StopIteration:
                        raise ValueError(f"{pat} matches none of the keys of any of the _page_caches.")
            else:
                page_attr_patterns_matched = []
                for page in self._tree.getroot().xpath(
                        'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]',
                        namespaces=NS):
                    patterns_exhausted = []
                    for pat_idx, pat in enumerate(page_attr_patterns):
                        try:
                            if isinstance(pat, str):
                                attr = next(a for a in list(METS_PAGE_DIV_ATTRIBUTE) if pat == page.get(a.name))
                                ret.append(page if return_divs else page.get('ID'))
                                patterns_exhausted.append(pat)
                            elif isinstance(pat, list):
                                if not isinstance(pat[0], METS_PAGE_DIV_ATTRIBUTE):
                                    pat.insert(0, next(a for a in list(METS_PAGE_DIV_ATTRIBUTE) if any(x == page.get(a.name) for x in pat)))
                                attr_val = page.get(pat[0].name)
                                if attr_val in pat:
                                    pat.remove(attr_val)
                                    ret.append(page if return_divs else page.get('ID'))
                                if len(pat) == 1:
                                    patterns_exhausted.append(pat)
                            elif isinstance(pat, tuple):
                                attr, re_pat = pat
                                if not attr:
                                    attr = next(a for a in list(METS_PAGE_DIV_ATTRIBUTE) if re_pat.fullmatch(page.get(a.name) or ''))
                                    page_attr_patterns[pat_idx] = (attr, re_pat)
                                if re_pat.fullmatch(page.get(attr.name) or ''):
                                    ret.append(page if return_divs else page.get('ID'))
                            else:
                                raise ValueError
                            page_attr_patterns_matched.append(pat)
                        except StopIteration:
                            continue
                    for p in patterns_exhausted:
                        page_attr_patterns.remove(p)
                unmatched = [x for x in page_attr_patterns_copy if x not in page_attr_patterns_matched]
                if unmatched:
                    raise ValueError(f"Patterns {unmatched} match none of the pages")

            ranges_without_start_match = []
            ranges_without_last_match = []
            for idx, pat in enumerate(page_attr_patterns_copy):
                if isinstance(pat, list):
                    start, last = range_patterns_first_last[idx]
                    if start in pat:
                        print(pat, start, last)
                        ranges_without_start_match.append(page_attr_patterns_raw[idx])
                    # if last in pat:
                    #     ranges_without_last_match.append(page_attr_patterns_raw[idx])
            if ranges_without_start_match:
                raise ValueError(f"Start of range patterns {ranges_without_start_match} not matched - invalid range")
            # if ranges_without_last_match:
            #     raise ValueError(f"End of range patterns {ranges_without_last_match} not matched - invalid range")
            return ret

        if for_fileIds == []:
            return []
        assert for_fileIds # at this point we know for_fileIds is set, assert to convince pyright
        ret = [None] * len(for_fileIds)
        if self._cache_flag:
            for pageId in self._fptr_cache.keys():
                for fptr in self._fptr_cache[pageId].keys():
                    if fptr in for_fileIds:
                        index = for_fileIds.index(fptr)
                        if return_divs:
                            ret[index] = self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID][pageId]
                        else:
                            ret[index] = pageId
        else:
            for page in self._tree.getroot().xpath(
                    'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]',
                    namespaces=NS):
                for fptr in page.findall('mets:fptr', NS):
                    if fptr.get('FILEID') in for_fileIds:
                        index = for_fileIds.index(fptr.get('FILEID'))
                        if return_divs:
                            ret[index] = page
                        else:
                            ret[index] = page.get('ID')
        return ret

    def set_physical_page_for_file(self, pageId : str, ocrd_file : OcrdFile, 
                                   order : Optional[str] = None, orderlabel : Optional[str] = None) -> None:
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

        # delete any existing page mapping for this file.ID
        fptrs = []
        if self._cache_flag:
            for page_id in self._fptr_cache.keys():
                if ocrd_file.ID in self._fptr_cache[page_id].keys():
                    if self._fptr_cache[page_id][ocrd_file.ID] is not None:
                        fptrs.append(self._fptr_cache[page_id][ocrd_file.ID])
        else:
            fptrs = self._tree.getroot().findall(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' %
                ocrd_file.ID, namespaces=NS)

        for el_fptr in fptrs:
            if self._cache_flag:
                del self._fptr_cache[el_fptr.getparent().get('ID')][ocrd_file.ID]
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

        el_pagediv = None
        if self._cache_flag:
            if pageId in self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID]:
                el_pagediv = self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID][pageId]
        else:
            el_pagediv = el_seqdiv.find('mets:div[@ID="%s"]' % pageId, NS)

        if el_pagediv is None:
            el_pagediv = ET.SubElement(el_seqdiv, TAG_METS_DIV)
            el_pagediv.set('TYPE', 'page')
            el_pagediv.set('ID', pageId)
            if order:
                el_pagediv.set('ORDER', order)
            if orderlabel:
                el_pagediv.set('ORDERLABEL', orderlabel)
            if self._cache_flag:
                # Create a new entry in the page cache
                self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID][pageId] = el_pagediv
                # Create a new entry in the fptr cache and 
                # assign an empty dictionary to hold the fileids
                self._fptr_cache.setdefault(pageId, {})

        el_fptr = ET.SubElement(el_pagediv, TAG_METS_FPTR)
        el_fptr.set('FILEID', ocrd_file.ID)

        if self._cache_flag:
            # Assign the ocrd fileID to the pageId in the cache
            self._fptr_cache[pageId].update({ocrd_file.ID: el_fptr})

    def update_physical_page_attributes(self, page_id : str, **kwargs) -> None:
        invalid_keys = list(k for k in kwargs.keys() if k not in METS_PAGE_DIV_ATTRIBUTE.names())
        if invalid_keys:
            raise ValueError(f"Invalid attribute {invalid_keys}. Allowed values: {METS_PAGE_DIV_ATTRIBUTE.names()}")

        page_div = self.get_physical_pages(for_pageIds=page_id, return_divs=True)
        if not page_div:
            raise ValueError(f"Could not find mets:div[@ID=={page_id}]")
        page_div = page_div[0]

        for k, v in kwargs.items():
            if not v:
                page_div.attrib.pop(k)
            else:
                page_div.attrib[k] = v

    def get_physical_page_for_file(self, ocrd_file : OcrdFile) -> Optional[str]:
        """
        Get the physical page ID (``@ID`` of the physical ``mets:structMap`` ``mets:div`` entry)
        corresponding to the ``mets:file`` :py:attr:`ocrd_file`.
        """
        if self._cache_flag:
            for pageId in self._fptr_cache.keys():
                if ocrd_file.ID in self._fptr_cache[pageId].keys():
                    return pageId
        else:
            ret = self._tree.getroot().find(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' %
                ocrd_file.ID, namespaces=NS)
            if ret is not None:
                return ret.getparent().get('ID')

    def remove_physical_page(self, ID : str) -> None:
        """
        Delete page (physical ``mets:structMap`` ``mets:div`` entry ``@ID``) :py:attr:`ID`.
        """
        mets_div = None
        if self._cache_flag:
            if ID in self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID].keys():
                mets_div = [self._page_cache[METS_PAGE_DIV_ATTRIBUTE.ID][ID]]
        else:
            mets_div = self._tree.getroot().xpath(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][@ID="%s"]' % ID,
                namespaces=NS)
        if mets_div:
            mets_div_attrib = {** mets_div[0].attrib}
            mets_div[0].getparent().remove(mets_div[0])
            if self._cache_flag:
                for attr in METS_PAGE_DIV_ATTRIBUTE:
                    if attr.name in mets_div_attrib:
                        del self._page_cache[attr][mets_div_attrib[attr.name]]
                del self._fptr_cache[ID]

    def remove_physical_page_fptr(self, fileId : str) -> List[str]:
        """
        Delete all ``mets:fptr[@FILEID = fileId]`` to ``mets:file[@ID == fileId]`` for :py:attr:`fileId` from all ``mets:div`` entries in the physical ``mets:structMap``.
        Returns:
            List of pageIds that mets:fptrs were deleted from
        """

        # Question: What is the reason to keep a list of mets_fptrs?
        # Do we have a situation in which the fileId is same for different pageIds ?
        # From the examples I have seen inside 'assets' that is not the case
        # and the mets_fptrs list will always contain a single element.
        # If that's the case then we do not need to iterate 2 loops, just one.
        mets_fptrs = []
        if self._cache_flag:
            for page_id in self._fptr_cache.keys():
                if fileId in self._fptr_cache[page_id].keys():
                    mets_fptrs.append(self._fptr_cache[page_id][fileId])
        else:
            mets_fptrs = self._tree.getroot().xpath(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' % fileId,
                namespaces=NS)
        ret = []
        for mets_fptr in mets_fptrs:
            mets_div = mets_fptr.getparent()
            ret.append(mets_div.get('ID'))
            if self._cache_flag:
                del self._fptr_cache[mets_div.get('ID')][mets_fptr.get('FILEID')]
            mets_div.remove(mets_fptr)
        return ret

    @property
    def physical_pages_labels(self) -> Dict[str, Tuple[Optional[str], Optional[str], Optional[str]]]:
        """
        Map all page IDs (the ``@ID`` of each physical ``mets:structMap`` ``mets:div``) to their
        ``@ORDER``, ``@ORDERLABEL`` and ``@LABEL`` attributes, if any.
        """
        divs = self._tree.getroot().xpath(
            'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]',
            namespaces=NS)
        return {div.get('ID'): (div.get('ORDER', None), div.get('ORDERLABEL', None), div.get('LABEL', None))
                for div in divs}

    def merge(self, other_mets, force : bool = False, 
              fileGrp_mapping : Optional[Dict[str, str]] = None, 
              fileId_mapping : Optional[Dict[str, str]] = None, 
              pageId_mapping : Optional[Dict[str, str]] = None,
              after_add_cb : Optional[Callable[[OcrdFile], Any]] = None, **kwargs) -> None:
        """
        Add all files from other_mets.
        Accepts the same kwargs as :py:func:`find_files`
        Keyword Args:
            force (boolean): Whether to :py:meth:`add_file`s with force (overwriting existing ``mets:file``s)
            fileGrp_mapping (dict): Map :py:attr:`other_mets` fileGrp to fileGrp in this METS
            fileId_mapping (dict): Map :py:attr:`other_mets` file ID to file ID in this METS
            pageId_mapping (dict): Map :py:attr:`other_mets` page ID to page ID in this METS
            after_add_cb (function): Callback received after file is added to the METS
        """
        if not fileGrp_mapping:
            fileGrp_mapping = {}
        if not fileId_mapping:
            fileId_mapping = {}
        if not pageId_mapping:
            pageId_mapping = {}
        for f_src in other_mets.find_files(**kwargs):
            f_dest = self.add_file(
                fileGrp_mapping.get(f_src.fileGrp, f_src.fileGrp),
                mimetype=f_src.mimetype,
                url=f_src.url,
                local_filename=f_src.local_filename,
                ID=fileId_mapping.get(f_src.ID, f_src.ID),
                pageId=pageId_mapping.get(f_src.pageId, f_src.pageId),
                force=force)
            # FIXME: merge metsHdr, amdSec, dmdSec as well
            # FIXME: merge structMap logical and structLink as well
            if after_add_cb:
                after_add_cb(f_dest)

