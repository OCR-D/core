import yaml
from pkg_resources import resource_string, resource_filename

VERSION = '0.8.6'

TMP_PREFIX = 'pyocrd-'

NAMESPACES = {
    'mets': "http://www.loc.gov/METS/",
    'mods': "http://www.loc.gov/mods/v3",
    'xlink': "http://www.w3.org/1999/xlink",
    'page': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15",
    'xsl': 'http://www.w3.org/1999/XSL/Transform#',
}

MIMETYPE_PAGE = 'application/vnd.prima.page+xml'

DEFAULT_UPLOAD_FOLDER = '/tmp/uploads-pyocrd'
DEFAULT_REPOSITORY_URL = 'http://localhost:5000/'

FILE_GROUP_PREFIX = 'OCR-D-'
FILE_GROUP_CATEGORIES = ['IMG', 'SEG', 'OCR', 'COR', 'GT']
IDENTIFIER_PRIORITY = ['purl', 'urn', 'doi', 'url']

TAG_METS_FILE = '{%s}file' % NAMESPACES['mets']
TAG_METS_FLOCAT = '{%s}FLocat' % NAMESPACES['mets']
TAG_METS_FILEGRP = '{%s}fileGrp' % NAMESPACES['mets']

TAG_MODS_IDENTIFIER = '{%s}identifier' % NAMESPACES['mods']

TAG_PAGE_COORDS = '{%s}Coords' % NAMESPACES['page']
TAG_PAGE_READINGORDER = '{%s}ReadingOrder' % NAMESPACES['page']
TAG_PAGE_REGIONREFINDEXED = '{%s}RegionRefIndexed' % NAMESPACES['page']
TAG_PAGE_TEXTLINE = '{%s}TextLine' % NAMESPACES['page']
TAG_PAGE_TEXTEQUIV = '{%s}TextEquiv' % NAMESPACES['page']
TAG_PAGE_TEXTREGION = '{%s}TextRegion' % NAMESPACES['page']

METS_XML_EMPTY = resource_string(__name__, 'model/mets-empty.xml')

EXT_TO_MIME = {
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.jpeg': 'image/jpg',
    '.xml': MIMETYPE_PAGE
}


OCRD_OAS3_SPEC = yaml.load(resource_string(__name__, 'model/yaml/ocrd_oas3.spec.yml'))
OCRD_TOOL_SCHEMA = yaml.load(resource_string(__name__, 'model/yaml/ocrd_tool.schema.yml'))

BASHLIB_FILENAME = resource_filename(__name__, 'lib.bash')
