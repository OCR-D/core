from ocrd_models import ValidationReport
from tests.base import (  # pylint: disable=import-error,no-name-in-module
    TestCase, main)


class TestValidationReport(TestCase):

    def test_str(self):
        report = ValidationReport()
        report.add_error('This is bad')
        self.assertEqual(str(report), 'INVALID[ 1 errors ]')

    def test_toxml(self):
        report = ValidationReport()
        self.assertEqual(str(report), 'OK')
        report.add_warning('This is not good')
        self.assertEqual(str(report), 'INVALID[ 1 warnings ]')
        report.add_error('This is bad')
        self.assertEqual(str(report), 'INVALID[ 1 warnings 1 errors ]')
        report.add_notice('This is noticeable')
        self.assertEqual(str(report), 'INVALID[ 1 warnings 1 errors 1 notices ]')
        self.assertEqual(report.to_xml(), '''\
<report valid="false">
  <warning>This is not good</warning>
  <error>This is bad</error>
  <notice>This is noticeable</notice>
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
