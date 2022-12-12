"""
Constants for ocrd_utils.
"""
from re import compile as regex_compile
from os import environ
from os.path import join, expanduser

from ocrd_utils.package_resources import get_distribution

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
    'XDG_CONFIG_HOME',
    'XDG_DATA_HOME',
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
    '.xsl': 'text/xsl',
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

# See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
if 'HOME' in environ and environ['HOME'] != expanduser('~'):
    HOME = environ['HOME']
else:
    HOME = expanduser('~')
XDG_DATA_HOME = environ['XDG_DATA_HOME'] if 'XDG_DATA_HOME' in environ else join(HOME, '.local', 'share')
XDG_CONFIG_HOME = environ['XDG_CONFIG_HOME'] if 'XDG_CONFIG_HOME' in environ else join(HOME, '.config')

RESOURCE_LOCATIONS = ['data', 'cwd', 'system', 'module']
