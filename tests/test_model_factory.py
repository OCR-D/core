from tests.base import TestCase, main, assets, create_ocrd_file, create_ocrd_file_with_defaults

from ocrd_utils import MIMETYPE_PAGE
from ocrd_models import OcrdMets
from ocrd_modelfactory import (
    exif_from_filename,
    page_from_image,
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
        f = create_ocrd_file_with_defaults(mimetype='image/tiff', local_filename=SAMPLE_IMG, ID='file1')
        self.assertEqual(f.mimetype, 'image/tiff')
        p = page_from_file(f)
        self.assertEqual(p.pcGtsId, f.ID)
        self.assertEqual(p.get_Page().imageWidth, 1457)

    def test_page_from_file_page(self):
        f = create_ocrd_file_with_defaults(mimetype=MIMETYPE_PAGE, local_filename=SAMPLE_PAGE)
        p = page_from_file(f)
        self.assertEqual(p.get_Page().imageWidth, 1457)

    def test_page_from_file_no_local_filename(self):
        with self.assertRaisesRegex(ValueError, "input_file must have 'local_filename' property"):
            page_from_file(create_ocrd_file_with_defaults(mimetype='image/tiff'))

    def test_page_from_file_no_existe(self):
        with self.assertRaisesRegex(FileNotFoundError, "File not found: 'no-existe'"):
            mets = OcrdMets.empty_mets()
            ocrd_file = mets.add_file('FOO', ID='foo', local_filename='no-existe', mimetype='foo/bar')
            page_from_file(ocrd_file)

    def test_page_from_file_unsupported_mimetype(self):
        with self.assertRaisesRegex(ValueError, "Unsupported mimetype"):
            page_from_file(create_ocrd_file_with_defaults(local_filename=__file__, mimetype='foo/bar'))

    def test_imports_from_generateds(self):
        from ocrd_models.ocrd_page import MetadataItemType

if __name__ == '__main__':
    main(__file__)
