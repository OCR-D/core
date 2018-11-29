from test.base import TestCase, main, assets
from PIL import Image

from ocrd.model import OcrdExif

# pylint: disable=no-member
class TestOcrdExif(TestCase):

    def test_tiff(self):
        exif = OcrdExif.from_filename(assets.path_to('SBB0000F29300010000/data/OCR-D-IMG/FILE_0001_IMAGE'))
        self.assertEqual(exif.width, 2875)
        self.assertEqual(exif.height, 3749)
        self.assertEqual(exif.xResolution, 300)
        self.assertEqual(exif.yResolution, 300)
        self.assertEqual(exif.compression, 'jpeg')
        self.assertEqual(exif.photometricInterpretation, 'RGB')

    def test_png1(self):
        exif = OcrdExif.from_filename(assets.path_to('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-BIN/BIN_0020'))
        self.assertEqual(exif.width, 1457)
        self.assertEqual(exif.height, 2084)
        self.assertEqual(exif.xResolution, 1)
        self.assertEqual(exif.yResolution, 1)
        self.assertEqual(exif.compression, None)
        self.assertEqual(exif.photometricInterpretation, 'L')

    def test_png2(self):
        exif = OcrdExif.from_filename(assets.path_to('scribo-test/data/OCR-D-IMG-BIN-SAUVOLA/OCR-D-IMG-orig_sauvola_png'))
        self.assertEqual(exif.width, 2097)
        self.assertEqual(exif.height, 3062)
        self.assertEqual(exif.xResolution, 1)
        self.assertEqual(exif.yResolution, 1)
        self.assertEqual(exif.photometricInterpretation, '1')

    def test_jpg(self):
        exif = OcrdExif.from_filename(assets.path_to('leptonica_samples/data/OCR-D-IMG/OCR-D-IMG_1555_007'))
        self.assertEqual(exif.width, 944)
        self.assertEqual(exif.height, 1472)
        self.assertEqual(exif.xResolution, 1)
        self.assertEqual(exif.yResolution, 1)
        self.assertEqual(exif.photometricInterpretation, 'RGB')

    def test_jp2(self):
        exif = OcrdExif.from_filename(assets.path_to('kant_aufklaerung_1784-jp2/data/OCR-D-IMG/INPUT_0020'))
        self.assertEqual(exif.width, 1457)
        self.assertEqual(exif.height, 2084)
        self.assertEqual(exif.xResolution, 1)
        self.assertEqual(exif.yResolution, 1)
        self.assertEqual(exif.photometricInterpretation, 'RGB')

if __name__ == '__main__':
    main()
