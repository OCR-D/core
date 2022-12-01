"""
API to METS
"""
from datetime import datetime
import re
import typing
from os import environ
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

        # XXX If the environment variable OCRD_METS_CACHING is set to "true",
        # then enable caching, if "false", disable caching, overriding the
        # kwarg to the constructor
        if 'OCRD_METS_CACHING' in environ:
            cache_override = environ['OCRD_METS_CACHING'] in ('true', '1')
            getLogger('ocrd_models.ocrd_mets').debug('METS Caching %s because OCRD_METS_CACHING is %s',
                    'enabled' if cache_override else 'disabled', environ['OCRD_METS_CACHING'])
            self._cache_flag = cache_override

        # If cache is enabled
        if self._cache_flag:
            self.refresh_caches()

    def __exit__(self):
        """

        """
        if self._cache_flag:
            self._clear_caches()

    def __str__(self):
        """
        String representation
        """
        return 'OcrdMets[cached=%s,fileGrps=%s,files=%s]' % (self._cache_flag, self.file_groups, list(self.find_files()))

    def _fill_caches(self):
        """
        Fills the caches with fileGrps and FileIDs
        """

        tree_root = self._tree.getroot()

        # Fill with files
        el_fileSec = tree_root.find("mets:fileSec", NS)
        if el_fileSec is None:
            return

        log = getLogger('ocrd_models.ocrd_mets._fill_caches-files')

        for el_fileGrp in el_fileSec.findall('mets:fileGrp', NS):
            fileGrp_use = el_fileGrp.get('USE')

            # Assign an empty dictionary that will hold the files of the added fileGrp
            self._file_cache[fileGrp_use] = {}

            for el_file in el_fileGrp:
                file_id = el_file.get('ID')
                self._file_cache[fileGrp_use].update({file_id : el_file})
                # log.info("File added to the cache: %s" % file_id)

        # Fill with pages
        el_div_list = tree_root.findall(".//mets:div[@TYPE='page']", NS)
        if len(el_div_list) == 0:
            return
        log = getLogger('ocrd_models.ocrd_mets._fill_caches-pages')

        for el_div in el_div_list:
            div_id = el_div.get('ID')
            log.debug("DIV_ID: %s" % el_div.get('ID'))

            self._page_cache[div_id] = el_div

            # Assign an empty dictionary that will hold the fptr of the added page (div)
            self._fptr_cache[div_id] = {}

            # log.info("Page_id added to the cache: %s" % div_id)

            for el_fptr in el_div:
                self._fptr_cache[div_id].update({el_fptr.get('FILEID') : el_fptr})
                # log.info("Fptr added to the cache: %s" % el_fptr.get('FILEID'))

        # log.info("Len of page_cache: %s" % len(self._page_cache))
        # log.info("Len of fptr_cache: %s" % len(self._fptr_cache))

    def _clear_caches(self):
        """
        Deallocates the caches
        """

        self._file_cache = None
        self._page_cache = None
        self._fptr_cache = None
        
    def refresh_caches(self):
        if self._cache_flag:
            # Cache for the files (mets:file) - two nested dictionaries
            # The outer dictionary's Key: 'fileGrp.USE'
            # The outer dictionary's Value: Inner dictionary
            # The inner dictionary's Key: 'file.ID'
            # The inner dictionary's Value: a 'file' object at some memory location
            self._file_cache = {}

            # Cache for the pages (mets:div)
            # The dictionary's Key: 'div.ID'
            # The dictionary's Value: a 'div' object at some memory location
            self._page_cache = {}

            # Cache for the file pointers (mets:fptr) - two nested dictionaries
            # The outer dictionary's Key: 'div.ID'
            # The outer dictionary's Value: Inner dictionary
            # The inner dictionary's Key: 'fptr.FILEID'
            # The inner dictionary's Value: a 'fptr' object at some memory location
            self._fptr_cache = {}
            
            # Note, if the empty_mets() function is used to instantiate OcrdMets
            # Then the cache is empty even after this operation
            self._fill_caches()
        
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

        # WARNING: Actually we cannot return strings in place of elements!
        if self._cache_flag:
           return list(self._file_cache.keys())

        return [el.get('USE') for el in self._tree.getroot().findall('.//mets:fileGrp', NS)]

    def find_all_files(self, *args, **kwargs):
        """
        Like :py:meth:`find_files` but return a list of all results.
        Equivalent to ``list(self.find_files(...))``
        """
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
        pageId_list = []
        if pageId:
            pageId_patterns = []
            for pageId_token in re.split(r',', pageId):
                if pageId_token.startswith(REGEX_PREFIX):
                    pageId_patterns.append(re.compile(pageId_token[REGEX_PREFIX_LEN:]))
                elif '..' in pageId_token:
                    pageId_patterns += generate_range(*pageId_token.split('..', 1))
                else:
                    pageId_patterns += [pageId_token]
            if self._cache_flag:
                for page_id in self._page_cache.keys():
                    if page_id in pageId_patterns or \
                        any([isinstance(p, typing.Pattern) and p.fullmatch(page_id) for p in pageId_patterns]):
                        pageId_list += self._fptr_cache[page_id]
            else:
                for page in self._tree.getroot().xpath(
                    '//mets:div[@TYPE="page"]', namespaces=NS):
                    if page.get('ID') in pageId_patterns or \
                        any([isinstance(p, typing.Pattern) and p.fullmatch(page.get('ID')) for p in pageId_patterns]):
                        pageId_list += [fptr.get('FILEID') for fptr in page.findall('mets:fptr', NS)]

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
                    candidates = [x for fileGrp_needle, el_file_list in self._file_cache.items() if fileGrp.match(fileGrp_needle) for x in el_file_list.values()]
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
                cand_locat = cand.find('mets:FLocat', namespaces=NS)
                if cand_locat is None:
                    continue
                cand_url = cand_locat.get('{%s}href' % NS['xlink'])
                if isinstance(url, str):
                    if cand_url != url: continue
                else:
                    if not url.fullmatch(cand_url): continue

            # Note: why we instantiate a class only to find out that the local_only is set afterwards
            # Checking local_only and url before instantiation should be better?
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
            
            if self._cache_flag:
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
        
        if self._cache_flag:
            self._file_cache[new] = self._file_cache.pop(old)

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
        log = getLogger('ocrd_models.ocrd_mets.add_file')

        el_fileGrp = self.add_file_group(fileGrp)
        if not ignore:
            mets_file = next(self.find_files(ID=ID, fileGrp=fileGrp), None)
            if mets_file:
                if mets_file.fileGrp == fileGrp and \
                   mets_file.pageId == pageId and \
                   mets_file.mimetype == mimetype:
                    if not force:
                        raise FileExistsError(f"A file with ID=={ID} already exists {mets_file} and neither force nor ignore are set")
                    self.remove_file(ID=ID, fileGrp=fileGrp)
                else:
                    raise FileExistsError(f"A file with ID=={ID} already exists {mets_file} but unrelated - cannot mitigate")

        # To get rid of Python's FutureWarning - checking if v is not None
        kwargs = {k: v for k, v in locals().items() if k in ['url', 'ID', 'mimetype', 'pageId', 'local_filename'] and v is not None}
        # This separation is needed to reuse the same el_mets_file element in the caching if block
        el_mets_file = ET.SubElement(el_fileGrp, TAG_METS_FILE)
        # The caching of the physical page is done in the OcrdFile constructor
        mets_file = OcrdFile(el_mets_file, mets=self, **kwargs)

        if self._cache_flag:
            # Add the file to the file cache
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

    def remove_one_file(self, ID, fileGrp=None):
        """
        Delete an existing :py:class:`ocrd_models.ocrd_file.OcrdFile`.
        Arguments:
            ID (string|OcrdFile): ``@ID`` of the ``mets:file`` to delete  Can also be an :py:class:`ocrd_models.ocrd_file.OcrdFile` to avoid search via ``ID``.
            fileGrp (string): ``@USE`` of the ``mets:fileGrp`` containing the ``mets:file``. Used only for optimization.
        Returns:
            The old :py:class:`ocrd_models.ocrd_file.OcrdFile` reference.
        """
        log = getLogger('ocrd_models.ocrd_mets.remove_one_file')
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
            if not page_div.getchildren():
                log.debug("Delete empty page %s", page_div)
                page_div.getparent().remove(page_div)
                # Delete the empty pages from caches as well
                if self._cache_flag:
                    del self._page_cache[page_div.get('ID')]
                    del self._fptr_cache[page_div.get('ID')]

        # Delete the file reference from the cache
        if self._cache_flag:
            parent_use = ocrd_file._el.getparent().get('USE')
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
        if self._cache_flag:
            return list(self._page_cache.keys())
            
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
        
        if self._cache_flag:
            for pageId in self._fptr_cache.keys():
                for fptr in self._fptr_cache[pageId].keys():
                    if fptr in for_fileIds:
                        ret[for_fileIds.index(fptr)] = pageId
        else:
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

        # delete any page mapping for this file.ID
        candidates = []
        if self._cache_flag:
            for page_id in self._fptr_cache.keys():
                if ocrd_file.ID in self._fptr_cache[page_id].keys():
                    if self._fptr_cache[page_id][ocrd_file.ID] is not None:
                        candidates.append(self._fptr_cache[page_id][ocrd_file.ID])
        else:
            candidates = self._tree.getroot().findall(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' %
                ocrd_file.ID, namespaces=NS)

        for el_fptr in candidates:
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
            if pageId in self._page_cache:
                el_pagediv = self._page_cache[pageId]
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
                self._page_cache[pageId] = el_pagediv
                # Create a new entry in the fptr cache and 
                # assign an empty dictionary to hold the fileids
                self._fptr_cache[pageId] = {}
                
        el_fptr = ET.SubElement(el_pagediv, TAG_METS_FPTR)
        el_fptr.set('FILEID', ocrd_file.ID)

        if self._cache_flag:
            # Assign the ocrd fileID to the pageId in the cache
            self._fptr_cache[el_pagediv.get('ID')].update({ocrd_file.ID : el_fptr})

    def get_physical_page_for_file(self, ocrd_file):
        """
        Get the physical page ID (``@ID`` of the physical ``mets:structMap`` ``mets:div`` entry)
        corresponding to the ``mets:file`` :py:attr:`ocrd_file`.
        """
        ret = []
        if self._cache_flag:
            for pageId in self._fptr_cache.keys():
                if ocrd_file.ID in self._fptr_cache[pageId].keys():
                    ret.append(self._page_cache[pageId].get('ID'))
        else:
            ret = self._tree.getroot().xpath(
                '/mets:mets/mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][./mets:fptr[@FILEID="%s"]]/@ID' %
                ocrd_file.ID, namespaces=NS)

        # To get rid of the python's FutureWarning
        if len(ret):
            return ret[0]

    def remove_physical_page(self, ID):
        """
        Delete page (physical ``mets:structMap`` ``mets:div`` entry ``@ID``) :py:attr:`ID`.
        """
        mets_div = None
        if self._cache_flag:
            if ID in self._page_cache.keys():
                mets_div = [self._page_cache[ID]]
        else:
            mets_div = self._tree.getroot().xpath(
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"][@ID="%s"]' % ID,
                namespaces=NS)
        if mets_div:
            mets_div[0].getparent().remove(mets_div[0])
            if self._cache_flag:
                del self._page_cache[ID]
                del self._fptr_cache[ID]

    def remove_physical_page_fptr(self, fileId):
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
                'mets:structMap[@TYPE="PHYSICAL"]/mets:div[@TYPE="physSequence"]/mets:div[@TYPE="page"]/mets:fptr[@FILEID="%s"]' % fileId, namespaces=NS)
        ret = []
        for mets_fptr in mets_fptrs:
            mets_div = mets_fptr.getparent()
            ret.append(mets_div.get('ID'))
            if self._cache_flag:
                del self._fptr_cache[mets_div.get('ID')][mets_fptr.get('FILEID')]
            mets_div.remove(mets_fptr)
        return ret

    def merge(self, other_mets, force=False, fileGrp_mapping=None, fileId_mapping=None, pageId_mapping=None, after_add_cb=None, **kwargs):
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
                    ID=fileId_mapping.get(f_src.ID, f_src.ID),
                    pageId=pageId_mapping.get(f_src.pageId, f_src.pageId),
                    force=force)
            # FIXME: merge metsHdr, amdSec, dmdSec as well
            # FIXME: merge structMap logical and structLink as well
            if after_add_cb:
                after_add_cb(f_dest)
