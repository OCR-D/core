"""
Constants for ocrd_utils.
"""
from .introspect import dist_version
from re import compile as regex_compile

__all__ = [
    'EXT_TO_MIME',
    'LOG_FORMAT',
    'LOG_TIMEFMT',
    'MIMETYPE_PAGE',
    'MIME_TO_EXT',
    'MIME_TO_PIL',
    'PIL_TO_MIME',
    'REGEX_PREFIX',
    'REGEX_FILE_ID',
    'RESOURCE_LOCATIONS',
    'VERSION',
]

VERSION = dist_version('ocrd')

MIMETYPE_PAGE = 'application/vnd.prima.page+xml'

EXT_TO_MIME = {
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.xml': MIMETYPE_PAGE,
    '.jp2': 'image/jp2',
    '.pdf': 'application/pdf',
    '.ps': 'application/postscript',
    '.eps': 'application/postscript',
    '.xps': 'application/oxps',
    '.ppm': 'image/x-portable-pixmap',
    '.pnm': 'image/x-portable-anymap',
    '.pbm': 'image/x-portable-bitmap',
    '.tar.gz': 'application/gzip',
    '.tar.xz': 'application/x-xz',
    '.tgz': 'application/gzip',
    '.txz': 'application/x-xz',
    '.txt': 'text/plain',
    '.xsl': 'text/xsl',
    '.zip': 'application/zip',
}

MIME_TO_EXT = {
    'image/tiff': '.tif',
    'image/tif': '.tif',
    'image/png': '.png',
    'image/jpg': '.jpg',
    'image/jpeg': '.jpg',
    MIMETYPE_PAGE: '.xml',
    'application/alto+xml': '.xml',
    'image/jp2': '.jp2',
    'application/pdf': '.pdf',
    'application/postscript': '.ps',
    'application/oxps': '.xps',
    'application/x-hdf': '.h5',
    'application/x-hdf;subtype=bag': '.h5',
    'application/vnd.pytorch': '.pth',
    'image/x-portable-pixmap': '.ppm',
    'image/x-portable-anymap': '.pnm',
    'image/x-portable-bitmap': '.pbm',
    'text/plain': '.txt',
    'text/xsl': '.xsl',
    'text/xml': '.xml',
    'application/zip': '.zip',
    'application/x-xz': '.tar.xz',
    'application/gzip': '.tar.gz',
}

#
# Translate between what PIL expects as ``format`` and IANA media types.
#
PIL_TO_MIME = {
    'BMP':  'image/bmp',
    'EPS':  'application/postscript',
    'GIF':  'image/gif',
    'JPEG': 'image/jpeg',
    'JP2':  'image/jp2',
    'PNG':  'image/png',
    'PPM':  'image/x-portable-pixmap',
    'TIFF': 'image/tiff',
}

MIME_TO_PIL = {
    'image/bmp': 'BMP',
    'application/postscript': 'EPS',
    'image/gif': 'GIF',
    'image/jpeg': 'JPEG',
    'image/jp2': 'JP2',
    'image/png': 'PNG',
    'image/x-portable-pixmap': 'PPM',
    'image/tiff': 'TIFF',
}

# Prefix to denote query is regular expression not fixed string
REGEX_PREFIX = '//'

# Regex for valid mets:file/@ID
REGEX_FILE_ID = regex_compile(r'^[a-zA-Z_][\w.-]*$')

# Log level format implementing https://ocr-d.de/en/spec/cli#logging
LOG_FORMAT = r'%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(message)s'
LOG_TIMEFMT = r'%H:%M:%S'

RESOURCE_LOCATIONS = ['data', 'cwd', 'system', 'module']

DEFAULT_METS_BASENAME = 'mets.xml'


#    2581 ▁ LOWER ONE EIGHTH BLOCK
#    2582 ▂ LOWER ONE QUARTER BLOCK
#    2583 ▃ LOWER THREE EIGHTHS BLOCK
#    2584 ▄ LOWER HALF BLOCK
#    2585 ▅ LOWER FIVE EIGHTHS BLOCK
#    2586 ▆ LOWER THREE QUARTERS BLOCK
#    2587 ▇ LOWER SEVEN EIGHTHS BLOCK
#    2588 █ FULL BLOCK
SPARKLINE_CHARS = [
    ' ',
    '\u2581',
    '\u2582',
    '\u2583',
    '\u2584',
    '\u2585',
    '\u2586',
    '\u2587',
    '\u2588',
]
