from tests.base import TestCase, assets, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd_validators import PageValidator
from ocrd_validators.page_validator import get_text, set_text
from ocrd_models.ocrd_page import parse, TextEquivType
from ocrd_utils import pushd_popd

class TestPageValidator(TestCase):

    def setUp(self):
        pass

    def test_validate_err(self):
        with self.assertRaisesRegex(Exception, 'At least one of ocrd_page, ocrd_file or filename must be set'):
            PageValidator.validate()
        with self.assertRaisesRegex(Exception, 'Element selection strategy best not implemented'):
            PageValidator(None, None, 'best')
        with self.assertRaisesRegex(Exception, 'Strictness level superstrictest not implemented'):
            PageValidator(None, 'superstrictest', 'index1')

    def test_validate_filename(self):
        report = PageValidator.validate(filename=assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'))
        self.assertEqual(len(report.errors), 17, '17 errors')

    def test_validate_filename_off(self):
        report = PageValidator.validate(filename=assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'), strictness='off')
        self.assertEqual(len(report.errors), 0, 'no errors')

    def test_validate_ocrd_file(self):
        resolver = Resolver()
        workspace = resolver.workspace_from_url(assets.url_of('glyph-consistency/data/mets.xml'))
        with pushd_popd(workspace.directory):
            ocrd_file = workspace.mets.find_files(ID="FAULTY_GLYPHS_FILE")[0]
            report = PageValidator.validate(ocrd_file=ocrd_file)
            self.assertEqual(len(report.errors), 17, 'errors')

    def test_validate_lax(self):
        ocrd_page = parse(assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0020_PAGE'), silence=True)

        # introduce a single word error (not just whitespace inconsistency)
        ocrd_page.get_Page().get_TextRegion()[0].get_TextLine()[0].get_Word()[1].get_TextEquiv()[0].set_Unicode('FOO')

        self.assertEqual(len(PageValidator.validate(ocrd_page=ocrd_page).errors), 26, '26 errors - strict')
        self.assertEqual(len(PageValidator.validate(ocrd_page=ocrd_page, strictness='lax').errors), 1, '1 error - lax')

    def test_validate_multi_textequiv_index1(self):
        ocrd_page = parse(assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0020_PAGE'), silence=True)
        self.assertEqual(len(PageValidator.validate(ocrd_page=ocrd_page).errors), 25, '25 errors - strict')

        word = ocrd_page.get_Page().get_TextRegion()[0].get_TextLine()[0].get_Word()[1]

        # delete all textequivs
        del(word.get_TextEquiv()[0])

        # Add textequiv
        set_text(word, 'FOO', 'index1')
        word.add_TextEquiv(TextEquivType(Unicode='BAR', conf=.7))
        word.add_TextEquiv(TextEquivType(Unicode='BAZ', conf=.5, index=1))
        self.assertEqual(get_text(word, 'index1'), 'BAZ')
        set_text(word, 'XYZ', 'index1')
        self.assertEqual(get_text(word, 'index1'), 'XYZ')


    def test_validate_multi_textequiv(self):
        ocrd_page = parse(assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0020_PAGE'), silence=True)
        self.assertEqual(len(PageValidator.validate(ocrd_page=ocrd_page).errors), 25, '25 errors - strict')

        word = ocrd_page.get_Page().get_TextRegion()[0].get_TextLine()[0].get_Word()[1]

        # delete all textequivs
        del(word.get_TextEquiv()[0])

        # Add textequiv
        set_text(word, 'FOO', 'index1')
        word.add_TextEquiv(TextEquivType(Unicode='BAR', conf=.7))

        self.assertEqual(get_text(word, 'index1'), 'FOO')
        set_text(word, 'BAR', 'index1')
        self.assertEqual(get_text(word, 'index1'), 'BAR')


    def test_fix(self):
        ocrd_page = parse(assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'), silence=True)
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len(report.errors), 17, 'errors')
        PageValidator.validate(ocrd_page=ocrd_page, strictness='fix')
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len(report.errors), 0, 'no more errors')

if __name__ == '__main__':
    main()
