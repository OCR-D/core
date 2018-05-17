from test.base import TestCase, main
from ocrd.validator import ParameterValidator

class TestParameterValidator(TestCase):

    def setUp(self):
        self.ocrd_tool = {
            "parameters": {
                "num-param": {"type": "number", "default": 1}
            }
        }

    def runTest(self):
        validator = ParameterValidator(self.ocrd_tool)
        obj = {}
        validator.validate(obj)
        self.assertEqual(obj, {"num-param": 1})


if __name__ == '__main__':
    main()
