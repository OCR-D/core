import yaml
from pkg_resources import resource_string

VERSION = '0.2.0'

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

DEFAULT_CACHE_FOLDER = '/tmp/cache-pyocrd'

FILE_GROUP_PREFIX = 'OCR-D-'
FILE_GROUP_CATEGORIES = ['IMG', 'SEG', 'OCR', 'COR']
IDENTIFIER_PRIORITY = ['purl', 'urn', 'doi', 'url']

TAG_METS_FILE = '{%s}file' % NAMESPACES['mets']
TAG_METS_FLOCAT = '{%s}FLocat' % NAMESPACES['mets']
TAG_METS_FILEGRP = '{%s}fileGrp' % NAMESPACES['mets']
TAG_PAGE_COORDS = '{%s}Coords' % NAMESPACES['page']
TAG_PAGE_READINGORDER = '{%s}ReadingOrder' % NAMESPACES['page']
TAG_PAGE_REGIONREFINDEXED = '{%s}RegionRefIndexed' % NAMESPACES['page']
TAG_PAGE_TEXTLINE = '{%s}TextLine' % NAMESPACES['page']
TAG_PAGE_TEXTEQUIV = '{%s}TextEquiv' % NAMESPACES['page']
TAG_PAGE_TEXTREGION = '{%s}TextRegion' % NAMESPACES['page']

METS_XML_EMPTY = '''<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:mets="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="info:lc/xmlns/premis-v2 http://www.loc.gov/standards/premis/v2/premis-v2-0.xsd http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-6.xsd http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/version17/mets.v1-7.xsd http://www.loc.gov/mix/v10 http://www.loc.gov/standards/mix/mix10/mix10.xsd">
  <mets:metsHdr CREATEDATE="2017-11-30T16:18:26">
    <mets:agent OTHERTYPE="SOFTWARE" ROLE="CREATOR" TYPE="OTHER">
      <mets:name>DFG-Koordinierungsprojekt zur Weiterentwicklung von Verfahren der Optical Character Recognition (OCR-D)</mets:name>
      <mets:note>OCR-D</mets:note>
    </mets:agent>
  </mets:metsHdr>
  <mets:dmdSec ID="DMDLOG_0001">
    <mets:mdWrap MDTYPE="MODS">
      <mets:xmlData>
        <mods:mods xmlns:mods="http://www.loc.gov/mods/v3">
        </mods:mods>
      </mets:xmlData>
    </mets:mdWrap>
  </mets:dmdSec>
  <mets:amdSec ID="AMD">
  </mets:amdSec>
  <mets:fileSec>
  </mets:fileSec>
</mets:mets>
'''

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
