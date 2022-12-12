"""
Constants for ocrd.
"""
from ocrd_utils.package_resources import resource_filename

__all__ = [
    'TMP_PREFIX',
    'DEFAULT_UPLOAD_FOLDER',
    'DOWNLOAD_DIR',
    'DEFAULT_REPOSITORY_URL',
    'BASHLIB_FILENAME',
    'RESOURCE_LIST_FILENAME',
    'BACKUP_DIR',
    'RESOURCE_USER_LIST_COMMENT',
]

TMP_PREFIX = 'ocrd-core-'
DEFAULT_UPLOAD_FOLDER = '/tmp/uploads-ocrd-core'
DOWNLOAD_DIR = '/tmp/ocrd-core-downloads'
DEFAULT_REPOSITORY_URL = 'http://localhost:5000/'
BASHLIB_FILENAME = resource_filename(__name__, 'lib.bash')
RESOURCE_LIST_FILENAME = resource_filename(__name__, 'resource_list.yml')
RESOURCE_USER_LIST_COMMENT = "# OCR-D private resource list (consider sending a PR with your own resources to OCR-D/core)"
BACKUP_DIR = '.backup'
