import yaml
from pkg_resources import resource_string, resource_filename

METS_XML_EMPTY = resource_string(__name__, 'model/mets-empty.xml')

OCRD_OAS3_SPEC = yaml.load(resource_string(__name__, 'model/yaml/ocrd_oas3.spec.yml'))
OCRD_TOOL_SCHEMA = yaml.load(resource_string(__name__, 'model/yaml/ocrd_tool.schema.yml'))

BASHLIB_FILENAME = resource_filename(__name__, 'lib.bash')

TMP_BAGIT_PREFIX = 'ocrd-bagit-'
OCRD_BAGIT_PROFILE_URL = 'https://ocr-d.github.io/bagit-profile.json'
OCRD_BAGIT_PROFILE = yaml.load(resource_string(__name__, 'model/yaml/bagit-profile.yml'))
BAGIT_TXT = 'BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8'
