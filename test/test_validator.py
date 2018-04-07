from ocrd.resolver import Resolver
from ocrd.validator import Validator, ValidationReport
from test.base import TestCase, assets, main
METS_HEROLD_SMALL = assets.url_of('SBB0000F29300010000/mets_one_file.xml')

class TestValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver(cache_enabled=True)

    def test_report(self):
        report = ValidationReport()
        self.assertEqual(str(report), 'OK')
        report.add_warning('This is not good')
        report.add_error('This is bad')
        self.assertEqual(report.to_xml(), '''\
<report valid="false">
  <warning>This is not good</warning>
  <error>This is bad</error>
</report>''')

    def test_basic(self):
        report = Validator.validate_url(self.resolver, METS_HEROLD_SMALL)
        print(report.to_xml())

if __name__ == '__main__':
    main()
