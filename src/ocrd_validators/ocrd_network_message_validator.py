"""
Validating ocrd-network messages
"""
from .constants import MESSAGE_SCHEMA_PROCESSING, MESSAGE_SCHEMA_RESULT
from .json_validator import JsonValidator


class OcrdNetworkMessageValidator(JsonValidator):
    """
    JsonValidator validating against the ocrd network message schemas
    """

    @staticmethod
    def validate_message_processing(obj):
        return JsonValidator.validate(obj, schema=MESSAGE_SCHEMA_PROCESSING)

    @staticmethod
    def validate_message_result(obj):
        return JsonValidator.validate(obj, schema=MESSAGE_SCHEMA_RESULT)
