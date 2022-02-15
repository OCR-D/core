from tests.base import TestCase, assets, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd_validators import PageValidator
from ocrd_validators.page_validator import get_text, set_text, ConsistencyError
from ocrd_models.ocrd_page import parse, TextEquivType
from ocrd_utils import pushd_popd

FAULTY_GLYPH_PAGE_FILENAME = assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS.xml')

class TestPageValidator(TestCase):

    def test_validate_err(self):
        with self.assertRaisesRegex(Exception, 'At least one of ocrd_page, ocrd_file or filename must be set'):
            PageValidator.validate()
        with self.assertRaisesRegex(Exception, 'page_textequiv_strategy best not implemented'):
            PageValidator.validate(filename=FAULTY_GLYPH_PAGE_FILENAME, page_textequiv_strategy='best')
        # test with deprecated name
        with self.assertRaisesRegex(Exception, 'page_textequiv_strategy best not implemented'):
            PageValidator.validate(filename=FAULTY_GLYPH_PAGE_FILENAME, strategy='best')
        with self.assertRaisesRegex(Exception, 'page_textequiv_consistency level superstrictest not implemented'):
            PageValidator.validate(filename=FAULTY_GLYPH_PAGE_FILENAME, page_textequiv_consistency='superstrictest', strategy='first')

    def test_validate_filename(self):
        report = PageValidator.validate(filename=FAULTY_GLYPH_PAGE_FILENAME)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 17, '17 textequiv consistency errors')

    def test_validate_filename_off(self):
        report = PageValidator.validate(filename=FAULTY_GLYPH_PAGE_FILENAME, page_textequiv_consistency='off')
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 0, '0 textequiv consistency errors')

    def test_validate_ocrd_file(self):
        resolver = Resolver()
        workspace = resolver.workspace_from_url(assets.url_of('glyph-consistency/data/mets.xml'))
        with pushd_popd(workspace.directory):
            ocrd_file = workspace.mets.find_all_files(ID="FAULTY_GLYPHS_FILE")[0]
            report = PageValidator.validate(ocrd_file=ocrd_file)
            self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 17, '17 textequiv consistency errors')

    def test_validate_lax(self):
        ocrd_page = parse(assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0020_PAGE.xml'), silence=True)

        # introduce a single word error (not just whitespace inconsistency)
        ocrd_page.get_Page().get_TextRegion()[0].get_TextLine()[0].get_Word()[1].get_TextEquiv()[0].set_Unicode('FOO')

        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 26, '26 textequiv consistency errors - strict')
        report = PageValidator.validate(ocrd_page=ocrd_page, strictness='lax')
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 1, '1 textequiv consistency errors - lax')

    def test_validate_multi_textequiv_first(self):
        ocrd_page = parse(assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0020_PAGE.xml'), silence=True)
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 25, '25 textequiv consistency errors - strict')

        word = ocrd_page.get_Page().get_TextRegion()[0].get_TextLine()[0].get_Word()[1]

        # delete all textequivs
        word.set_TextEquiv([])

        # Add textequiv
        set_text(word, 'FOO', 'first')
        word.add_TextEquiv(TextEquivType(Unicode='BAR', conf=.7))
        word.add_TextEquiv(TextEquivType(Unicode='BAZ', conf=.5, index=0))
        self.assertEqual(get_text(word, 'first'), 'BAZ')
        set_text(word, 'XYZ', 'first')
        self.assertEqual(get_text(word, 'first'), 'XYZ')


    def test_validate_multi_textequiv(self):
        ocrd_page = parse(assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0020_PAGE.xml'), silence=True)
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 25, '25 textequiv consistency errors - strict')

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
        ocrd_page = parse(FAULTY_GLYPH_PAGE_FILENAME, silence=True)
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 17, '17 textequiv consistency errors')
        PageValidator.validate(ocrd_page=ocrd_page, strictness='fix')
        report = PageValidator.validate(ocrd_page=ocrd_page)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 0, 'no more textequiv consistency errors')

if __name__ == '__main__':
    main()
