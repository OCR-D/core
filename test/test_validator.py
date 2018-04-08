import json
from ocrd.resolver import Resolver
from ocrd.validator import ValidationReport, WorkspaceValidator, OcrdToolValidator
from test.base import TestCase, assets, main
METS_HEROLD_SMALL = assets.url_of('SBB0000F29300010000/mets_one_file.xml')

class TestValidationReport(TestCase):

    def setUp(self):
        self.resolver = Resolver(cache_enabled=True)

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
        self.resolver = Resolver(cache_enabled=True)

    def runTest(self):
        report = WorkspaceValidator.validate_url(self.resolver, METS_HEROLD_SMALL)
        print(report.to_xml())

class TestOcrdToolValidator(TestCase):

    def runTest(self):
        report = OcrdToolValidator.validate_json(json.loads('''
        {
            "git_url": "https://github.com/ocr-d/foo",
            "tools": [
                {
                    "xxx binary": "foo",
                    "description": "bars all the foos",
                    "category": "preprocess"
                }
            ]
        }
        '''))
        print(report.to_xml())

if __name__ == '__main__':
    main()
