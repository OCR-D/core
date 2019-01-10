from tests.base import TestCase, main, assets

from ocrd_models import OcrdFile
from ocrd.model_factory import page_from_file

class TestModelFactory(TestCase):

    def test_page_from_file(self):
        f = OcrdFile(
            None,
            mimetype='image/tiff',
            local_filename=assets.path_to('kant_aufklaerung_1784/data/OCR-D-IMG/INPUT_0017')
        )
        self.assertEqual(f.mimetype, 'image/tiff')
        p = page_from_file(f)
        self.assertEqual(p.get_Page().imageWidth, 1457)

if __name__ == '__main__':
    main()
