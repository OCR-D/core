"""
Validating ``resource_list.yml``.

See `specs <https://ocr-d.de/en/spec/cli#processor-resources>`_.
"""
from .constants import RESOURCE_LIST_SCHEMA
from .json_validator import DefaultValidatingDraft20199Validator, JsonValidator

#
# -------------------------------------------------
#

class OcrdResourceListValidator(JsonValidator):
    """
    JsonValidator validating against the ``resource_list.yml`` schema.
    """

    @staticmethod
    def validate(obj, schema=None):
        """
        Validate against ``resource_list.schema.yml`` schema.
        """
        if schema is None:
            schema = RESOURCE_LIST_SCHEMA
        return JsonValidator(schema, validator_class=DefaultValidatingDraft20199Validator)._validate(obj) # pylint: disable=protected-access
