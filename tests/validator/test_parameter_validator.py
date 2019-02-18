from tests.base import TestCase, main
from ocrd_validators import ParameterValidator

class TestParameterValidator(TestCase):

    def test_default_assignment(self):
        validator = ParameterValidator({"parameters": {"num-param": {"type": "number", "default": 1}}})
        obj = {}
        validator.validate(obj)
        self.assertEqual(obj, {"num-param": 1})


if __name__ == '__main__':
    main()
