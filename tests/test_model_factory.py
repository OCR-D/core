from tests.base import TestCase, main, assets

from ocrd_utils import MIMETYPE_PAGE
from ocrd_models import OcrdFile
from ocrd_modelfactory import (
    exif_from_filename,
    page_from_file
)

SAMPLE_IMG = assets.path_to('kant_aufklaerung_1784/data/OCR-D-IMG/INPUT_0017.tif')
SAMPLE_PAGE = assets.path_to('kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0017_PAGE.xml')

class TestModelFactory(TestCase):

    def test_exif_from_filename(self):
        exif_from_filename(SAMPLE_IMG)
        with self.assertRaisesRegex(Exception, "Must pass 'image_filename' to 'exif_from_filename'"):
            exif_from_filename(None)

    def test_page_from_file(self):
        f = OcrdFile(None, mimetype='image/tiff', local_filename=SAMPLE_IMG, ID='file1')
        self.assertEqual(f.mimetype, 'image/tiff')
        p = page_from_file(f)
        self.assertEqual(p.get_Page().imageWidth, 1457)

    def test_page_from_file_page(self):
        f = OcrdFile(None, mimetype=MIMETYPE_PAGE, local_filename=SAMPLE_PAGE)
        p = page_from_file(f)
        self.assertEqual(p.get_Page().imageWidth, 1457)

    def test_page_from_file_no_local_filename(self):
        with self.assertRaisesRegex(ValueError, "input_file must have 'local_filename' property"):
            page_from_file(OcrdFile(None, mimetype='image/tiff'))

    def test_page_from_file_no_existe(self):
        with self.assertRaisesRegex(FileNotFoundError, "File not found: 'no-existe'"):
            page_from_file(OcrdFile(None, local_filename='no-existe', mimetype='foo/bar'))

    def test_page_from_file_unsupported_mimetype(self):
        with self.assertRaisesRegex(ValueError, "Unsupported mimetype"):
            page_from_file(OcrdFile(None, local_filename=__file__, mimetype='foo/bar'))

    def test_imports_from_generateds(self):
        from ocrd_models.ocrd_page import MetadataItemType

if __name__ == '__main__':
    main()
