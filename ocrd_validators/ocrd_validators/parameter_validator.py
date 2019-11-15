"""
Validate parameters against ocrd-tool.json.
"""
from .json_validator import JsonValidator, DefaultValidatingDraft4Validator

#
# -------------------------------------------------
#

class ParameterValidator(JsonValidator):
    """
    JsonValidator validating parametersagains ocrd-tool.json.
    """

    def validate(self, *args, **kwargs): # pylint: disable=arguments-differ
        """
        Validate a parameter dict against a parameter schema from an ocrd-tool.json

        Args:
            obj (dict):
            schema (dict):
        """
        return super(ParameterValidator, self)._validate(*args, **kwargs)

    def __init__(self, ocrd_tool):
        """
        Construct a ParameterValidator.

        Arguments:
            ocrd_tool (dict): Parsed ``ocrd-tool.json``.
        """
        required = []
        if ocrd_tool is None:
            ocrd_tool = {}
        if 'parameters' not in ocrd_tool:
            ocrd_tool['parameters'] = {}
        p = ocrd_tool['parameters']
        for n in p:
            if 'required' in p[n]:
                if p[n]['required']:
                    required.append(n)
                del(p[n]['required'])
        super(ParameterValidator, self).__init__({
            "type": "object",
            "required": required,
            "additionalProperties": False,
            "properties": p
        }, DefaultValidatingDraft4Validator)
