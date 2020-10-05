"""
Constants for ocrd_utils.
"""
from pkg_resources import get_distribution
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
    'VERSION',
]

VERSION = get_distribution('ocrd_utils').version

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
    '.txt': 'text/plain',
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
    'image/x-portable-pixmap': '.ppm',
    'image/x-portable-anymap': '.pnm',
    'image/x-portable-bitmap': '.pbm',
    'text/plain': '.txt',
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
