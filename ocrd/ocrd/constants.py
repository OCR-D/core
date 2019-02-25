"""
Constants for ocrd.
"""
from pkg_resources import resource_filename

TMP_PREFIX = 'pyocrd-'
DEFAULT_UPLOAD_FOLDER = '/tmp/uploads-pyocrd'
DOWNLOAD_DIR = '/tmp/ocrd-core-downloads'
DEFAULT_REPOSITORY_URL = 'http://localhost:5000/'
BASHLIB_FILENAME = resource_filename(__name__, '../lib.bash')
BACKUP_DIR = '.backup'
