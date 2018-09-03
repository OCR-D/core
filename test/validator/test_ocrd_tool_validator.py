from test.base import TestCase, main # pylint: disable=import-error,no-name-in-module
import json
from ocrd.validator import OcrdToolValidator

class TestOcrdToolValidator(TestCase):

    def runTest(self):
        report = OcrdToolValidator.validate_json(json.loads('''
        {
            "git_url": "https://github.com/ocr-d/foo",
            "version": "0.0.1",
            "tools": {
                "ocrd-xyz": {
                    "executable": "ocrd-xyz",
                    "description": "bars all the foos",
                    "categories": ["Layout analysis"],
                    "steps": ["layout/analysis"]
                }
            }
        }
        '''))
        print(report.to_xml())

if __name__ == '__main__':
    main()
