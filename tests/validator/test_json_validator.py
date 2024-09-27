from tests.base import TestCase, main
from ocrd_validators.json_validator import JsonValidator, DefaultValidatingDraft20199Validator

class TestParameterValidator(TestCase):

    def setUp(self):
        self.schema = {
            'required': ['bar'],
            'properties': {
                'foo': {'default': 3000},
                'bar': {},
                'quux': {
                    'required': ['foo'],
                    'type': 'object'
                }
            }
        }
        self.defaults_validator = JsonValidator(self.schema, DefaultValidatingDraft20199Validator)
        super().setUp()

    def test_validate_string(self):
        report = JsonValidator.validate('{}', {})
        self.assertTrue(report.is_valid, str(report.to_xml()))

    def test_defaults_set(self):
        obj = {'bar': 2000}
        report = self.defaults_validator._validate(obj)
        self.assertTrue(report.is_valid, str(report.to_xml()))
        self.assertEqual(obj, {'foo': 3000, 'bar': 2000})

    def test_properr(self):
        obj = {'bar': 100, 'quux': {}}
        report = self.defaults_validator._validate(obj)
        self.assertFalse(report.is_valid, str(report.to_xml()))
        self.assertEqual(len(report.errors), 1)


if __name__ == '__main__':
    main()
