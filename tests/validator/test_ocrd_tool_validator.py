import json

from tests.base import TestCase, main # pylint: disable=import-error,no-name-in-module

from ocrd_validators import OcrdToolValidator

skeleton = '''
        {
            "git_url": "https://github.com/ocr-d/foo",
            "version": "0.0.1",
            "tools": {
                "ocrd-xyz": {
                    "executable": "ocrd-xyz",
                    "description": "bars all the foos",
                    "input_file_grp_cardinality": 1,
                    "output_file_grp_cardinality": 1,
                    "categories": ["Layout analysis"],
                    "steps": ["layout/analysis"]
                }
            }
        }
'''

class TestOcrdToolValidator(TestCase):

    def setUp(self):
        super().setUp()
        self.ocrd_tool = json.loads(skeleton)

    def test_smoke(self):
        report = OcrdToolValidator.validate(self.ocrd_tool)
        self.assertTrue(report.is_valid, str(report.errors))

    def test_additional_props(self):
        self.ocrd_tool['not-allowed'] = 'YUP'
        report = OcrdToolValidator.validate(self.ocrd_tool)
        self.assertFalse(report.is_valid)
        self.assertIn("Additional properties are not allowed ('not-allowed' was unexpected)", report.errors[0])

    def test_additional_props_in_tool(self):
        # XXX 'parameter' is the wrong key, should be 'parameters'
        self.ocrd_tool['tools']['ocrd-xyz']['parameter'] = {}
        report = OcrdToolValidator.validate(self.ocrd_tool)
        self.assertFalse(report.is_valid)
        self.assertIn("Additional properties are not allowed ('parameter' was unexpected)", report.errors[0])

    def test_file_param_ok(self):
        ocrd_tool = json.loads(skeleton)
        ocrd_tool['tools']['ocrd-xyz']['parameters'] = {"file-param": {"description": "...", "type": "string", "content-type": 'application/rdf+xml'}}
        report = OcrdToolValidator.validate(ocrd_tool)
        self.assertTrue(report.is_valid, str(report.errors))

    # Not restricted anymore since spec 3.3.0
    #  def test_file_param_bad_content_types(self):
    #      bad_and_why = [
    #              [2, 'Number not string'],
    #              ['foo', 'No subtype'],
    #              ['foo/bar~300', 'Invalid char in subtype'],
    #              ['foo/bar 300', 'Invalid char in subtype'],
    #      ]
    #      for case in bad_and_why:
    #          ocrd_tool = json.loads(skeleton)
    #          ocrd_tool['tools']['ocrd-xyz']['parameters'] = {"file-param": {"description": "...", "type": "string", "content-type": case[0]}}
    #          report = OcrdToolValidator.validate(ocrd_tool)
    #          print('# %s: %s' % (case[0], case[1]))
    #          self.assertEqual(report.is_valid, False, case[1])

if __name__ == '__main__':
    main()
