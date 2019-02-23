"""
Constants for ocrd_utils.
"""
from pkg_resources import get_distribution

__all__ = [
    'VERSION',
    'MIMETYPE_PAGE',
    'EXT_TO_MIME',
]

VERSION = get_distribution('ocrd_utils').version

MIMETYPE_PAGE = 'application/vnd.prima.page+xml'

EXT_TO_MIME = {
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.jpeg': 'image/jpg',
    '.xml': MIMETYPE_PAGE
}
