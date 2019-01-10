from tests.base import TestCase, main # pylint: disable=import-error,no-name-in-module
from ocrd_validators import ValidationReport

class TestValidationReport(TestCase):

    def test_toxml(self):
        report = ValidationReport()
        self.assertEqual(str(report), 'OK')
        report.add_warning('This is not good')
        report.add_error('This is bad')
        self.assertEqual(report.to_xml(), '''\
<report valid="false">
  <warning>This is not good</warning>
  <error>This is bad</error>
</report>''')

    def test_merge(self):
        report = ValidationReport()
        other_report = ValidationReport()
        report.add_error("foo")
        other_report.add_error("bar")
        other_report.add_warning("foo")
        report.merge_report(other_report)
        self.assertEqual(report.errors, ['foo', 'bar'])
        self.assertEqual(report.warnings, ['foo'])

if __name__ == '__main__':
    main()
