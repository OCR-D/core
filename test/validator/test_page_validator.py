from test.base import TestCase, assets, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd.validator import PageValidator
from ocrd.model.ocrd_page import parse

class TestPageValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        #  self.workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))

    def test_fix(self):
        page = parse(assets.path_to('page-with-glyphs.xml'), silence=True)
        report = PageValidator.validate_ocrd_page(page)
        self.assertEqual(len(report.errors), 63, 'errors')
        PageValidator.validate_ocrd_page(page, strictness='fix')
        report = PageValidator.validate_ocrd_page(page)
        self.assertEqual(len(report.errors), 0, 'no more errors')

if __name__ == '__main__':
    main()
