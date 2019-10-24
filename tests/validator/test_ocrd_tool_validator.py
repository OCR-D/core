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
                    "input_file_grp": ["OCR-D-FOO"],
                    "output_file_grp": ["OCR-D-BAR"],
                    "categories": ["Layout analysis"],
                    "steps": ["layout/analysis"]
                }
            }
        }
'''

class TestOcrdToolValidator(TestCase):

    def test_something(self):
        report = OcrdToolValidator.validate(json.loads(skeleton))
        #  print(report.to_xml())
        self.assertEqual(report.is_valid, True)

    def test_file_param_ok(self):
        ocrd_tool = json.loads(skeleton)
        ocrd_tool['tools']['ocrd-xyz']['parameters'] = {"file-param": {"description": "...", "type": "string", "content-type": 'application/rdf+xml'}}
        report = OcrdToolValidator.validate(ocrd_tool)
        self.assertEqual(report.is_valid, True)

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
