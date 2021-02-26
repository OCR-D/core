from PIL import Image
from tests.base import TestCase, main, assets

from ocrd_models import OcrdExif

# pylint: disable=no-member
class TestOcrdExif(TestCase):

    def test_str(self):
        with Image.open(assets.path_to('SBB0000F29300010000/data/OCR-D-IMG/FILE_0001_IMAGE.tif')) as img:
            exif = OcrdExif(img)
        print(str(exif.to_xml()))
        # XXX not platform-independent/stable
        #  self.assertEqual(
        #      exif.to_xml(),
        #      '<exif><width>2875</width><height>3749</height><photometricInterpretation>RGB</photometricInterpretation><compression>jpeg</compression><photometric_interpretation>None</photometric_interpretation><xResolution>300.0</xResolution><yResolution>300.0</yResolution><resolutionUnit>inches</resolutionUnit></exif>'
        #  )


    def test_tiff(self):
        with Image.open(assets.path_to('SBB0000F29300010000/data/OCR-D-IMG/FILE_0001_IMAGE.tif')) as img:
            exif = OcrdExif(img)
        self.assertEqual(exif.width, 2875)
        self.assertEqual(exif.height, 3749)
        self.assertEqual(exif.xResolution, 300)
        self.assertEqual(exif.yResolution, 300)
        self.assertEqual(exif.resolution, 300)
        self.assertEqual(exif.compression, 'jpeg')
        self.assertEqual(exif.photometricInterpretation, 'RGB')
        self.assertEqual(exif.resolutionUnit, 'inches')

    def test_png1(self):
        with Image.open(assets.path_to('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-BIN/BIN_0020.png')) as img:
            exif = OcrdExif(img)
        self.assertEqual(exif.width, 1457)
        self.assertEqual(exif.height, 2084)
        self.assertEqual(exif.xResolution, 116)
        self.assertEqual(exif.yResolution, 116)
        self.assertEqual(exif.resolution, 116)
        self.assertEqual(exif.resolutionUnit, 'cm')
        self.assertEqual(exif.compression, None)
        self.assertEqual(exif.photometricInterpretation, '1')

    def test_png2(self):
        with Image.open(assets.path_to('scribo-test/data/OCR-D-PRE-BIN-SAUVOLA/OCR-D-PRE-BIN-SAUVOLA_0001-BIN_sauvola.png')) as img:
            exif = OcrdExif(img)
        self.assertEqual(exif.width, 2097)
        self.assertEqual(exif.height, 3062)
        self.assertEqual(exif.xResolution, 72)
        self.assertEqual(exif.yResolution, 72)
        self.assertEqual(exif.resolution, 72)
        self.assertEqual(exif.photometricInterpretation, '1')
        self.assertEqual(exif.resolutionUnit, 'inches')

    def test_jpg(self):
        with Image.open(assets.path_to('leptonica_samples/data/OCR-D-IMG/OCR-D-IMG_1555_007.jpg')) as img:
            exif = OcrdExif(img)
        self.assertEqual(exif.width, 944)
        self.assertEqual(exif.height, 1472)
        self.assertEqual(exif.xResolution, 72)
        self.assertEqual(exif.yResolution, 72)
        self.assertEqual(exif.resolution, 72)
        self.assertEqual(exif.resolutionUnit, 'inches')
        self.assertEqual(exif.photometricInterpretation, 'RGB')
        self.assertEqual(exif.resolutionUnit, 'inches')

    def test_jp2(self):
        with Image.open(assets.path_to('kant_aufklaerung_1784-jp2/data/OCR-D-IMG/INPUT_0020.jp2')) as img:
            exif = OcrdExif(img)
        self.assertEqual(exif.width, 1457)
        self.assertEqual(exif.height, 2084)
        self.assertEqual(exif.xResolution, 1)
        self.assertEqual(exif.yResolution, 1)
        self.assertEqual(exif.resolution, 1)
        self.assertEqual(exif.photometricInterpretation, 'RGB')
        self.assertEqual(exif.resolutionUnit, 'inches')

    # def test_kolonie(self):
        # with Image.open('/tmp/Kolonie186-fixed.png') as img:
            # exif = OcrdExif(img)
            # print(exif.to_xml())
            # assert exif.resolution == 236

if __name__ == '__main__':
    main(__file__)
