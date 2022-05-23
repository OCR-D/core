"""
Validating ``resource_list.yml``.

See `specs <https://ocr-d.de/en/spec/cli#processor-resources>`_.
"""
from .constants import RESOURCE_LIST_SCHEMA
from .json_validator import JsonValidator, DefaultValidatingDraft6Validator

#
# -------------------------------------------------
#

class OcrdResourceListValidator(JsonValidator):
    """
    JsonValidator validating against the ``resource_list.yml`` schema.
    """

    @staticmethod
    def validate(obj, schema=RESOURCE_LIST_SCHEMA):
        """
        Validate against ``resource_list.schema.yml`` schema.
        """
        return JsonValidator(schema, validator_class=DefaultValidatingDraft6Validator)._validate(obj)

