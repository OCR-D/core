import json

from jsonschema import Draft4Validator, validators # pylint: disable=import-error

from .report import ValidationReport

# http://python-jsonschema.readthedocs.io/en/latest/faq/
def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for prop, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(prop, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return validators.extend(validator_class, {"properties" : set_defaults})


DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)

#
# -------------------------------------------------
#

class JsonValidator(object):

    @staticmethod
    def validate_json(obj, schema):
        if isinstance(obj, str):
            obj = json.loads(obj)
        return JsonValidator(schema).validate(obj)

    def __init__(self, schema, validator_class=Draft4Validator):
        self.validator = validator_class(schema)

    def validate(self, obj):
        report = ValidationReport()
        if not self.validator.is_valid(obj):
            for v in self.validator.iter_errors(obj):
                report.add_error("[%s] %s" % ('.'.join(str(vv) for vv in v.path), v.message))
        return report
