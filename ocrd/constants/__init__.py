import yaml
from pkg_resources import resource_string, resource_filename, get_distribution

from ocrd.constants.xml import *  # pylint: disable=wildcard-import

VERSION = get_distribution('ocrd').version

TMP_PREFIX = 'pyocrd-'
TMP_BAGIT_PREFIX = 'ocrd-bagit-'

MIMETYPE_PAGE = 'application/vnd.prima.page+xml'

DEFAULT_UPLOAD_FOLDER = '/tmp/uploads-pyocrd'
DEFAULT_REPOSITORY_URL = 'http://localhost:5000/'

FILE_GROUP_PREFIX = 'OCR-D-'
FILE_GROUP_CATEGORIES = ['IMG', 'SEG', 'OCR', 'COR', 'GT']
IDENTIFIER_PRIORITY = ['purl', 'urn', 'doi', 'url']

EXT_TO_MIME = {
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.jpeg': 'image/jpg',
    '.xml': MIMETYPE_PAGE
}


METS_XML_EMPTY = resource_string(__name__, '../model/mets-empty.xml')
OCRD_TOOL_SCHEMA = yaml.load(resource_string(__name__, '../model/yaml/ocrd_tool.schema.yml'))
OCRD_BAGIT_PROFILE_URL = 'https://ocr-d.github.io/bagit-profile.json'
OCRD_BAGIT_PROFILE = yaml.load(resource_string(__name__, '../model/yaml/bagit-profile.yml'))

BASHLIB_FILENAME = resource_filename(__name__, '../lib.bash')

BACKUP_DIR = '.backup'
BAGIT_TXT = 'BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8'
