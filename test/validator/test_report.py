from test.base import TestCase, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd_models.validator import ValidationReport

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

if __name__ == '__main__':
    main()
