import json
from test.base import TestCase, assets, main

from ocrd.resolver import Resolver
from ocrd.validator import (
    ValidationReport,
    WorkspaceValidator,
    ParameterValidator,
    OcrdToolValidator
)

class TestValidationReport(TestCase):

    def setUp(self):
        self.resolver = Resolver()

    def runTest(self):
        report = ValidationReport()
        self.assertEqual(str(report), 'OK')
        report.add_warning('This is not good')
        report.add_error('This is bad')
        self.assertEqual(report.to_xml(), '''\
<report valid="false">
  <warning>This is not good</warning>
  <error>This is bad</error>
</report>''')

class TestWorkspaceValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()

    def runTest(self):
        report = WorkspaceValidator.validate_url(self.resolver, assets.url_of('SBB0000F29300010000/mets_one_file.xml'))
        print(report.to_xml())

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
