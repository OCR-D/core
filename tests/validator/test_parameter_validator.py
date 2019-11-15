from tests.base import TestCase, main
from ocrd_validators import ParameterValidator

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


if __name__ == '__main__':
    main()
