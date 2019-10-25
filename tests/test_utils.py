from os import getcwd

from PIL import Image

from tests.base import TestCase, main, assets
from ocrd_utils import (
    abspath,

    bbox_from_points,
    bbox_from_xywh,

    concat_padded,
    is_local_filename,
    get_local_filename,
    is_string,
    membername,

    nth_url_segment,
    remove_non_path_from_url,

    points_from_bbox,
    points_from_x0y0x1y1,
    points_from_xywh,
    points_from_polygon,

    polygon_from_points,
    polygon_from_x0y0x1y1,

    xywh_from_points,
    xywh_from_polygon,
    pushd_popd,

)
from ocrd_models.utils import xmllint_format

class TestUtils(TestCase):

    def test_abspath(self):
        self.assertEqual(abspath('file:///'), '/')

    def test_points_from_xywh(self):
        self.assertEqual(
            points_from_xywh({'x': 100, 'y': 100, 'w': 100, 'h': 100}),
            '100,100 200,100 200,200 100,200')

    def test_points_from_bbox(self):
        self.assertEqual(
            points_from_bbox(100, 100, 200, 200),
            '100,100 200,100 200,200 100,200')

    def test_points_from_polygon(self):
        self.assertEqual(
            points_from_polygon([[100, 100], [200, 100], [200, 200], [100, 200]]),
            '100,100 200,100 200,200 100,200')

    def test_polygon_from_x0y0x1y1(self):
        self.assertEqual(
            polygon_from_x0y0x1y1([100, 100, 200, 200]),
            [[100, 100], [200, 100], [200, 200], [100, 200]])

    def test_points_from_x0y0x1y1(self):
        self.assertEqual(
            points_from_x0y0x1y1([100, 100, 200, 200]),
            '100,100 200,100 200,200 100,200')

    def test_bbox_from_points(self):
        self.assertEqual(
            bbox_from_points('100,100 200,100 200,200 100,200'), (100, 100, 200, 200))

    def test_bbox_from_xywh(self):
        self.assertEqual(
            bbox_from_xywh({'x': 100, 'y': 100, 'w': 100, 'h': 100}),
            (100, 100, 200, 200))

    def test_xywh_from_polygon(self):
        self.assertEqual(
            xywh_from_polygon([[100, 100], [200, 100], [200, 200], [100, 200]]),
            {'x': 100, 'y': 100, 'w': 100, 'h': 100})

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

    def test_membername(self):
        class Klazz:
            def __init__(self):
                self.prop = 42
        instance = Klazz()
        self.assertEqual(membername(instance, 42), 'prop')

    def test_pil_version(self):
        """
        Test segfault issue in PIL TiffImagePlugin

        Run the same code multiple times to make segfaults more probable

        Test is failing due to segfaults in Pillow versions:
            6.0.0
            6.1.0

        Test succeeds in Pillow versions:
            5.3.1
            5.4.1
            6.2.0
        """
        for _ in range(0, 10):
            pil_image = Image.open(assets.path_to('grenzboten-test/data/OCR-D-IMG-BIN/p179470.tif'))
            pil_image.crop(box=[1539, 202, 1626, 271])

    def test_pushd_popd(self):
        cwd = getcwd()
        with pushd_popd('/tmp'):
            self.assertEqual(getcwd(), '/tmp')
        self.assertEqual(getcwd(), cwd)

    def test_is_local_filename(self):
        self.assertTrue(is_local_filename('/foo/bar'))
        self.assertTrue(is_local_filename('file:///foo/bar'))
        self.assertTrue(is_local_filename('file:/foo/bar'))
        self.assertTrue(is_local_filename('foo/bar'))
        self.assertFalse(is_local_filename('bad-scheme://foo/bar'))

    def test_local_filename(self):
        self.assertEqual(get_local_filename('/foo/bar'), '/foo/bar')
        self.assertEqual(get_local_filename('file:///foo/bar'), '/foo/bar')
        self.assertEqual(get_local_filename('file:/foo/bar'), '/foo/bar')
        self.assertEqual(get_local_filename('/foo/bar', '/foo/'), 'bar')
        self.assertEqual(get_local_filename('/foo/bar', '/foo'), 'bar')
        self.assertEqual(get_local_filename('foo/bar', 'foo'), 'bar')

    def test_remove_non_path_from_url(self):
        self.assertEqual(remove_non_path_from_url('https://foo/bar'), 'https://foo/bar')
        self.assertEqual(remove_non_path_from_url('https://foo//?bar#frag'), 'https://foo')
        self.assertEqual(remove_non_path_from_url('/path/to/foo#frag'), '/path/to/foo')

    def test_nth_url_segment(self):
        self.assertEqual(nth_url_segment(''), '')
        self.assertEqual(nth_url_segment('foo'), 'foo')
        self.assertEqual(nth_url_segment('foo', n=-1), 'foo')
        self.assertEqual(nth_url_segment('foo', n=-2), '')
        self.assertEqual(nth_url_segment('foo/bar', n=-2), 'foo')
        self.assertEqual(nth_url_segment('/baz/bar', n=-2), 'baz')
        self.assertEqual(nth_url_segment('foo/'), 'foo')
        self.assertEqual(nth_url_segment('foo//?bar#frag'), 'foo')
        self.assertEqual(nth_url_segment('/path/to/foo#frag'), 'foo')
        self.assertEqual(nth_url_segment('/path/to/foo#frag', n=-2), 'to')
        self.assertEqual(nth_url_segment('https://server/foo?xyz=zyx'), 'foo')

if __name__ == '__main__':
    main()
