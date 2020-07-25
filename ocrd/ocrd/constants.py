"""
Constants for ocrd.
"""
from pkg_resources import resource_filename

__all__ = [
    'TMP_PREFIX',
    'DEFAULT_UPLOAD_FOLDER',
    'DOWNLOAD_DIR',
    'DEFAULT_REPOSITORY_URL',
    'BASHLIB_FILENAME',
    'BACKUP_DIR',
]

TMP_PREFIX = 'ocrd-core-'
DEFAULT_UPLOAD_FOLDER = '/tmp/uploads-ocrd-core'
DOWNLOAD_DIR = '/tmp/ocrd-core-downloads'
DEFAULT_REPOSITORY_URL = 'http://localhost:5000/'
BASHLIB_FILENAME = resource_filename(__name__, 'lib.bash')
BACKUP_DIR = '.backup'
