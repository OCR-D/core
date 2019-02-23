"""
Validating ``ocrd-tool.json``.

See `specs <https://ocr-d.github.io/ocrd_tool>`_.
"""
from .constants import OCRD_TOOL_SCHEMA
from .json_validator import JsonValidator

#
# -------------------------------------------------
#

class OcrdToolValidator(JsonValidator):
    """
    JsonValidator validating against the ``ocrd-tool.json`` schema.
    """

    @staticmethod
    def validate(obj, schema=OCRD_TOOL_SCHEMA):
        """
        Validate against ``ocrd-tool.json`` schema.
        """
        return JsonValidator.validate(obj, schema)
