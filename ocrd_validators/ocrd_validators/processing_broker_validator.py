"""
Validating configuration file for the Processing-Broker
"""
from .json_validator import JsonValidator
import yaml
from ocrd_utils.package_resources import resource_string


# TODO: provide a link somewhere in this file as it is done in ocrd_tool.schema.yml but best with a
# working link. Currently it is here:
# https://github.com/OCR-D/spec/pull/222/files#diff-a71bf71cbc7d9ce94fded977f7544aba4df9e7bdb8fc0cf1014e14eb67a9b273
# But that is a PR not merged yet
class ProcessingBrokerValidator(JsonValidator):
    """
    JsonValidator validating against the schema for the Processing Broker
    """

    @staticmethod
    def validate(obj):
        """
        Validate against schema for Processing-Broker
        """
        schema = yaml.safe_load(resource_string(__name__, 'config.schema.yml'))
        return JsonValidator.validate(obj, schema)
