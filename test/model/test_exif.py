from ocrd.model import OcrdExif

from test.base import TestCase, main, assets
TEST_IMG = assets.url_of('SBB0000F29300010000//00000001.tif')[len('file://'):]

class TestOcrdExif(TestCase):

    def runTest(self):
        exif = OcrdExif.from_filename(TEST_IMG)
        self.assertEqual(exif.width, 2875)
        self.assertEqual(exif.height, 3749)

if __name__ == '__main__':
    main()
