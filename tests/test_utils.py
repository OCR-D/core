from os import getcwd, chdir
from tests.base import TestCase, main, assets
from ocrd_utils import (
    abspath,
    is_local_filename,
    points_from_xywh,
    is_string,
    concat_padded,
    points_from_x0y0x1y1,
    pushd_popd,
    polygon_from_points,
    xywh_from_points,
)
from ocrd_models.utils import xmllint_format

from PIL import Image

class TestUtils(TestCase):

    #  def runTest(self):

    def test_abspath(self):
        self.assertEqual(abspath('file:///'), '/')

    def test_is_local_filename(self):
        self.assertEqual(is_local_filename('file:///'), True)

    def test_points_from_xywh(self):
        self.assertEqual(
            points_from_xywh({'x': 100, 'y': 100, 'w': 100, 'h': 100}),
            '100,100 200,100 200,200 100,200'
        )

    def test_points_from_x0y0x1y1(self):
        self.assertEqual(
            points_from_x0y0x1y1([100, 100, 200, 200]),
            '100,100 200,100 200,200 100,200'
        )


    def test_xywh_from_points(self):
        self.assertEqual(
            xywh_from_points('100,100 200,100 200,200 100,200'),
            {'x': 100, 'y': 100, 'w': 100, 'h': 100})

    def test_xywh_from_points_unordered(self):
        self.assertEqual(
            xywh_from_points('500,500 100,100 200,100 200,200 100,200'),
            {'x': 100, 'y': 100, 'w': 400, 'h': 400})

    def test_polygon_from_points(self):
        self.assertEqual(
            polygon_from_points('100,100 200,100 200,200 100,200'),
            [[100, 100], [200, 100], [200, 200], [100, 200]])

    def test_concat_padded(self):
        self.assertEqual(concat_padded('x', 0), 'x_0001')
        self.assertEqual(concat_padded('x', 0, 1, 2), 'x_0001_0002_0003')
        self.assertEqual(concat_padded('x', 0, '1', 2), 'x_0001_1_0003')

    def test_is_string(self):
        self.assertTrue(is_string('x'))
        self.assertTrue(is_string(u'x'))

    def test_xmllint(self):
        xml_str = '<beep>\n  <boop>42</boop>\n</beep>\n'
        pretty_xml = xmllint_format(xml_str).decode('utf-8')
        self.assertEqual(pretty_xml, '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str)

    def test_pil_version(self):
        """
        Test segfault issue in PIL TiffImagePlugin

        Run the same code multiple times to make segfaults more probable

        Should fail persistently:
            5.3.1 no
            5.4.1 no
            6.0.0 yes
            6.1.0 yes
        """
        for _ in range(0, 10):
            pil_image = Image.open(assets.path_to('grenzboten-test/data/OCR-D-IMG-BIN/p179470'))
            pil_image.crop(box=[1539, 202, 1626, 271])

    def test_pushd_popd(self):
        cwd = getcwd()
        with pushd_popd('/tmp'):
            self.assertEqual(getcwd(), '/tmp')
        self.assertEqual(getcwd(), cwd)


if __name__ == '__main__':
    main()
