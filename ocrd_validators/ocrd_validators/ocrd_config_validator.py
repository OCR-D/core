"""
Validating $HOME/.config/ocrd.yml
"""
from .constants import CONFIG_SCHEMA
from .json_validator import JsonValidator

#
# -------------------------------------------------
#

class OcrdConfigValidator(JsonValidator):
    """
    JsonValidator validating against the ``ocrd-tool.json`` schema.
    """

    @staticmethod
    def validate(obj, schema=CONFIG_SCHEMA):
        """
        Validate against ``ocrd_config.schema.yml`` schema.
        """
        return JsonValidator.validate(obj, schema)

