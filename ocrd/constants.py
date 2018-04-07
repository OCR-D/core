import os
import tesserocr

NAMESPACES = {
    'mets': "http://www.loc.gov/METS/",
    'mods': "http://www.loc.gov/mods/v3",
    'xlink': "http://www.w3.org/1999/xlink",
    'page': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15",
    'xsl': 'http://www.w3.org/1999/XSL/Transform#',
}

PAGE_XML_EMPTY = '''<?xml version="1.0" encoding="UTF-8"?>
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd">
        <Page>
        </Page>
</PcGts>
'''

MIMETYPE_PAGE = 'text/page+xml'

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

TESSDATA_PREFIX = os.environ['TESSDATA_PREFIX'] if 'TESSDATA_PREFIX' in os.environ else tesserocr.get_languages()[0]
