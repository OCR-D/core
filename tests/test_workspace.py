# -*- coding: utf-8 -*-

from os import chdir, curdir, walk, stat, chmod, umask
import shutil
import logging
from stat import filemode
from os.path import join, exists, abspath, basename, dirname
from shutil import copyfile, copytree as copytree_, rmtree
from pathlib import Path
from gzip import open as gzip_open

from PIL import Image
import numpy as np

import pytest

from tests.base import (
    assets,
    main,
    FIFOIO
)

from ocrd_models import (
    OcrdFile,
    OcrdMets
)
from ocrd_models.ocrd_page import parseString
from ocrd_models.ocrd_page import TextRegionType, CoordsType, AlternativeImageType
from ocrd_utils import polygon_mask, xywh_from_polygon, bbox_from_polygon, points_from_polygon
from ocrd_modelfactory import page_from_file
from ocrd.resolver import Resolver
from ocrd.workspace import Workspace
from ocrd.workspace_backup import WorkspaceBackupManager
from ocrd_validators import WorkspaceValidator

TMP_FOLDER = '/tmp/test-core-workspace'
SRC_METS = assets.path_to('kant_aufklaerung_1784/data/mets.xml')

SAMPLE_FILE_FILEGRP = 'OCR-D-IMG'
SAMPLE_FILE_ID = 'INPUT_0017'
SAMPLE_FILE_URL = join(SAMPLE_FILE_FILEGRP, '%s.tif' % SAMPLE_FILE_ID)


def copytree(src, dst, *args, **kwargs):
    rmtree(dst)
    copytree_(src, dst, *args, **kwargs)


def count_files(d): return sum(len(files) for _, _, files in walk(d))


@pytest.fixture(name='plain_workspace')
def _fixture_plain_workspace(tmp_path):
    resolver = Resolver()
    ws = resolver.workspace_from_nothing(directory=tmp_path)
    prev_dir = abspath(curdir)
    chdir(tmp_path)
    yield ws
    chdir(prev_dir)

def test_workspace_add_file(plain_workspace):
    fpath = plain_workspace.directory / 'ID1.tif'

    # act
    plain_workspace.add_file(
        'GRP',
        file_id='ID1',
        mimetype='image/tiff',
        content='CONTENT',
        page_id=None,
        local_filename=fpath
    )
    f = plain_workspace.mets.find_all_files()[0]

    # assert
    assert f.ID == 'ID1'
    assert f.mimetype == 'image/tiff'
    assert not f.url
    assert f.local_filename == str(fpath)
    assert Path(f.local_filename).exists()


def test_workspace_add_file_overwrite(plain_workspace):
    fpath = plain_workspace.directory / 'ID1.tif'

    # act
    plain_workspace.add_file('GRP', file_id='ID1', mimetype='image/tiff', content='CONTENT', page_id='phys1', local_filename=fpath)
    with pytest.raises(FileExistsError) as fn_exc:
        plain_workspace.add_file('GRP', file_id='ID1', mimetype='image/tiff', content='CONTENT', page_id=None, local_filename=fpath)
        assert str(fn_exc.value) == "File with file_id='ID1' already exists"
    with pytest.raises(FileExistsError) as fn_exc:
        plain_workspace.add_file('GRP', file_id='ID1', mimetype='image/tiff', content='CONTENT', page_id='phys2', local_filename=fpath, force=True)
        assert 'cannot mitigate' in str(fn_exc.value)
    plain_workspace.add_file('GRP', file_id='ID1', mimetype='image/tiff', content='CONTENT2', page_id='phys1', local_filename=fpath, force=True)

    f = plain_workspace.mets.find_all_files()[0]
    assert f.ID == 'ID1'
    assert f.mimetype == 'image/tiff'
    assert not f.url
    assert f.local_filename == str(fpath)
    assert f.pageId == 'phys1'
    assert fpath.exists()


def test_workspace_add_file_basename_no_content(plain_workspace):
    plain_workspace.add_file('GRP', file_id='ID1', mimetype='image/tiff', page_id=None)
    f = next(plain_workspace.mets.find_files())
    assert f.url == ''

def test_workspace_add_file_binary_content(plain_workspace):
    fpath = join(plain_workspace.directory, 'subdir', 'ID1.tif')
    plain_workspace.add_file('GRP', file_id='ID1', content=b'CONTENT', local_filename=fpath, url='http://foo/bar', page_id=None)

    # assert
    assert exists(fpath)


def test_workspacec_add_file_content_wo_local_filename(plain_workspace):
    # act
    with pytest.raises(Exception) as fn_exc:
        plain_workspace.add_file('GRP', file_id='ID1', content=b'CONTENT', page_id='foo1234')

    assert "'content' was set but no 'local_filename'" in str(fn_exc.value)


def test_workspacec_add_file_content_wo_pageid(plain_workspace):
    # act
    with pytest.raises(ValueError) as val_err:
        plain_workspace.add_file('GRP', file_id='ID1', content=b'CONTENT', local_filename='foo')

    assert "workspace.add_file must be passed a 'page_id' kwarg, even if it is None." in str(val_err.value)


def test_workspace_str(plain_workspace):

    # act
    plain_workspace.save_mets()
    plain_workspace.reload_mets()

    # assert
    ws_dir = plain_workspace.directory
    assert str(plain_workspace) == 'Workspace[remote=False, directory=%s, baseurl=None, file_groups=[], files=[]]' % ws_dir


def test_workspace_backup(plain_workspace):

    # act
    plain_workspace.automatic_backup = WorkspaceBackupManager(plain_workspace)
    plain_workspace.save_mets()
    plain_workspace.reload_mets()

    # TODO
    # changed test semantics
    assert exists(join(plain_workspace.directory, '.backup'))


def _url_to_file(the_path):
    dummy_mets = OcrdMets.empty_mets()
    dummy_url = abspath(the_path)
    return dummy_mets.add_file('TESTGRP', ID=Path(dummy_url).name, url=dummy_url)


def test_download_very_self_file(plain_workspace):
    the_file = _url_to_file(abspath(__file__))
    fn = plain_workspace.download_file(the_file)
    assert fn, join('TESTGRP', basename(__file__))
    assert fn == the_file


def test_download_url_without_baseurl_raises_exception(tmp_path):
    # arrange
    dst_mets = join(tmp_path, 'mets.xml')
    copyfile(SRC_METS, dst_mets)
    ws1 = Resolver().workspace_from_url(dst_mets)
    the_file = _url_to_file(SAMPLE_FILE_URL)

    # act
    with pytest.raises(Exception) as exc:
        ws1.download_file(the_file)

    # assert exception message contents
    assert "File path passed as 'url' to download_to_directory does not exist:" in str(exc.value)


def test_download_url_with_baseurl(tmp_path):
    # arrange
    dst_mets = join(tmp_path, 'mets.xml')
    copyfile(SRC_METS, dst_mets)
    tif_dir = tmp_path / 'OCR-D-IMG'
    tif_dir.mkdir()
    dst_tif = join(tmp_path, SAMPLE_FILE_URL)
    copyfile(join(dirname(SRC_METS), SAMPLE_FILE_URL), dst_tif)
    ws1 = Resolver().workspace_from_url(dst_mets, src_baseurl=dirname(SRC_METS))
    the_file = _url_to_file(dst_tif)

    # act
    # TODO
    # semantics changed from .download_url to .download_file
    # and from context path 'DEPRECATED' to 'OCR-D-IMG'
    f = Path(ws1.download_file(the_file).local_filename)

    # assert
    assert f.name == f'{SAMPLE_FILE_ID}.tif'
    assert f.parent.name == 'TESTGRP'
    assert Path(ws1.directory, f).exists()


def test_from_url_dst_dir_download(plain_workspace):
    """
    https://github.com/OCR-D/core/issues/319
    """
    ws_dir = join(plain_workspace.directory, 'non-existing-for-good-measure')
    # Create a relative path to trigger #319
    src_path = str(Path(assets.path_to('kant_aufklaerung_1784/data/mets.xml')))
    plain_workspace.resolver.workspace_from_url(src_path, dst_dir=ws_dir, download=True)

    # assert
    assert Path(ws_dir, 'mets.xml').exists()  # sanity check, mets.xml must exist
    assert Path(ws_dir, 'OCR-D-GT-PAGE/PAGE_0017_PAGE.xml').exists()


def test_superfluous_copies_in_ws_dir(tmp_path):
    """
    https://github.com/OCR-D/core/issues/227
    """
    # arrange
    src_path = assets.path_to('SBB0000F29300010000/data/mets_one_file.xml')
    dst_path = join(tmp_path, 'mets.xml')
    copyfile(src_path, dst_path)
    ws1 = Workspace(Resolver(), tmp_path)

    # assert directory files
    assert count_files(tmp_path) == 1

    # act
    for file in ws1.mets.find_all_files():
        ws1.download_file(file)

    # assert
    assert count_files(tmp_path) == 2
    assert exists(join(tmp_path, 'OCR-D-IMG/FILE_0005_IMAGE.tif'))


@pytest.fixture(name='sbb_data_tmp')
def _fixture_sbb_data_tmp(tmp_path):
    copytree(assets.path_to('SBB0000F29300010000/data'), str(tmp_path))
    yield str(tmp_path)


@pytest.fixture(name='sbb_data_workspace')
def _fixture_sbb_data(sbb_data_tmp):
    resolver = Resolver()
    workspace = Workspace(resolver, directory=sbb_data_tmp)
    yield workspace


def test_remove_file_not_existing_raises_error(sbb_data_workspace):

    # act
    with pytest.raises(FileNotFoundError) as fnf_err:
        sbb_data_workspace.remove_file('non-existing-id')

    # assert
    assert "not found" in str(fnf_err.value)


def test_remove_file_force(sbb_data_workspace):
    """Enforce removal of non-existing-id doesn't yield any error
    but also returns no ocrd-file identifier"""

    # TODO check semantics - can a non-existent thing be removed?
    assert not sbb_data_workspace.remove_file('non-existing-id', force=True)
    # should also succeed
    sbb_data_workspace.overwrite_mode = True
    assert not sbb_data_workspace.remove_file('non-existing-id', force=False)


def test_remove_file_remote_not_available_raises_exception(plain_workspace):
    plain_workspace.add_file('IMG', file_id='page1_img', mimetype='image/tiff', url='http://remote', page_id=None)
    with pytest.raises(Exception) as not_avail_exc:
        plain_workspace.remove_file('page1_img')

    assert "not locally available" in str(not_avail_exc.value)


def test_remove_file_remote(plain_workspace):

    # act
    plain_workspace.add_file('IMG', file_id='page1_img', mimetype='image/tiff', url='http://remote', page_id=None)

    # must succeed because removal is enforced
    assert plain_workspace.remove_file('page1_img', force=True)

    # TODO check returned value
    # should also "succeed", because overwrite_mode is set which also sets 'force' to 'True'
    plain_workspace.overwrite_mode = True
    assert not plain_workspace.remove_file('page1_img')


def test_rename_file_group(tmp_path):
    # arrange
    copytree(assets.path_to('kant_aufklaerung_1784-page-region-line-word_glyph/data'), tmp_path)
    workspace = Workspace(Resolver(), directory=tmp_path)

    # before act
    # TODO clear semantics
    # requires rather odd additional path-setting because root path from
    # workspace is not propagated - works only if called inside workspace
    # which can be achieved with pushd_popd functionalities
    ocrd_file = next(workspace.mets.find_files(ID='OCR-D-GT-SEG-WORD_0001'))
    relative_name = ocrd_file.local_filename
    ocrd_file.local_filename = tmp_path / relative_name
    pcgts_before = page_from_file(ocrd_file)
    # before assert
    assert pcgts_before.get_Page().imageFilename == 'OCR-D-IMG/INPUT_0017.tif'

    # act
    workspace.rename_file_group('OCR-D-IMG', 'FOOBAR')
    next_ocrd_file = next(workspace.mets.find_files(ID='OCR-D-GT-SEG-WORD_0001'))
    next_ocrd_file.local_filename = str(tmp_path / relative_name)
    pcgts_after = page_from_file(next_ocrd_file)

    # assert
    assert pcgts_after.get_Page().imageFilename == 'FOOBAR/INPUT_0017.tif'
    assert Path(tmp_path / 'FOOBAR/INPUT_0017.tif').exists()
    assert not Path('OCR-D-IMG/OCR-D-IMG_0001.tif').exists()
    assert workspace.mets.get_physical_pages(for_fileIds=['OCR-D-IMG_0001']) == [None]
    assert workspace.mets.get_physical_pages(for_fileIds=['FOOBAR_0001']) == ['phys_0001']


def test_remove_file_group_invalid_raises_exception(sbb_data_workspace):
    with pytest.raises(Exception) as no_fg_exc:
        # should fail
        sbb_data_workspace.remove_file_group('I DO NOT EXIST')
    assert "No such fileGrp" in str(no_fg_exc.value)


def test_remove_file_group_force(sbb_data_workspace):

    # TODO
    # check function and tests semantics
    # should succeed
    assert not sbb_data_workspace.remove_file_group('I DO NOT EXIST', force=True)
    # should also succeed
    sbb_data_workspace.overwrite_mode = True
    assert not sbb_data_workspace.remove_file_group('I DO NOT EXIST', force=False)


def test_remove_file_group_rmdir(sbb_data_tmp, sbb_data_workspace):
    assert exists(join(sbb_data_tmp, 'OCR-D-IMG'))
    sbb_data_workspace.remove_file_group('OCR-D-IMG', recursive=True)
    assert not exists(join(sbb_data_tmp, 'OCR-D-IMG'))


def test_remove_file_group_flat(plain_workspace):
    """
    https://github.com/OCR-D/core/issues/728
    """

    # act
    added_res = plain_workspace.add_file('FOO', file_id='foo', mimetype='foo/bar', local_filename='file.ext', content='foo', page_id=None).local_filename
    # requires additional prepending of current path because not pushd_popd-magic at work
    added_filename = join(plain_workspace.directory, added_res)

    # assert
    assert Path(added_filename).exists()
    plain_workspace.remove_file_group('FOO', recursive=True)


@pytest.fixture(name='kant_complex_workspace')
def _fixture_kant_complex(tmp_path):
    copytree(assets.path_to('kant_aufklaerung_1784-complex/data'), str(tmp_path))
    yield Workspace(Resolver, directory=tmp_path)


def test_remove_file_page_recursive0(kant_complex_workspace):
    assert len(kant_complex_workspace.mets.find_all_files()) == 119
    kant_complex_workspace.remove_file('OCR-D-OCR-OCRO-fraktur-SEG-LINE-tesseract-ocropy-DEWARP_0001', page_recursive=True, page_same_group=False, keep_file=True)
    assert len(kant_complex_workspace.mets.find_all_files()) == 83
    kant_complex_workspace.remove_file('PAGE_0017_ALTO', page_recursive=True)


def test_remove_file_page_recursive_keep_file(kant_complex_workspace):
    before = count_files(kant_complex_workspace.directory)
    kant_complex_workspace.remove_file('OCR-D-IMG-BINPAGE-sauvola_0001', page_recursive=True, page_same_group=False, force=True)
    after = count_files(kant_complex_workspace.directory)
    assert after == (before - 2), '2 files deleted'


def test_remove_file_page_recursive_same_group(kant_complex_workspace):
    before = count_files(kant_complex_workspace.directory)
    kant_complex_workspace.remove_file('OCR-D-IMG-BINPAGE-sauvola_0001', page_recursive=True, page_same_group=True, force=False)
    after = count_files(kant_complex_workspace.directory)
    assert after == before - 1, '1 file deleted'


def test_download_to_directory_from_workspace_download_file(plain_workspace):
    """
    https://github.com/OCR-D/core/issues/342
    """
    f1 = plain_workspace.add_file('IMG', file_id='page1_img', mimetype='image/tiff', local_filename='test.tif', content='', page_id=None)
    f2 = plain_workspace.add_file('GT', file_id='page1_gt', mimetype='text/xml', local_filename='test.xml', content='', page_id=None)

    assert not f1.url
    assert not f2.url

    # these should be no-ops
    plain_workspace.download_file(f1)
    plain_workspace.download_file(f2)

    assert f1.local_filename == 'test.tif'
    assert f2.local_filename == 'test.xml'


def test_save_image_file_invalid_mimetype_raises_exception(plain_workspace):
    img = Image.new('RGB', (1000, 1000))

    # act raise
    with pytest.raises(KeyError) as key_exc:
        plain_workspace.save_image_file(img, 'page1_img', 'IMG', 'page1', 'ceci/nest/pas/une/mimetype')

    assert "'ceci/nest/pas/une/mimetype'" == str(key_exc.value)


def test_save_image_file(plain_workspace):

    # arrange
    img = Image.new('RGB', (1000, 1000))

    # act
    assert plain_workspace.save_image_file(img, 'page1_img', 'IMG', 'page1', 'image/jpeg')
    assert exists(join(plain_workspace.directory, 'IMG', 'page1_img.jpg'))
    # should succeed
    assert plain_workspace.save_image_file(img, 'page1_img', 'IMG', 'page1', 'image/jpeg', force=True)
    # should also succeed
    plain_workspace.overwrite_mode = True
    assert plain_workspace.save_image_file(img, 'page1_img', 'IMG', 'page1', 'image/jpeg')


@pytest.fixture(name='workspace_kant_aufklaerung')
def _fixture_workspace_kant_aufklaerung(tmp_path):
    copytree(assets.path_to('kant_aufklaerung_1784/data/'), str(tmp_path))
    resolver = Resolver()
    ws = resolver.workspace_from_url(join(tmp_path, 'mets.xml'), src_baseurl=tmp_path)
    prev_dir = abspath(curdir)
    chdir(tmp_path)
    yield ws
    chdir(prev_dir)


def test_resolve_image_exif(workspace_kant_aufklaerung):

    tif_path = 'OCR-D-IMG/INPUT_0017.tif'

    # act
    exif = workspace_kant_aufklaerung.resolve_image_exif(tif_path)

    # assert
    assert exif.compression == 'jpeg'
    assert exif.width == 1457


def test_resolve_image_as_pil(workspace_kant_aufklaerung):
    img = workspace_kant_aufklaerung._resolve_image_as_pil('OCR-D-IMG/INPUT_0017.tif')
    assert img.width == 1457
    img = workspace_kant_aufklaerung._resolve_image_as_pil('OCR-D-IMG/INPUT_0017.tif', coords=([100, 100], [50, 50]))
    assert img.width == 50


@pytest.fixture(name='workspace_gutachten_data')
def _fixture_workspace_gutachten_data(tmp_path):
    copytree(assets.path_to('gutachten/data'), str(tmp_path))
    resolver = Resolver()
    ws = resolver.workspace_from_url(join(str(tmp_path), 'mets.xml'))
    prev_path = abspath(curdir)
    chdir(tmp_path)
    yield ws
    chdir(prev_path)


def test_image_from_page_basic(workspace_gutachten_data):
    # arrange
    with open(assets.path_to('gutachten/data/TEMP1/PAGE_TEMP1.xml'), 'r') as f:
        pcgts = parseString(f.read().encode('utf8'), silence=True)

    # act + assert
    _, info, _ = workspace_gutachten_data.image_from_page(pcgts.get_Page(), page_id='PHYS_0017', feature_selector='clipped', feature_filter='cropped')
    assert info['features'] == 'binarized,clipped'
    _, info, _ = workspace_gutachten_data.image_from_page(pcgts.get_Page(), page_id='PHYS_0017')
    assert info['features'] == 'binarized,clipped'


@pytest.fixture(name='workspace_sample_features')
def _fixture_workspace_sample_features(tmp_path):
    copytree('tests/data/sample-features', str(tmp_path))
    resolver = Resolver()
    ws = resolver.workspace_from_url(join(str(tmp_path), 'mets.xml'))
    prev_path = abspath(curdir)
    chdir(tmp_path)
    yield ws
    chdir(prev_path)


def test_image_feature_selectoro(workspace_sample_features):
    # arrange
    with open(Path(workspace_sample_features.directory) / 'image_features.page.xml', 'r', encoding='utf-8') as f:
        pcgts = parseString(f.read().encode('utf-8'))

    # richest feature set is not last:
    _, info, _ = workspace_sample_features.image_from_page(pcgts.get_Page(), page_id='page1', feature_selector='dewarped')
    # recropped because foo4 contains cropped+deskewed but not recropped yet:
    assert info['features'] == 'cropped,dewarped,binarized,despeckled,deskewed'
    # richest feature set is also last:
    _, info, _ = workspace_sample_features.image_from_page(pcgts.get_Page(), page_id='page1', feature_selector='dewarped', feature_filter='binarized')
    # no deskewing here, thus no recropping:
    assert info['features'] == 'cropped,dewarped,despeckled'

def test_deskewing(plain_workspace):
    #from ocrd_utils import initLogging, setOverrideLogLevel
    #setOverrideLogLevel('DEBUG')
    size = (3000, 4000)
    poly = [[1403, 2573], [1560, 2573], [1560, 2598], [2311, 2598], [2311, 2757],
            [2220, 2757], [2220, 2798], [2311, 2798], [2311, 2908], [1403, 2908]]
    xywh = xywh_from_polygon(poly)
    bbox = bbox_from_polygon(poly)
    skew = 4.625
    image = Image.new('L', size)
    image = polygon_mask(image, poly)
    #image.show(title='image')
    pixels = np.count_nonzero(np.array(image) > 0)
    name = 'foo0'
    assert plain_workspace.save_image_file(image, name, 'IMG')
    pcgts = page_from_file(next(plain_workspace.mets.find_files(ID=name)))
    page = pcgts.get_Page()
    region = TextRegionType(id='nonrect',
                            Coords=CoordsType(points=points_from_polygon(poly)),
                            orientation=-skew)
    page.add_TextRegion(region)
    page_image, page_coords, _ = plain_workspace.image_from_page(page, '')
    #page_image.show(title='page_image')
    assert list(image.getdata()) == list(page_image.getdata())
    assert np.all(page_coords['transform'] == np.eye(3))
    reg_image, reg_coords = plain_workspace.image_from_segment(region, page_image, page_coords,
                                                               feature_filter='deskewed', fill=0)
    assert list(image.crop(bbox).getdata()) == list(reg_image.getdata())
    assert reg_image.width == xywh['w'] == 908
    assert reg_image.height == xywh['h'] == 335
    assert reg_coords['transform'][0, 2] == -xywh['x']
    assert reg_coords['transform'][1, 2] == -xywh['y']
    # same fg after cropping to minimal bbox
    reg_pixels = np.count_nonzero(np.array(reg_image) > 0)
    assert pixels == reg_pixels
    # now with deskewing (test for size after recropping)
    reg_image, reg_coords = plain_workspace.image_from_segment(region, page_image, page_coords, fill=0)
    #reg_image.show(title='reg_image')
    assert reg_image.width == 932 > xywh['w']
    assert reg_image.height == 382 > xywh['h']
    assert reg_coords['transform'][0, 1] != 0
    assert reg_coords['transform'][1, 0] != 0
    assert 'deskewed' in reg_coords['features']
    # same fg after cropping to minimal bbox (roughly - due to aliasing)
    reg_pixels = np.count_nonzero(np.array(reg_image) > 0)
    assert np.abs(pixels - reg_pixels) / pixels < 0.005
    reg_array = np.array(reg_image) > 0
    # now via AlternativeImage
    path = plain_workspace.save_image_file(reg_image, region.id + '_img', 'IMG')
    region.add_AlternativeImage(AlternativeImageType(filename=path, comments=reg_coords['features']))
    logger_capture = FIFOIO(256)
    logger_handler = logging.StreamHandler(logger_capture)
    #logger_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
    logger = logging.getLogger('ocrd.utils.crop_image')
    logger.addHandler(logger_handler)
    reg_image2, reg_coords2 = plain_workspace.image_from_segment(region, page_image, page_coords, fill=0)
    #reg_image2.show(title='reg_image2')
    logger_output = logger_capture.getvalue()
    logger_capture.close()
    assert logger_output == ''
    assert reg_image2.width == reg_image.width
    assert reg_image2.height == reg_image.height
    assert np.allclose(reg_coords2['transform'], reg_coords['transform'])
    assert reg_coords2['features'] == reg_coords['features']
    # same fg after cropping to minimal bbox (roughly - due to aliasing)
    reg_pixels2 = np.count_nonzero(np.array(reg_image) > 0)
    assert reg_pixels2 == reg_pixels
    reg_array2 = np.array(reg_image2) > 0
    assert 0.98 < np.sum(reg_array == reg_array2) / reg_array.size <= 1.0

def test_downsample_16bit_image(plain_workspace):
    # arrange image
    img_path = Path(plain_workspace.directory, '16bit.tif')
    with gzip_open(Path(__file__).parent / 'data/OCR-D-IMG_APBB_Mitteilungen_62.0002.tif.gz', 'rb') as gzip_in:
        with open(img_path, 'wb') as tif_out:
            tif_out.write(gzip_in.read())

    # act
    plain_workspace.add_file('IMG', file_id='foo', local_filename=img_path, mimetype='image/tiff', page_id=None)

    # assert
    pil_before = Image.open(img_path)
    assert pil_before.mode == 'I;16'
    pil_after = plain_workspace._resolve_image_as_pil(img_path)
    assert pil_after.mode == 'L'


def test_mets_permissions(plain_workspace):
    plain_workspace.save_mets()
    mets_path = join(plain_workspace.directory, 'mets.xml')
    mask = umask(0)
    umask(mask)
    assert (stat(mets_path).st_mode) == 0o100664 & ~mask
    chmod(mets_path, 0o777)
    plain_workspace.save_mets()
    assert filemode(stat(mets_path).st_mode) == '-rwxrwxrwx'


def test_merge0(tmp_path):

    # arrange
    dst_path1 = tmp_path / 'kant_aufklaerung'
    dst_path1.mkdir()
    dst_path2 = tmp_path / 'sbb'
    dst_path2.mkdir()
    copytree(assets.path_to('kant_aufklaerung_1784/data'), dst_path1)
    copytree(assets.path_to('SBB0000F29300010000/data'), dst_path2)

    ws1 = Workspace(Resolver(), dst_path1)
    ws2 = Workspace(Resolver(), dst_path2)

    # assert number of files before
    assert len(ws1.mets.find_all_files()) == 6
    assert len(ws2.mets.find_all_files()) == 35

    # act
    ws1.merge(ws2, overwrite=True)

    # assert
    assert len(ws1.mets.find_all_files()) == 41
    assert exists(join(dst_path1, 'OCR-D-IMG/INPUT_0017.tif'))

def test_merge_no_copy_files(tmp_path):

    # arrange
    dst_path1 = tmp_path / 'ws1'
    dst_path1.mkdir()
    dst_path2 = dst_path1 / 'ws2'
    dst_path2.mkdir()

    ws1 = Resolver().workspace_from_nothing(directory=dst_path1)
    ws2 = Resolver().workspace_from_nothing(directory=dst_path2)

    ws2.add_file('GRP2', page_id='p01', mimetype='text/plain', file_id='f1', local_filename='GRP2/f1', content='ws2')

    ws1.merge(ws2, copy_files=False, fileId_mapping={'f1': 'f1_copy_files'})

    assert next(ws1.mets.find_files(ID='f1_copy_files')).local_filename == 'ws2/GRP2/f1'

    with pytest.raises(FileExistsError):
        ws1.merge(ws2, copy_files=True, fileId_mapping={'f1': 'f1_copy_files'})
    ws1.merge(ws2, copy_files=True, fileId_mapping={'f1': 'f1_copy_files'}, force=True)
    assert next(ws1.mets.find_files(ID='f1_copy_files')).local_filename == 'GRP2/f1'

def test_merge_overwrite(tmp_path):
    # arrange
    dst_path1 = tmp_path / 'ws1'
    dst_path1.mkdir()
    dst_path2 = dst_path1 / 'ws2'
    dst_path2.mkdir()

    ws1 = Resolver().workspace_from_nothing(directory=dst_path1)
    ws2 = Resolver().workspace_from_nothing(directory=dst_path2)

    with pytest.raises(Exception) as exc:
        ws1.add_file('X', page_id='X', mimetype='X', file_id='id123', local_filename='X/X', content='ws1')
        ws2.add_file('X', page_id='X', mimetype='X', file_id='id456', local_filename='X/X', content='ws2')
        ws1.merge(ws2)
        assert "would overwrite" == str(exc.value)

def test_merge_with_filter(plain_workspace, tmp_path):
    # arrange
    page_id1, file_id1, file_grp1 = 'page1', 'ID1', 'GRP1'
    plain_workspace.add_file(file_grp1, file_id='ID1', mimetype='image/tiff', page_id='page1')

    dst_path2 = tmp_path / 'foo'
    resolver = Resolver()
    ws2 = resolver.workspace_from_nothing(directory=dst_path2)
    page_id2, file_id2, file_grp2 = 'page2', 'ID2', 'GRP2'
    ws2.add_file('GRP2', file_id=file_id2, mimetype='image/tiff', page_id=page_id2, url='bar')
    ws2.add_file('GRP2', file_id='ID2-2', mimetype='image/tiff', page_id='page3', url='bar')

    # act
    plain_workspace.merge(ws2, copy_files=False, page_id=page_id2, file_id=file_id2,
                          file_grp=file_grp2, filegrp_mapping={file_grp2: file_grp1})

    # assert:
    files = list(plain_workspace.find_files())
    assert len(files) == 2

    for f in files:
        assert f.fileGrp == file_grp1
        assert f.pageId in [page_id1, page_id2]
        assert f.ID in [file_id1, file_id2]

def test_merge_force(plain_workspace, tmp_path):
    resolver = Resolver()

    # target ws
    page_id1, file_id1, file_grp1 = 'page1', 'ID1', 'GRP1'
    plain_workspace.add_file(file_grp1, file_id=file_id1, mimetype='image/tiff', page_id=page_id1)

    # source ws
    dst_path2 = tmp_path / 'foo'
    ws2 = resolver.workspace_from_nothing(directory=dst_path2)
    page_id2, file_id2, file_grp2 = 'page1', 'ID1', 'GRP1'
    ws2.add_file(file_grp2, file_id=file_id2, mimetype='image/tiff', page_id=page_id2, url='bar')

    # fails because force is false
    with pytest.raises(Exception) as fn_exc:
        plain_workspace.merge(ws2, force=False)

    # works because force overrides ID clash
    plain_workspace.merge(ws2, force=True)

    files = list(plain_workspace.find_files())
    assert len(files) == 1

@pytest.fixture(name='workspace_metsDocumentID')
def _fixture_metsDocumentID(tmp_path):
    resolver = Resolver()
    mets_content = (Path(__file__).parent / "data/mets-with-metsDocumentID.xml").read_text()
    with open(tmp_path / 'mets.xml', 'w', encoding='utf-8') as f:
        f.write(mets_content)
    yield Workspace(Resolver, directory=tmp_path)

def test_agent_before_metsDocumentID(workspace_metsDocumentID):
    report = WorkspaceValidator.validate(Resolver(), mets_url=workspace_metsDocumentID.mets_target)
    assert report.is_valid
    workspace_metsDocumentID.mets.add_agent('foo bar v0.0.1', 'OTHER', 'OTHER', 'OTHER')
    workspace_metsDocumentID.save_mets()
    report = WorkspaceValidator.validate(Resolver(), mets_url=workspace_metsDocumentID.mets_target)
    print(report.errors)
    assert report.is_valid

if __name__ == '__main__':
    main(__file__)
