"""
Validating ``ocrd-tool.json``.

See `specs <https://ocr-d.de/en/spec/ocrd_tool>`_.
"""
from .constants import OCRD_TOOL_SCHEMA
from .json_validator import DefaultValidatingDraft20199Validator, JsonValidator

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
        return OcrdToolValidator(schema)._validate(obj) # pylint: disable=protected-access

    def __init__(self, schema, validator_class=...):
        super().__init__(schema, DefaultValidatingDraft20199Validator)
