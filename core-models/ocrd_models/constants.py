import yaml
from pkg_resources import resource_string, resource_filename

METS_XML_EMPTY = resource_string(__name__, 'model/mets-empty.xml')

OCRD_OAS3_SPEC = yaml.load(resource_string(__name__, 'model/yaml/ocrd_oas3.spec.yml'))
OCRD_TOOL_SCHEMA = yaml.load(resource_string(__name__, 'model/yaml/ocrd_tool.schema.yml'))

BASHLIB_FILENAME = resource_filename(__name__, 'lib.bash')
