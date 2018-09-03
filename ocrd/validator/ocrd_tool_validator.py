from ..constants import OCRD_TOOL_SCHEMA
from .json_validator import JsonValidator

#
# -------------------------------------------------
#

class OcrdToolValidator(JsonValidator):

    @staticmethod
    def validate_json(obj, schema=OCRD_TOOL_SCHEMA):
        return JsonValidator.validate_json(obj, schema)
