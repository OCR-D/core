from os import getcwd
from tempfile import TemporaryDirectory, gettempdir
from pathlib import Path

from PIL import Image

from tests.base import TestCase, main, assets, create_ocrd_file
from pytest import raises, warns
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
    sparkline,

    nth_url_segment,
    remove_non_path_from_url,
    safe_filename,

    parse_json_string_or_file,
    set_json_key_value_overrides,

    partition_list,

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


def test_abspath():
    assert abspath('file:///') == '/'

def test_points_from_xywh():
    assert points_from_xywh({'x': 100, 'y': 100, 'w': 100, 'h': 100}) == '100,100 200,100 200,200 100,200'

def test_points_from_bbox():
    assert points_from_bbox(100, 100, 200, 200) == '100,100 200,100 200,200 100,200'

def test_points_from_polygon():
    assert points_from_polygon([[100, 100], [200, 100], [200, 200], [100, 200]]) == '100,100 200,100 200,200 100,200'

def test_polygon_from_x0y0x1y1():
    assert polygon_from_x0y0x1y1([100, 100, 200, 200]) == [[100, 100], [200, 100], [200, 200], [100, 200]]

def test_points_from_x0y0x1y1():
    assert points_from_x0y0x1y1([100, 100, 200, 200]) == '100,100 200,100 200,200 100,200'

def test_bbox_from_points():
    assert bbox_from_points('100,100 200,100 200,200 100,200') == (100, 100, 200, 200)

def test_bbox_from_xywh():
    assert bbox_from_xywh({'x': 100, 'y': 100, 'w': 100, 'h': 100}) == (100, 100, 200, 200)

def test_xywh_from_polygon():
    assert xywh_from_polygon([[100, 100], [200, 100], [200, 200], [100, 200]]) == {'x': 100, 'y': 100, 'w': 100, 'h': 100}

def test_xywh_from_points():
    assert xywh_from_points('100,100 200,100 200,200 100,200') == {'x': 100, 'y': 100, 'w': 100, 'h': 100}

def test_xywh_from_points_unordered():
    assert xywh_from_points('500,500 100,100 200,100 200,200 100,200') == {'x': 100, 'y': 100, 'w': 400, 'h': 400}

def test_polygon_from_points():
    assert polygon_from_points('100,100 200,100 200,200 100,200') == [[100, 100], [200, 100], [200, 200], [100, 200]]

def test_concat_padded():
    assert concat_padded('x', 1) == 'x_0001'
    assert concat_padded('x', 1, 2, 3) == 'x_0001_0002_0003'
    assert concat_padded('x', 1, '2', 3) == 'x_0001_2_0003'

def test_is_string():
    assert is_string('x')
    assert is_string(u'x')

def test_xmllint():
    xml_str = '<beep>\n  <boop>42</boop>\n</beep>\n'
    pretty_xml = xmllint_format(xml_str).decode('utf-8')
    assert pretty_xml == '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

def test_membername():
    class Klazz:
        def __init__(self):
            self.prop = 42
    instance = Klazz()
    assert membername(instance, 42) == 'prop'

def test_pil_version():
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

def test_pushd_popd_newcwd():
    cwd = getcwd()
    tmp_dir = Path(gettempdir()).resolve()
    with pushd_popd(tmp_dir):
        assert getcwd() == str(tmp_dir)
    assert getcwd() == cwd
    assert getcwd() == cwd

def test_pushd_popd_tempdir():
    cwd = getcwd()
    tmp_dir = str(Path(gettempdir()).resolve())
    with pushd_popd(tempdir=True) as newcwd:
        newcwd_str = str(newcwd)
        assert getcwd() == newcwd_str
        assert newcwd_str.startswith(tmp_dir)
    assert getcwd() == cwd
    assert getcwd() == cwd

def test_pushd_popd_bad_call():
    with raises(Exception, match='pushd_popd can accept either newcwd or tempdir, not both'):
        with pushd_popd('/foo/bar', True):
            pass

def test_is_local_filename():
    assert is_local_filename('/foo/bar')
    assert is_local_filename('file:///foo/bar')
    assert is_local_filename('file:/foo/bar')
    assert is_local_filename('foo/bar')
    assert not is_local_filename('bad-scheme://foo/bar')

def test_local_filename():
    assert get_local_filename('/foo/bar') == '/foo/bar'
    assert get_local_filename('file:///foo/bar') == '/foo/bar'
    assert get_local_filename('file:/foo/bar') == '/foo/bar'
    assert get_local_filename('/foo/bar', '/foo/') == 'bar'
    assert get_local_filename('/foo/bar', '/foo') == 'bar'
    assert get_local_filename('foo/bar', 'foo') == 'bar'

def test_remove_non_path_from_url():
    assert remove_non_path_from_url('https://foo/bar') == 'https://foo/bar'
    assert remove_non_path_from_url('https://foo//?bar#frag') == 'https://foo'
    assert remove_non_path_from_url('/path/to/foo#frag') == '/path/to/foo'

def test_nth_url_segment():
    assert nth_url_segment('') == ''
    assert nth_url_segment('foo') == 'foo'
    assert nth_url_segment('foo', n=-1) == 'foo'
    assert nth_url_segment('foo', n=-2) == ''
    assert nth_url_segment('foo/bar', n=-2) == 'foo'
    assert nth_url_segment('/baz/bar', n=-2) == 'baz'
    assert nth_url_segment('foo/') == 'foo'
    assert nth_url_segment('foo//?bar#frag') == 'foo'
    assert nth_url_segment('/path/to/foo#frag') == 'foo'
    assert nth_url_segment('/path/to/foo#frag', n=-2) == 'to'
    assert nth_url_segment('https://server/foo?xyz=zyx') == 'foo'

def test_parse_json_string_or_file():
    assert parse_json_string_or_file() == {}
    assert parse_json_string_or_file('') == {}
    assert parse_json_string_or_file(' ') == {}
    assert parse_json_string_or_file('{}') == {}
    assert parse_json_string_or_file('{"foo": 32}') == {'foo': 32}
    assert parse_json_string_or_file(
      '{"dpi": -1, "textequiv_level": "word", "overwrite_words": false, "raw_lines": false, "char_whitelist": "", "char_blacklist": "", "char_unblacklist": ""}') == \
      {"dpi": -1, "textequiv_level": "word", "overwrite_words": False, "raw_lines": False, "char_whitelist": "", "char_blacklist": "", "char_unblacklist": ""}

def test_parameter_file():
    """
    Verify that existing filenames get priority over valid JSON string interpretation
    """
    with TemporaryDirectory() as tempdir:
        paramfile = Path(tempdir, '{"foo":23}')  # XXX yes, the file is called '{"foo":23}'
        paramfile.write_text('{"bar": 42}')
        # /tmp/<var>/{"foo":23} -- exists, read file and parse as JSON
        assert parse_json_string_or_file(str(paramfile)) == {'bar': 42}
        # $PWD/{"foo":23} -- does not exist, parse as json
        assert parse_json_string_or_file(paramfile.name) == {'foo': 23}

def test_parameter_file_comments():
    with TemporaryDirectory() as tempdir:
        jsonpath = Path(tempdir, 'test.json')
        jsonpath.write_text("""\
                {
                    # Metasyntactical variables are rarely imaginative
                    "foo": 42,
                    # case in point:
                    "bar": 23
                }""")
        assert parse_json_string_or_file(str(jsonpath)) == {'foo': 42, 'bar': 23}

def test_parameters_invalid():
    with raises(ValueError, match='Not a valid JSON object'):
        parse_json_string_or_file('[]')
    with raises(ValueError, match='Error parsing'):
        parse_json_string_or_file('[}')

def test_mime_ext():
    assert MIME_TO_EXT['image/jp2'] == '.jp2'
    assert EXT_TO_MIME['.jp2'] == 'image/jp2'
    assert MIME_TO_PIL['image/jp2'] == 'JP2'
    assert PIL_TO_MIME['JP2'] == 'image/jp2'


def test_set_json_key_value_overrides():
    assert set_json_key_value_overrides({}, ('foo', 'true')) == {'foo': True}
    assert set_json_key_value_overrides({}, ('foo', 'false')) == {'foo': False}
    assert set_json_key_value_overrides({}, ('foo', '42')) == {'foo': 42}
    assert set_json_key_value_overrides({}, ('foo', '42.3')) == {'foo': 42.3}
    assert set_json_key_value_overrides({}, ('foo', '["one", 2, 3.33]')) == {'foo': ['one', 2, 3.33]}
    assert set_json_key_value_overrides({}, ('foo', '{"one": 2}')) == {'foo': {'one': 2}}
    assert set_json_key_value_overrides({}, ('foo', '"a string"')) == {'foo': 'a string'}
    assert set_json_key_value_overrides({}, ('foo', 'a string')) == {'foo': 'a string'}

def test_assert_file_grp_cardinality():
    with raises(AssertionError, match="Expected exactly 5 output file groups, but '.'FOO', 'BAR'.' has 2"):
        assert_file_grp_cardinality('FOO,BAR', 5)
    with raises(AssertionError, match="Expected exactly 1 output file group, but '.'FOO', 'BAR'.' has 2"):
        assert_file_grp_cardinality('FOO,BAR', 1)
    assert_file_grp_cardinality('FOO,BAR', 2)
    with raises(AssertionError, match="Expected exactly 1 output file group .foo bar., but '.'FOO', 'BAR'.' has 2"):
        assert_file_grp_cardinality('FOO,BAR', 1, 'foo bar')

def test_make_file_id_simple():
    f = create_ocrd_file('MAX', ID="MAX_0012")
    assert make_file_id(f, 'FOO') == 'FOO_0012'

def test_make_file_id_mets():
    mets = OcrdMets.empty_mets()
    for i in range(1, 10):
        mets.add_file('FOO', ID="FOO_%04d" % (i), mimetype="image/tiff", pageId='FOO_%04d' % i)
        mets.add_file('BAR', ID="BAR_%04d" % (i), mimetype="image/tiff", pageId='BAR_%04d' % i)
    assert make_file_id(mets.find_all_files(ID='BAR_0007')[0], 'FOO') == 'FOO_0007'
    f = mets.add_file('ABC', ID="BAR_42", mimetype="image/tiff")
    mets.remove_file(fileGrp='FOO')
    assert make_file_id(f, 'FOO') == 'FOO_BAR_42'
    mets.add_file('FOO', ID="FOO_0001", mimetype="image/tiff")

def test_make_file_id_570():
    """https://github.com/OCR-D/core/pull/570"""
    mets = OcrdMets.empty_mets()
    f = mets.add_file('GRP', ID='FOO_0001', pageId='phys0001')
    mets.add_file('GRP', ID='GRP2_0001', pageId='phys0002')
    assert make_file_id(f, 'GRP2') == 'GRP2_phys0001'

def test_make_file_id_605():
    """
    https://github.com/OCR-D/core/pull/605
    Also: Same fileGrp!
    """
    mets = OcrdMets.empty_mets()
    f = mets.add_file('GRP1', ID='FOO_0001', pageId='phys0001')
    f = mets.add_file('GRP2', ID='FOO_0002', pageId='phys0002')
    # NB: same fileGrp
    assert make_file_id(f, 'GRP2') == 'FOO_0002'
    assert make_file_id(f, 'GRP3') == 'GRP3_phys0002'

def test_make_file_id_744():
    """
    https://github.com/OCR-D/core/pull/744
    > Often file IDs have two numbers, one of which will clash. In that case only the numerical fallback works.
    """
    mets = OcrdMets.empty_mets()
    f = mets.add_file('GRP2', ID='img1796-97_00000024_img', pageId='phys0024')
    f = mets.add_file('GRP2', ID='img1796-97_00000025_img', pageId='phys0025')
    assert make_file_id(f, 'GRP3') == 'GRP3_phys0025'

def test_generate_range():
    assert generate_range('PHYS_0001', 'PHYS_0005') == ['PHYS_0001', 'PHYS_0002', 'PHYS_0003', 'PHYS_0004', 'PHYS_0005']
    with raises(ValueError, match='could not find numeric part'):
        assert generate_range('NONUMBER', 'ALSO_NONUMBER')
    with raises(ValueError, match='differ in their non-numeric part'):
        generate_range('PHYS_0001_123', 'PHYS_0010_123')
    with raises(ValueError, match='differ in their non-numeric part'):
        assert generate_range('1', 'PHYS_0005') == 0
    with raises(ValueError, match='differ in their non-numeric part'):
        assert generate_range('1', 'page 5') == 0
    with warns(UserWarning, match='same number'):
        assert generate_range('PHYS_0001_123', 'PHYS_0001_123') == ['PHYS_0001_123']

def test_safe_filename():
    assert safe_filename('Hello world,!') == 'Hello_world_'
    assert safe_filename(' Καλημέρα κόσμε,') == '_Καλημέρα_κόσμε_'
    assert safe_filename(':コンニチハ:') == '_コンニチハ_'

def test_partition_list():
    lst_10 = list(range(1, 11))
    assert partition_list(None, 1) == []
    assert partition_list([], 1) == []
    assert partition_list(lst_10, 1) == [lst_10]
    assert partition_list(lst_10, 3) == [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]
    assert partition_list(lst_10, 3, 1) == [[5, 6, 7]]
    assert partition_list(lst_10, 3, 0) == [[1, 2, 3, 4]]
    with raises(IndexError):
        partition_list(lst_10, chunks=4, chunk_index=5)
        partition_list(lst_10, chunks=5, chunk_index=5)
        partition_list(lst_10, chunks=5, chunk_index=6)
    with raises(ValueError):
        partition_list(lst_10, chunks=11)
    # odd prime number tests
    lst_13 = list(range(1, 14))
    assert partition_list(lst_13, chunks=2) == [[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13]]
    assert partition_list(lst_13, chunks=3) == [[1, 2, 3, 4, 5], [6, 7, 8, 9], [10, 11, 12, 13]]
    assert partition_list(lst_13, chunks=4) == [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12, 13]]
    assert partition_list(lst_13, chunks=4, chunk_index=1) == [[5, 6, 7]]

def test_sparkline():
    assert sparkline([5, 2, 3]) == '█▃▄'
    assert sparkline([1000, 1, 2222]) == '▃ █'
    assert sparkline([8, 7, 6, 5, 4, 3, 2, 1, 0]) == '█▇▆▅▄▃▂▁ '
    assert sparkline([-1, None, 'forty-two']) == ''


if __name__ == '__main__':
    main(__file__)
