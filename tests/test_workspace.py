# -*- coding: utf-8 -*-

from os import chdir, curdir, walk, stat, chmod, umask
import shutil
from stat import filemode
from os.path import join, exists, abspath, basename, dirname
from shutil import copyfile, copytree as copytree_, rmtree
from pathlib import Path
from gzip import open as gzip_open

from PIL import Image

import pytest

from tests.base import (
    assets,
    main
)

from ocrd_models import (
    OcrdFile,
    OcrdMets
)
from ocrd_models.ocrd_page import parseString
from ocrd_modelfactory import page_from_file
from ocrd.resolver import Resolver
from ocrd.workspace import Workspace


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
    workspace = resolver.workspace_from_nothing(directory=tmp_path)
    yield workspace


def test_workspace_add_file(plain_workspace):
    fpath = str(plain_workspace.directory / 'ID1.tif')

    # act
    plain_workspace.add_file(
        'GRP',
        ID='ID1',
        mimetype='image/tiff',
        content='CONTENT',
        pageId=None,
        local_filename=fpath
    )
    f = plain_workspace.mets.find_all_files()[0]

    # assert
    assert f.ID == 'ID1'
    assert f.mimetype == 'image/tiff'
    assert f.url == fpath
    assert f.local_filename == fpath
    assert exists(fpath)


def test_workspace_add_file_basename_no_content(plain_workspace):
    plain_workspace.add_file('GRP', ID='ID1', mimetype='image/tiff', pageId=None)
    f = next(plain_workspace.mets.find_files())

    # assert
    assert f.url == None


def test_workspace_add_file_binary_content(plain_workspace):
    fpath = join(plain_workspace.directory, 'subdir', 'ID1.tif')
    plain_workspace.add_file('GRP', ID='ID1', content=b'CONTENT', local_filename=fpath, url='http://foo/bar', pageId=None)

    # assert
    assert exists(fpath)


def test_workspacec_add_file_content_wo_local_filename(plain_workspace):
    # act
    with pytest.raises(Exception) as fn_exc:
        plain_workspace.add_file('GRP', ID='ID1', content=b'CONTENT', pageId='foo1234')

    assert "'content' was set but no 'local_filename'" in str(fn_exc.value)


def test_workspacec_add_file_content_wo_pageid(plain_workspace):
    # act
    with pytest.raises(ValueError) as val_err:
        plain_workspace.add_file('GRP', ID='ID1', content=b'CONTENT', local_filename='foo')

    assert "workspace.add_file must be passed a 'pageId' kwarg, even if it is None." in str(val_err.value)


def test_workspace_str(plain_workspace):

    # act
    plain_workspace.save_mets()
    plain_workspace.reload_mets()

    # assert
    ws_dir = plain_workspace.directory
    assert str(plain_workspace) == 'Workspace[directory=%s, baseurl=None, file_groups=[], files=[]]' % ws_dir


def test_workspace_backup(plain_workspace):

    # act
    plain_workspace.automatic_backup = True
    plain_workspace.save_mets()
    plain_workspace.reload_mets()

    # TODO
    # changed test semantics
    assert exists(join(plain_workspace.directory, '.backup'))


def _url_to_file(the_path):
    dummy_mets = OcrdMets.empty_mets()
    dummy_url = abspath(the_path)
    return dummy_mets.add_file('DEPRECATED', ID=Path(dummy_url).name, url=dummy_url)


def test_download_very_self_file(plain_workspace):

    # arrange with some dummy stuff
    the_file = _url_to_file(abspath(__file__))

    # act
    fn = plain_workspace.download_file(the_file)

    # assert
    assert fn, join('DEPRECATED', basename(__file__))


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
    assert "Already tried prepending baseurl '%s'" % str(tmp_path) in str(exc.value)


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
    assert str(f).endswith(join('OCR-D-IMG', '%s.tif' % SAMPLE_FILE_ID))
    assert Path(ws1.directory, f).exists()


def test_from_url_dst_dir_download(plain_workspace):
    """
    https://github.com/OCR-D/core/issues/319
    """
    ws_dir = join(plain_workspace.directory, 'non-existing-for-good-measure')
    # Create a relative path to trigger #319
    src_path = str(Path(assets.path_to('kant_aufklaerung_1784/data/mets.xml')).relative_to(Path.cwd()))
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

    # TODO check semantics - can a non-existend thing be removed?
    assert not sbb_data_workspace.remove_file('non-existing-id', force=True)
    # should also succeed
    sbb_data_workspace.overwrite_mode = True
    assert not sbb_data_workspace.remove_file('non-existing-id', force=False)


def test_remove_file_remote_not_available_raises_exception(plain_workspace):
    plain_workspace.add_file('IMG', ID='page1_img', mimetype='image/tiff', url='http://remote', pageId=None)
    with pytest.raises(Exception) as not_avail_exc:
        plain_workspace.remove_file('page1_img')

    assert "not locally available" in str(not_avail_exc.value)


def test_remove_file_remote(plain_workspace):

    # act
    plain_workspace.add_file('IMG', ID='page1_img', mimetype='image/tiff', url='http://remote', pageId=None)

    # must succeed because removal is enforced
    assert plain_workspace.remove_file('page1_img', force=True)

    # TODO check returned value
    # should also "succeed", because overwrite_mode is set which also sets 'force' to 'True'
    plain_workspace.overwrite_mode = True
    assert not plain_workspace.remove_file('page1_img')


def test_rename_file_group(tmp_path):
    # arrange
    copytree(assets.path_to('kant_aufklaerung_1784-page-region-line-word_glyph/data'), str(tmp_path))
    workspace = Workspace(Resolver(), directory=str(tmp_path))

    # before act
    # TODO clear semantics
    # requires rather odd additional path-setting because root path from
    # workspace is not propagated - works only if called inside workspace
    # which can be achieved with pushd_popd functionalities
    ocrd_file = next(workspace.mets.find_files(ID='OCR-D-GT-SEG-WORD_0001'))
    relative_name = ocrd_file.local_filename
    ocrd_file.local_filename = join(tmp_path, relative_name)
    pcgts_before = page_from_file(ocrd_file)
    # before assert
    assert pcgts_before.get_Page().imageFilename == 'OCR-D-IMG/OCR-D-IMG_0001.tif'

    # act
    workspace.rename_file_group('OCR-D-IMG', 'FOOBAR')
    next_ocrd_file = next(workspace.mets.find_files(ID='OCR-D-GT-SEG-WORD_0001'))
    next_ocrd_file.local_filename = join(tmp_path, relative_name)
    pcgts_after = page_from_file(next_ocrd_file)

    # assert
    assert pcgts_after.get_Page().imageFilename == 'FOOBAR/FOOBAR_0001.tif'
    assert Path(tmp_path / 'FOOBAR/FOOBAR_0001.tif').exists()
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
    added_res = plain_workspace.add_file('FOO', ID='foo', mimetype='foo/bar', local_filename='file.ext', content='foo', pageId=None).url
    # requires additional prepending of current path because not pushd_popd-magic at work
    added_path = Path(join(plain_workspace.directory, added_res))

    # assert
    assert added_path.exists()
    plain_workspace.remove_file_group('FOO', recursive=True)


@pytest.fixture(name='kant_complex_workspace')
def _fixture_kant_complex(tmp_path):
    copytree(assets.path_to('kant_aufklaerung_1784-complex/data'), str(tmp_path))
    yield Workspace(Resolver, directory=tmp_path)


def test_remove_file_page_recursive(kant_complex_workspace):
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
    f1 = plain_workspace.add_file('IMG', ID='page1_img', mimetype='image/tiff', local_filename='test.tif', content='', pageId=None)
    f2 = plain_workspace.add_file('GT', ID='page1_gt', mimetype='text/xml', local_filename='test.xml', content='', pageId=None)

    assert f1.url == 'test.tif'
    assert f2.url == 'test.xml'

    # these should be no-ops
    plain_workspace.download_file(f1)
    plain_workspace.download_file(f2)

    assert f1.url == 'test.tif'
    assert f2.url == 'test.xml'


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
    with open(join(str(workspace_sample_features.directory), 'image_features.page.xml'), 'r') as f:
        pcgts = parseString(f.read().encode('utf8'))

    # richest feature set is not last:
    _, info, _ = workspace_sample_features.image_from_page(pcgts.get_Page(), page_id='page1', feature_selector='dewarped')
    # recropped because foo4 contains cropped+deskewed but not recropped yet:
    assert info['features'] == 'cropped,dewarped,binarized,despeckled,deskewed,recropped'
    # richest feature set is also last:
    _, info, _ = workspace_sample_features.image_from_page(pcgts.get_Page(), page_id='page1', feature_selector='dewarped', feature_filter='binarized')
    # no deskewing here, thus no recropping:
    assert info['features'] == 'cropped,dewarped,despeckled'


def test_downsample_16bit_image(plain_workspace):
    # arrange image
    img_path = join(plain_workspace.directory, '16bit.tif')
    with gzip_open(join(dirname(__file__), 'data/OCR-D-IMG_APBB_Mitteilungen_62.0002.tif.gz'), 'rb') as gzip_in:
        with open(img_path, 'wb') as tif_out:
            tif_out.write(gzip_in.read())

    # act
    plain_workspace.add_file('IMG', ID='foo', url=img_path, mimetype='image/tiff', pageId=None)

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


def test_merge(tmp_path):

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

    # act
    ws1.merge(ws2)

    # assert
    assert len(ws1.mets.find_all_files()) == 41
    assert exists(join(dst_path1, 'OCR-D-IMG/FILE_0001_IMAGE.tif'))


if __name__ == '__main__':
    main(__file__)
