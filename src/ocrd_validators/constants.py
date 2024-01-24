"""
Constants for ocrd_validators.
"""
import yaml
from ocrd_utils import resource_string, resource_filename

__all__ = [
    'PROCESSING_SERVER_CONFIG_SCHEMA',
    'MESSAGE_SCHEMA_PROCESSING',
    'MESSAGE_SCHEMA_RESULT',
    'OCRD_TOOL_SCHEMA',
    'RESOURCE_LIST_SCHEMA',
    'OCRD_BAGIT_PROFILE',
    'BAGIT_TXT',
    'FILE_GROUP_PREFIX',
    'FILE_GROUP_CATEGORIES',
    'TMP_BAGIT_PREFIX',
    'OCRD_BAGIT_PROFILE_URL',
    'XSD_METS_URL',
    'XSD_PAGE_URL',
    'XSD_PATHS',
]

PROCESSING_SERVER_CONFIG_SCHEMA = yaml.safe_load(resource_string(__package__, 'processing_server_config.schema.yml'))
MESSAGE_SCHEMA_PROCESSING = yaml.safe_load(resource_string(__package__, 'message_processing.schema.yml'))
MESSAGE_SCHEMA_RESULT = yaml.safe_load(resource_string(__package__, 'message_result.schema.yml'))
OCRD_TOOL_SCHEMA = yaml.safe_load(resource_string(__package__, 'ocrd_tool.schema.yml'))
RESOURCE_LIST_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'patternProperties': {
        '^ocrd-.*': OCRD_TOOL_SCHEMA['properties']['tools']['patternProperties']['ocrd-.*']['properties']['resources']
    }
}
OCRD_BAGIT_PROFILE = yaml.safe_load(resource_string(__package__, 'bagit-profile.yml'))

BAGIT_TXT = 'BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8'
FILE_GROUP_PREFIX = 'OCR-D-'
FILE_GROUP_CATEGORIES = ['IMG', 'PRE', 'SEG', 'OCR', 'COR', 'GT']
TMP_BAGIT_PREFIX = 'ocrd-bagit-'
OCRD_BAGIT_PROFILE_URL = 'https://ocr-d.github.io/bagit-profile.json'
XSD_METS_URL = 'https://www.loc.gov/standards/mets/mets.xsd'
XSD_PAGE_URL = 'http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd'
XSD_PATHS = {}
XSD_PATHS[XSD_METS_URL] = resource_filename(__package__, 'mets.xsd')
XSD_PATHS[XSD_PAGE_URL] = resource_filename(__package__, 'page.xsd')
