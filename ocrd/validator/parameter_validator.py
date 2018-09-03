from ocrd.validator.json_validator import JsonValidator, DefaultValidatingDraft4Validator

#
# -------------------------------------------------
#

class ParameterValidator(JsonValidator):

    def __init__(self, ocrd_tool):
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
            "properties": p
        }, DefaultValidatingDraft4Validator)
