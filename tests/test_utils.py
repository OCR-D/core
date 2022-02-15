from os import getcwd
from tempfile import TemporaryDirectory, gettempdir
from pathlib import Path

from PIL import Image

from tests.base import TestCase, main, assets, create_ocrd_file
from ocrd_utils import (
    abspath,

    assert_file_grp_cardinality,
    make_file_id,

    bbox_from_points,
    bbox_from_xywh,

    concat_padded,
    is_local_filename,
    get_local_filename,
    is_string,
    membername,
    generate_range,

    nth_url_segment,
    remove_non_path_from_url,

    parse_json_string_or_file,
    set_json_key_value_overrides,

    points_from_bbox,
    points_from_x0y0x1y1,
    points_from_xywh,
    points_from_polygon,

    polygon_from_points,
    polygon_from_x0y0x1y1,

    xywh_from_points,
    xywh_from_polygon,
    pushd_popd,

    MIME_TO_EXT, EXT_TO_MIME,
    MIME_TO_PIL, PIL_TO_MIME,
)
from ocrd_models.utils import xmllint_format
from ocrd_models import OcrdMets

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
        self.assertEqual(concat_padded('x', 1), 'x_0001')
        self.assertEqual(concat_padded('x', 1, 2, 3), 'x_0001_0002_0003')
        self.assertEqual(concat_padded('x', 1, '2', 3), 'x_0001_2_0003')

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

    def test_pushd_popd_newcwd(self):
        cwd = getcwd()
        with pushd_popd('/tmp'):
            self.assertEqual(getcwd(), '/tmp')
        self.assertEqual(getcwd(), cwd)

    def test_pushd_popd_tempdir(self):
        cwd = getcwd()
        with pushd_popd(tempdir=True) as newcwd:
            self.assertEqual(getcwd(), newcwd)
            self.assertTrue(newcwd.startswith(gettempdir()))
        self.assertEqual(getcwd(), cwd)

    def test_pushd_popd_bad_call(self):
        with self.assertRaisesRegex(Exception, 'pushd_popd can accept either newcwd or tempdir, not both'):
            with pushd_popd('/foo/bar', True):
                pass

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

    def test_parse_json_string_or_file(self):
        self.assertEqual(parse_json_string_or_file(), {})
        self.assertEqual(parse_json_string_or_file(''), {})
        self.assertEqual(parse_json_string_or_file(' '), {})
        self.assertEqual(parse_json_string_or_file('{}'), {})
        self.assertEqual(parse_json_string_or_file('{"foo": 32}'), {'foo': 32})
        self.assertEqual(parse_json_string_or_file(
          '{"dpi": -1, "textequiv_level": "word", "overwrite_words": false, "raw_lines": false, "char_whitelist": "", "char_blacklist": "", "char_unblacklist": ""}'
        ), {"dpi": -1, "textequiv_level": "word", "overwrite_words": False, "raw_lines": False, "char_whitelist": "", "char_blacklist": "", "char_unblacklist": ""})

    def test_parameter_file(self):
        """
        Verify that existing filenames get priority over valid JSON string interpretation
        """
        with TemporaryDirectory() as tempdir:
            paramfile = Path(tempdir, '{"foo":23}')  # XXX yes, the file is called '{"foo":23}'
            paramfile.write_text('{"bar": 42}')
            # /tmp/<var>/{"foo":23} -- exists, read file and parse as JSON
            self.assertEqual(parse_json_string_or_file(str(paramfile)), {'bar': 42})
            # $PWD/{"foo":23} -- does not exist, parse as json
            self.assertEqual(parse_json_string_or_file(paramfile.name), {'foo': 23})

    def test_parameter_file_comments(self):
        with TemporaryDirectory() as tempdir:
            jsonpath = Path(tempdir, 'test.json')
            jsonpath.write_text("""\
                    {
                        # Metasyntactical variables are rarely imaginative
                        "foo": 42,
                        # case in point:
                        "bar": 23
                    }""")
            self.assertEqual(parse_json_string_or_file(str(jsonpath)), {'foo': 42, 'bar': 23})

    def test_parameters_invalid(self):
        with self.assertRaisesRegex(ValueError, 'Not a valid JSON object'):
            parse_json_string_or_file('[]')
        with self.assertRaisesRegex(ValueError, 'Error parsing'):
            parse_json_string_or_file('[}')

    def test_mime_ext(self):
        self.assertEqual(MIME_TO_EXT['image/jp2'], '.jp2')
        self.assertEqual(EXT_TO_MIME['.jp2'], 'image/jp2')
        self.assertEqual(MIME_TO_PIL['image/jp2'], 'JP2')
        self.assertEqual(PIL_TO_MIME['JP2'], 'image/jp2')


    def test_set_json_key_value_overrides(self):
        self.assertEqual(set_json_key_value_overrides({}, ('foo', 'true')), {'foo': True})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', 'false')), {'foo': False})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', '42')), {'foo': 42})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', '42.3')), {'foo': 42.3})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', '["one", 2, 3.33]')), {'foo': ['one', 2, 3.33]})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', '{"one": 2}')), {'foo': {'one': 2}})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', '"a string"')), {'foo': 'a string'})
        self.assertEqual(set_json_key_value_overrides({}, ('foo', 'a string')), {'foo': 'a string'})

    def test_assert_file_grp_cardinality(self):
        with self.assertRaisesRegex(AssertionError, "Expected exactly 5 output file groups, but '.'FOO', 'BAR'.' has 2"):
            assert_file_grp_cardinality('FOO,BAR', 5)
        with self.assertRaisesRegex(AssertionError, "Expected exactly 1 output file group, but '.'FOO', 'BAR'.' has 2"):
            assert_file_grp_cardinality('FOO,BAR', 1)
        assert_file_grp_cardinality('FOO,BAR', 2)
        with self.assertRaisesRegex(AssertionError, r"Expected exactly 1 output file group .foo bar., but '.'FOO', 'BAR'.' has 2"):
            assert_file_grp_cardinality('FOO,BAR', 1, 'foo bar')

    def test_make_file_id_simple(self):
        f = create_ocrd_file('MAX', ID="MAX_0012")
        self.assertEqual(make_file_id(f, 'FOO'), 'FOO_0012')

    def test_make_file_id_mets(self):
        mets = OcrdMets.empty_mets()
        for i in range(1, 10):
            mets.add_file('FOO', ID="FOO_%04d" % (i), mimetype="image/tiff")
            mets.add_file('BAR', ID="BAR_%04d" % (i), mimetype="image/tiff")
        self.assertEqual(make_file_id(mets.find_all_files(ID='BAR_0007')[0], 'FOO'), 'FOO_0007')
        f = mets.add_file('ABC', ID="BAR_7", mimetype="image/tiff")
        self.assertEqual(make_file_id(f, 'FOO'), 'FOO_0010')
        mets.remove_file(fileGrp='FOO')
        self.assertEqual(make_file_id(f, 'FOO'), 'FOO_0001')
        mets.add_file('FOO', ID="FOO_0001", mimetype="image/tiff")
        # print('\n'.join(['%s' % of for of in mets.find_all_files()]))
        self.assertEqual(make_file_id(f, 'FOO'), 'FOO_0002')

    def test_make_file_id_570(self):
        """https://github.com/OCR-D/core/pull/570"""
        mets = OcrdMets.empty_mets()
        f = mets.add_file('GRP', ID='FOO_0001', pageId='phys0001')
        mets.add_file('GRP', ID='GRP2_0001', pageId='phys0002')
        self.assertEqual(make_file_id(f, 'GRP2'), 'GRP2_0002')

    def test_make_file_id_605(self):
        """https://github.com/OCR-D/core/pull/605"""
        mets = OcrdMets.empty_mets()
        f = mets.add_file('GRP1', ID='FOO_0001', pageId='phys0001')
        f = mets.add_file('GRP2', ID='FOO_0002', pageId='phys0002')
        self.assertEqual(make_file_id(f, 'GRP2'), 'GRP2_0001')

    def test_make_file_id_744(self):
        """
        https://github.com/OCR-D/core/pull/744
        > Often file IDs have two numbers, one of which will clash. In that case only the numerical fallback works.
        """
        mets = OcrdMets.empty_mets()
        f = mets.add_file('GRP2', ID='img1796-97_00000024_img', pageId='phys0024')
        f = mets.add_file('GRP2', ID='img1796-97_00000025_img', pageId='phys0025')
        self.assertEqual(make_file_id(f, 'GRP2'), 'GRP2_0002')

    def test_generate_range(self):
        assert generate_range('PHYS_0001', 'PHYS_0005') == ['PHYS_0001', 'PHYS_0002', 'PHYS_0003', 'PHYS_0004', 'PHYS_0005']
        with self.assertRaisesRegex(ValueError, 'Unable to generate range'):
            generate_range('NONUMBER', 'ALSO_NONUMBER')


if __name__ == '__main__':
    main(__file__)
