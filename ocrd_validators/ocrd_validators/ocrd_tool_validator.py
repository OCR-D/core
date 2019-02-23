from .constants import OCRD_TOOL_SCHEMA
from .json_validator import JsonValidator

#
# -------------------------------------------------
#

class OcrdToolValidator(JsonValidator):

    @staticmethod
    def validate(obj, schema=OCRD_TOOL_SCHEMA):
        return JsonValidator.validate(obj, schema)
