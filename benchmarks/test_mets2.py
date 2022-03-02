from itertools import product
from time import time
from copy import deepcopy

from pytest import main, fixture, mark

from ocrd import Resolver
from ocrd_utils import (
    MIME_TO_EXT,
    is_local_filename,
    getLogger,
    initLogging,
    generate_range,
    VERSION,
    REGEX_PREFIX,
    REGEX_FILE_ID
)

from ocrd_models import OcrdMets, OcrdFile
from lxml import etree as ET

from datetime import datetime
from pkg_resources import resource_string

from pprint import pprint
from memory_profiler import profile
import cProfile

NS = {
    'mets': "http://www.loc.gov/METS/",
    'mods': "http://www.loc.gov/mods/v3",
    'xlink': "http://www.w3.org/1999/xlink",
    'page': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15",
    'xsl': 'http://www.w3.org/1999/XSL/Transform#',
    'ocrd': 'https://ocr-d.de',
}

TAG_METS_FILE = '{%s}file' % NS['mets']

initLogging()
LOG = getLogger('ocrd.benchmark.mets')

REGIONS_PER_PAGE = 10
LINES_PER_REGION = 2

GRPS_REG = ['SEG-REG', 'SEG-REPAIR', 'SEG-REG-DESKEW', 'SEG-REG-DESKEW-CLIP', 'SEG-LINE', 'SEG-REPAIR-LINE', 'SEG-LINE-RESEG-DEWARP']
GRPS_IMG = ['FULL', 'PRESENTATION', 'BIN', 'CROP', 'BIN2', 'BIN-DENOISE', 'BIN-DENOISE-DESKEW', 'OCR']
FILES_PER_PAGE = len(GRPS_IMG) * 2 + len(GRPS_REG) * REGIONS_PER_PAGE

REGEX_PREFIX_LEN = len(REGEX_PREFIX)

class ExtendedOcrdMets(OcrdMets):

    @staticmethod    
    def empty_mets(now=None):
        """
        Create an empty METS file from bundled template.
        """
        if not now:
            now = datetime.now().isoformat()
        tpl = resource_string(__name__, 'mets-empty.xml').decode('utf-8')
        tpl = tpl.replace('{{ VERSION }}', VERSION)
        tpl = tpl.replace('{{ NOW }}', '%s' % now)
        return ExtendedOcrdMets(content=tpl.encode('utf-8'))

    def __init__(self, **kwargs):
        """

        """
        super(ExtendedOcrdMets, self).__init__(**kwargs)
        # Cache the tree root to avoid many calls of _tree.getroot()
        self._tree_root = None
        # { K('fileGrp.USE') : V(<Element {http://www.loc.gov/METS/}fileGrp at memoryLocationVal>)}
        self._fileGrp_cache = {}
        # { K('fileGrp.USE') : V( K('file.ID') : V(<Element {http://www.loc.gov/METS/}file at memoryLocationVal>))}
        self._file_cache = {}
    
    def __str__(self):
        """
        String representation
        """
        return 'ExtendedOcrdMets[fileGrps=%s,files=%s]' % (self.file_groups, list(self.find_files()))

    # Returns a list containing all mets:fileGrp inside the xml tree and the length of the list
    def get_all_fileGrps(self):
        if self._tree_root is None:
            # Get XML tree root
            tree_root = self._tree.getroot()

        el_fileGrp_list = tree_root.find(".//mets:fileSec", NS)
        return el_fileGrp_list
    
    # REGEX_PREFIX is not considered -> has to be tested!
    # Returns a reference pointer (element) of a fileGrp_USE (mets:fileGrp)
    # from the cache or the xml tree, or None if not found
    def get_a_fileGrp(self, fileGrp_USE=None):
        if fileGrp_USE is None:
            raise ValueError("fileGrp_USE cannot be 'None'!")
        
        # If the searched fileGrp is inside the cache, return it
        if fileGrp_USE in self._fileGrp_cache:
            # LOG.info("Returning %s from cache -> [%s][%s]" % (fileGrp_USE, fileGrp_cache[fileGrp_USE], fileGrp_cache[fileGrp_USE].attrib))
            return self._fileGrp_cache[fileGrp_USE]

        # If not, search for it in the xml tree
        # Get the list of all fileGrps
        el_fileGrp_list = self.get_all_fileGrps()

        # Iterate over all fileGrps in the tree
        for el_fileGrp in el_fileGrp_list:
            # If the USE attribute of the fileGrp matches 
            # with the searched USE attribute
            if el_fileGrp.get('USE') == fileGrp_USE:
                # Add the fileGrp to the cache
                self._fileGrp_cache[el_fileGrp.get('USE')] = el_fileGrp
                # Assign an empty dictionary which will hold the mets_files of the added fileGrp
                self._file_cache[el_fileGrp.get('USE')] = {}
                # LOG.info("FileGrp %s added to the cache" % fileGrp_USE)
                # LOG.info("Cache total elements: %s" % len(fileGrp_cache))
                return el_fileGrp
        
        # Alternative way to get the searched fileGrp element is:
        # el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (fileGrp_USE), NS)

        # Which way is faster should still be tested and decided for

        return None
    
    # REGEX_PREFIX is not considered -> has to be tested!    
    # Returns a list with all mets:file of a specific fileGrp and the length of the list
    def get_all_files_of_a_fileGrp(self, fileGrp_USE=None):
        if fileGrp_USE is None:
            raise ValueError("fileGrp_USE cannot be 'None'!")
        
        el_fileGrp = self.get_a_fileGrp(fileGrp_USE)
        el_mets_file_list = []
        
        if el_fileGrp is None:
            return []
        
        for el_mets_file in el_fileGrp:
            el_mets_file_list.append(el_mets_file)
        
        return el_mets_file_list
        
        '''
        Alternatively, we can also search for a specific mets file 
        according to one of its attribute values:

        for el_mets_file in el_fileGrp:
            print("%s: '%s'" % (el_mets_file.tag, el_mets_file.attrib))
        '''
    
    # REGEX_PREFIX is not considered -> has to be tested!
    # Returns a reference pointer (element) of a (mets:file)
    # from the cache or the xml tree, or None if not found
    '''
    def get_a_file(self, filgeGrp=None, ID=None):
        el_file_list = []
        
        # If the fileGrp of the searched file is known, it is found faster!
        if fileGrp:
            el_file_list, list_len = get_all_files_of_a_fileGrp(fileGrp)

        return None
    '''

    def mm_find_all_files(self, *args, **kwargs):
        """
        Like :py:meth:`find_files` but return a list of all results.

        Equivalent to ``list(self.find_files(...))``
        """
        
        # If only the fileGrp parameter has been passed
        # Return a list with all files of that fileGrp from the cache
        if 'fileGrp' in kwargs and 'ID' not in kwargs and 'pageId' not in kwargs and 'mimetype' not in kwargs and 'url' not in kwargs:
            # print("fileGrp=%s" % kwargs['fileGrp'])
            return self.get_all_files_of_a_fileGrp(kwargs['fileGrp'])

        return list(self.mm_find_files(*args, **kwargs))

    # This is the mimic of the original find_files func without any changes in the parameters signature
    def mm_find_files(self, ID=None, fileGrp=None, pageId=None, mimetype=None, url=None, local_only=False):
        """
        Search ``mets:file`` entries in this METS document and yield results.

        The :py:attr:`ID`, :py:attr:`fileGrp`, :py:attr:`url` and :py:attr:`mimetype`
        parameters can each be either a literal string, or a regular expression if
        the string starts with ``//`` (double slash).

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

        # If there is a fileGrp and mets ID parameters passed
        # search the file only inside its fileGrp
        if ID and fileGrp:
            # Get the element of that fileGrp
            el_fileGrp = self.get_a_fileGrp(fileGrp)
            if el_fileGrp != None and el_fileGrp.get('USE') == fileGrp:
                if ID in self._file_cache[el_fileGrp.get('USE')]:
                    #LOG.info(file_cache[el_fileGrp.get('USE')][ID])
                    #LOG.info("BINGO! %s %s %s" % (fileGrp, ID, file_cache[el_fileGrp.get('USE')][ID]))
                    yield self._file_cache[el_fileGrp.get('USE')][ID]
                else:
                    yield None
                    #LOG.info("Cache miss %s %s" % (fileGrp, ID))

        # If only the ID parameter has been passed
        # Search that ID in the file_cache that holds all files inside the xml tree
        if ID:
            for str_fileGrp in self._file_cache:
                if str_fileGrp in self._file_cache[str_fileGrp]:
                    if ID in self._file_cache[str_fileGrp][ID]: 
                        yield elf._file_cache[str_fileGrp][ID]
                    else:
                        # Not found
                        yield None

        # IF NO MATCHES FOUND WITH ID AND FileGrp in the cache, execute the original old routine

        if pageId:
            if pageId.startswith(REGEX_PREFIX):
                raise Exception("find_files does not support regex search for pageId")
            pageIds, pageId = pageId.split(','), list()
            pageIds_expanded = []
            for pageId_ in pageIds:
                if '..' in pageId_:
                    pageIds_expanded += generate_range(*pageId_.split('..', 2))
            pageIds += pageIds_expanded
            for page in self._tree.getroot().xpath(
                '//mets:div[@TYPE="page"]', namespaces=NS):
                if page.get('ID') in pageIds:
                    pageId.extend(
                        [fptr.get('FILEID') for fptr in page.findall('mets:fptr', NS)]) 

        # Check if the parameters have REGEX_PREFIX before the loop, not inside!
        # Doing this eliminates the call of the startswith function by millions of times
        if ID:
            ID_HAS_REGEX_PREFIX = ID.startswith(REGEX_PREFIX)               # True or False
        if fileGrp:
            fileGrp_HAS_REGEX_PREFIX = fileGrp.startswith(REGEX_PREFIX)     # True or False
        if mimetype:
            mimetype_HAS_REGEX_PREFIX = mimetype.startswith(REGEX_PREFIX)   # True or False
        if url:
            url_HAS_REGEX_PREFIX = url.startswith(REGEX_PREFIX)             # True or False
        
        # Remove the prefix before the loop, not inside.
        # Not an efficiency improvement, but better for reading
        if ID and ID_HAS_REGEX_PREFIX:
            ID_NO_PREFIX = ID[REGEX_PREFIX_LEN:]
        if fileGrp and fileGrp_HAS_REGEX_PREFIX:
            fileGrp_NO_PREFIX = fileGrp[REGEX_PREFIX_LEN:]
        if mimetype and mimetype_HAS_REGEX_PREFIX:
            mimetype_NO_PREFIX = mimetype[REGEX_PREFIX_LEN:]
        if url and url_HAS_REGEX_PREFIX:
            url_NO_PREFIX = url[REGEX_PREFIX_LEN:]   

        # THE ORIGINAL ROUTINE:
        for cand in self._tree.getroot().xpath('//mets:file', namespaces=NS):
            # LOG.info("cand--ID[%s]-USE[%s]-MIMETYPE[%s]" % (cand.get('ID'), cand.getparent().get('USE'), cand.get('MIMETYPE')))
            if ID:
                if ID_HAS_REGEX_PREFIX:
                    if not fullmatch(ID_NO_PREFIX, cand.get('ID')): continue
                else:
                    if not ID == cand.get('ID'): continue

            if pageId is not None and cand.get('ID') not in pageId:
                continue
            
            if fileGrp:
                if fileGrp_HAS_REGEX_PREFIX:
                    if not fullmatch(fileGrp_NO_PREFIX, cand.getparent().get('USE')): continue
                else:
                    if cand.getparent().get('USE') != fileGrp: continue

            if mimetype:
                if mimetype_HAS_REGEX_PREFIX:
                    if not fullmatch(mimetype_NO_PREFIX, cand.get('MIMETYPE') or ''): continue
                else:
                    if cand.get('MIMETYPE') != mimetype: continue

            if url:
                cand_locat = cand.find('mets:FLocat', namespaces=NS)
                if cand_locat is None:
                    continue
                cand_url = cand_locat.get('{%s}href' % NS['xlink'])
                if url_HAS_REGEX_PREFIX:
                    if not fullmatch(url_NO_PREFIX, cand_url): continue
                else:
                    if cand_url != url: continue

            f = OcrdFile(cand, mets=self)
            # If only local resources should be returned and f is not a file path: skip the file
            if local_only and not is_local_filename(f.url):
                # LOG.info("LOCAL ONLY ___AND___ URL not local")
                continue
            # LOG.info("F created!!!")
            yield f

    # This is the mimic of the original add_file func without any changes in the parameters signature
    def mm_add_file(self, fileGrp, mimetype=None, url=None, ID=None, pageId=None, force=False, local_filename=None, ignore=False, **kwargs):
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
            raise ValueError("Invalid syntax for mets:fileGrp/@USE %s (not an xs:ID)" % ID)
        
        # Get the fileGrp element from the cache or the xml tree
        el_fileGrp = self.get_a_fileGrp(fileGrp)
        
        # Alternative non-cached version: 
        # el_fileGrp = self._tree.getroot().find(".//mets:fileGrp[@USE='%s']" % (fileGrp), NS)

        # If the fileGrp is neither in the cache nor in the xml tree
        if el_fileGrp is None:
            # Add the fileGrp to the xml tree
            el_fileGrp = self.add_file_group(fileGrp)
            # Add the fileGrp element to the cache
            self._fileGrp_cache[fileGrp] = el_fileGrp
            self._file_cache[fileGrp] = {}
        
        # Only ID was passed as a parameter previously
        # Since the ID is in form '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper())
        # and the fileGrp being None raises exception, safe to send the fileGrp to the mm_find_files
        mets_file = next(self.mm_find_files(fileGrp=el_fileGrp.get('USE'), ID=ID), None) 
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
            # Add the file to the file_cache
            self._file_cache[el_fileGrp.get('USE')].update({ID : el_mets_file})

        return mets_file

def build_mets(number_of_pages, force=False):
    mets = OcrdMets.empty_mets()
    mets._number_of_pages = number_of_pages
    # for page_id, mimetype in product(page_ids, mimetypes):
    for n in ['%04d' % (n + 1) for n in range(number_of_pages)]:
        _add_file = lambda n, fileGrp, mimetype, ID=None: mets.add_file(
            fileGrp,
            mimetype=mimetype,
            pageId='PHYS_%s' % n,
            ID=ID if ID else '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper()),
            url='%s/%s%s' % (fileGrp, ID if ID else '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper()), MIME_TO_EXT.get(mimetype))
        )
        for grp in GRPS_IMG:
            _add_file(n, grp, 'image/tiff')
            _add_file(n, grp, 'application/vnd.prima.page+xml')
        for grp in GRPS_REG:
            for region_n in range(REGIONS_PER_PAGE):
                _add_file(n, grp, 'image/png', '%s_%s_region%s' % (grp, n, region_n))
    return mets

def build_mets2(number_of_pages, force=False):
    extendedMets = ExtendedOcrdMets.empty_mets()
    extendedMets._number_of_pages = number_of_pages

    # clear cache to avoid bugs when the build_mets2 is called more than once
    # was relevant when the cache was global, it is not now!

    # print("file_cache_len: %s" % len(extendedMets._file_cache))
    # print("fileGrp_cache_len: %s" % len(extendedMets._fileGrp_cache))
    # extendedMets._file_cache.clear()
    # extendedMets._fileGrp_cache.clear()

    # for page_id, mimetype in product(page_ids, mimetypes):
    for n in ['%04d' % (n + 1) for n in range(number_of_pages)]:
        # LOG.info("number_of_pages[%s]" % n)
        _add_file = lambda n, fileGrp, mimetype, ID=None: extendedMets.mm_add_file(
            fileGrp,
            mimetype=mimetype,
            pageId='PHYS_%s' % n,
            ID=ID if ID else '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper()),
            url='%s/%s%s' % (fileGrp, ID if ID else '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper()), MIME_TO_EXT.get(mimetype))
        )
        for grp in GRPS_IMG:
            _add_file(n, grp, 'image/tiff')
            _add_file(n, grp, 'application/vnd.prima.page+xml')
        for grp in GRPS_REG:
            for region_n in range(REGIONS_PER_PAGE):
                _add_file(n, grp, 'image/png', '%s_%s_region%s' % (grp, n, region_n))
    
    return extendedMets

def _create_mets_file(number_of_pages, filename=None):
    if not filename:
        filename = "builded_mets_%s_pages.xml" % number_of_pages
    with open(filename, "wb") as output_file:
        output_file.write(build_mets(number_of_pages).to_xml(xmllint=True))

def _create_mets_file2(number_of_pages, filename=None):
    if not filename:
        filename = "builded_mets_%s_pages2.xml" % number_of_pages
    with open(filename, "wb") as output_file:
        output_file.write(build_mets2(number_of_pages).to_xml(xmllint=True))

if __name__ == '__main__':
    cProfile.run('build_mets(100)', sort="tottime")
    cProfile.run('build_mets2(100)', sort="tottime")

    #print("Print fileGrp_cache:")
    #pprint(fileGrp_cache)
    #print("Print file_cache:")
    #pprint(file_cache)

    '''
    tmp = {"Key1" : { "InKey1" : "Value1"}}
    tmp["Key2"] = {"InKey2" : "Value1"}
    tmp["Key1"].update({"InKey2" : "Value2"})

    pprint(tmp)

    print("InKey1_Value1[%s]" % tmp["Key1"]["InKey1"])
    '''

    #for n in debug_list:
    #    pprint.pprint(n)
	
    # _create_mets_file(100)
    # _create_mets_file2(100)
