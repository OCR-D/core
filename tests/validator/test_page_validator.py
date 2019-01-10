from tests.base import TestCase, assets, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd_validators import PageValidator
from ocrd_models.ocrd_page import parse

class TestPageValidator(TestCase):

    def setUp(self):
        pass

    def test_validate_filename(self):
        report = PageValidator.validate(filename=assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'))
        self.assertEqual(len(report.errors), 17, 'errors')

    def test_validate_ocrd_file(self):
        resolver = Resolver()
        workspace = resolver.workspace_from_url(assets.url_of('glyph-consistency/data/mets.xml'))
        ocrd_file = workspace.mets.find_files(ID="FAULTY_GLYPHS_FILE")[0]
        report = PageValidator.validate(ocrd_file=ocrd_file)
        self.assertEqual(len(report.errors), 17, 'errors')

    def test_validate_lax(self):
        resolver = Resolver()
        workspace = resolver.workspace_from_url(assets.url_of('kant_aufklaerung_1784/data/mets.xml'))
        ocrd_file = workspace.mets.find_files(ID="PAGE_0020_PAGE")[0]
        self.assertEqual(len(PageValidator.validate(ocrd_file=ocrd_file).errors), 25, '25 errors - strict')
        self.assertEqual(len(PageValidator.validate(ocrd_file=ocrd_file, strictness='lax').errors), 0, 'no errors - lax')

    def test_fix(self):
        ocrd_page = parse(assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'), silence=True)
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len(report.errors), 17, 'errors')
        PageValidator.validate(ocrd_page=ocrd_page, strictness='fix')
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len(report.errors), 0, 'no more errors')

if __name__ == '__main__':
    main()
