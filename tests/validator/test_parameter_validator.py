from ocrd_validators import ParameterValidator
from tests.base import TestCase, main


class TestParameterValidator(TestCase):

    def test_extraneous(self):
        validator = ParameterValidator({"parameters": {}})
        obj = {"foo": 42}
        report = validator.validate(obj)
        self.assertFalse(report.is_valid)
        self.assertIn("Additional properties are not allowed ('foo' was unexpected)", report.errors[0])

    def test_missing_required(self):
        validator = ParameterValidator({
            "parameters": {
                "i-am-required": {
                    "type": "number",
                    "required": True
                },
            }
        })
        obj = {}
        report = validator.validate(obj)
        self.assertFalse(report.is_valid)
        self.assertIn('is a required property', report.errors[0])

    def test_default_assignment(self):
        validator = ParameterValidator({
            "parameters": {
                "num-param": {
                    "type": "number",
                    "default": 1
                },
                "baz": {
                    "type": "string",
                    "required": True,
                },
                'foo': {
                    "required": False
                }
            }
        })
        obj = {'baz': '23'}
        report = validator.validate(obj)
        self.assertTrue(report.is_valid)
        self.assertEqual(obj, {'baz': '23', "num-param": 1})

def test_min_max():
    validator = ParameterValidator({
        "parameters": {
            "num-param": {
                "type": "number",
                "exclusiveMinimum": 10,
                "maximum": 100,
                "multipleOf": 2
            }
        }
    })
    report = validator.validate({'num-param': 23})
    assert not report.is_valid
    assert 'is not a multiple of 2' in report.errors[0]
    report = validator.validate({'num-param': 102})
    assert not report.is_valid
    assert 'is greater than the maximum of' in report.errors[0]
    report = validator.validate({'num-param': 8})
    assert not report.is_valid
    assert 'is less than or equal to the minimum of' in report.errors[0]



if __name__ == '__main__':
    main(__name__)
