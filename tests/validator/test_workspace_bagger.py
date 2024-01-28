from os import makedirs
from os.path import abspath, exists, join
from pathlib import Path
from shutil import copytree, make_archive, move, rmtree
from tempfile import mkdtemp

from bagit import Bag, _load_tag_file
from pytest import fixture, raises

from ocrd.resolver import Resolver
from ocrd.workspace import Workspace
from ocrd.workspace_bagger import BACKUPDIR, WorkspaceBagger
from ocrd_utils import initLogging, pushd_popd, unzip_file_to_dir
from tests.base import (  # pylint: disable=import-error,no-name-in-module
    TestCase, assets, main)

README_FILE = abspath('README.md')

@fixture(name='bagger_fixture')
def _bagger_fixture(tmpdir):
    if exists(BACKUPDIR):
        rmtree(BACKUPDIR)
    makedirs(BACKUPDIR)
    resolver = Resolver()
    bagdir = join(tmpdir, 'bag')
    copytree(assets.path_to('kant_aufklaerung_1784'), bagdir)
    workspace_dir = join(bagdir, 'data')
    workspace = Workspace(resolver, directory=workspace_dir)
    bagger = WorkspaceBagger(resolver)
    yield bagger, workspace, bagdir, tmpdir
    rmtree(bagdir)

def test_bag_zip_and_spill(bagger_fixture):
    bagger, workspace, _, tempdir = bagger_fixture
    workspace.mets.find_all_files(ID='INPUT_0017')[0].url = 'bad-scheme://foo'
    workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://ocr-d.de'
    bagger.bag(workspace, 'kant_aufklaerung_1784', skip_zip=False, dest=join(tempdir, 'out.ocrd.zip'))
    bagger.spill(join(tempdir, 'out.ocrd.zip'), join(tempdir, 'out'))

def test_bag_zip_and_spill_wo_dest(bagger_fixture):
    bagger, workspace, _, tempdir = bagger_fixture
    bagger.bag(workspace, 'kant_aufklaerung_1784', skip_zip=False, dest=join(tempdir, 'out.ocrd.zip'))
    bagger.spill(join(tempdir, 'out.ocrd.zip'), tempdir)

def test_bag_wo_dest(bagger_fixture):
    bagger, workspace, _, _ = bagger_fixture
    bagger.bag(workspace, 'kant_aufklaerung_1784', skip_zip=True)

def test_bag_wo_dest_zip(bagger_fixture):
    bagger, workspace, _, _ = bagger_fixture
    bagger.bag(workspace, 'kant_aufklaerung_1784', skip_zip=True)

def test_bag_partial_http_nostrict(bagger_fixture):
    bagger, workspace, _, _ = bagger_fixture
    bagger.strict = False
    workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://ocr-d.de'
    bagger.bag(workspace, 'kant_aufklaerung_1784')
    bagger.strict = True

def test_bag_full(bagger_fixture):
    bagger, workspace, _, _ = bagger_fixture
    bagger.strict = True
    f = workspace.mets.find_all_files(ID='INPUT_0017')[0]
    f.url = 'bad-scheme://foo'
    f.local_filename = None
    with raises(Exception, match="No connection adapters were found for 'bad-scheme://foo'"):
        bagger.bag(workspace, 'kant_aufklaerung_1784', skip_zip=False)
    bagger.strict = False

def test_spill_dest_not_dir(bagger_fixture):
    bagger, _, _, _ = bagger_fixture
    with raises(Exception, match="Not a directory: /dev/stdout"):
        bagger.spill('x', '/dev/stdout')

def test_spill_derived_dest_exists(bagger_fixture):
    bagger, _, bagdir, _ = bagger_fixture
    dest = join(bagdir, 'foo')
    makedirs(dest)
    with raises(Exception, match=f"Directory exists: {dest}"):
        bagger.spill('/path/to/foo.ocrd.zip', bagdir)

def test_spill_derived_dest(bagger_fixture):
    bagger, workspace, bagdir, _ = bagger_fixture
    bag_dest = join(bagdir, 'foo.ocrd.zip')
    spill_dest = join(bagdir, 'foo')
    bagger.bag(workspace, 'kant_aufklaerung_1784', skip_zip=False, dest=bag_dest)
    bagger.spill(bag_dest, bagdir)
    assert exists(spill_dest)

def test_bag_with_changed_metsname(bagger_fixture):
    bagger, _, bagdir, _ = bagger_fixture
    # arrange
    workspace_dir = join(bagdir, "changed-mets-test")
    bag_dest = join(bagdir, 'bagged-workspace')
    copytree(join(assets.path_to('kant_aufklaerung_1784'), "data"), workspace_dir)
    new_metsname = "other-metsname.xml"
    old_metspath = join(workspace_dir, "mets.xml")
    new_metspath = join(workspace_dir, new_metsname)
    move(old_metspath, new_metspath)
    workspace = Workspace(Resolver(), directory=workspace_dir, mets_basename=new_metsname)

    # act
    bagger.bag(workspace, "changed-mets-test", dest=bag_dest, ocrd_mets=new_metsname, skip_zip=True)

    # assert
    bag_metspath = join(bag_dest, "data", new_metsname)
    assert exists(bag_metspath), f"Mets not existing. Expected: {bag_metspath}"

    bag_info_path = join(bag_dest, "bag-info.txt")
    tags = _load_tag_file(bag_info_path)
    assert "Ocrd-Mets" in tags, "expect 'Ocrd-Mets'-key in bag-info.txt"
    assert tags["Ocrd-Mets"] == new_metsname, "Ocrd-Mets key present but wrong value"

def test_spill_with_changed_metsname(bagger_fixture):
    bagger, _, bagdir, _ = bagger_fixture

    # arrange
    new_metsname = "other-metsname.xml"
    example_workspace_dir = join(bagdir, "example_workspace_dir")
    makedirs(join(example_workspace_dir))
    bag_dest = join(bagdir, 'foo.ocrd.zip')
    workspace = Resolver().workspace_from_nothing(example_workspace_dir, new_metsname)
    bagger.bag(workspace, "mets-changed-test", bag_dest, new_metsname)

    # act
    spill_dest = join(bagdir, 'spilled_changed_mets')
    bagger.spill(bag_dest, spill_dest)

    # assert
    assert exists(spill_dest), "spill-destination-directory was not created"
    assert not exists(join(spill_dest, "mets.xml")), "'mets.xml' should not be present"
    assert exists(join(spill_dest, new_metsname)), "expected mets-file to be '{new_metsname}'"

def test_recreate_checksums_param_validation(bagger_fixture):
    bagger, _, _, _ = bagger_fixture
    with raises(Exception, match="For checksum recreation 'dest' must be provided"):
        bagger.recreate_checksums("src/path")
    with raises(Exception, match="Setting 'dest' and 'overwrite' is a contradiction"):
        bagger.recreate_checksums("src/path", "dest/path", overwrite=True)

def test_recreate_checksums_overwrite_unzipped(bagger_fixture):
    bagger, _, bagdir, _ = bagger_fixture

    # arrange
    assert Bag(bagdir).is_valid(), "tests arrangements for recreate_checksums failed"
    move(join(bagdir, "data", "mets.xml"), join(bagdir, "data", "mets-neu.xml"))
    assert not Bag(bagdir).is_valid(), "tests arrangements for recreate_checksums failed"

    # act
    bagger.recreate_checksums(bagdir, overwrite=True)

    # assert
    assert Bag(bagdir).is_valid(), "recreate_checksums unzippd with overwrite failed"

def test_recreate_checksums_unzipped(bagger_fixture):
    bagger, _, bagdir, tempdir = bagger_fixture

    # arrange
    move(join(bagdir, "data", "mets.xml"), join(bagdir, "data", "mets-neu.xml"))
    new_bag = join(tempdir, "new_bag")

    # act
    bagger.recreate_checksums(bagdir, new_bag)

    # assert
    assert Bag(new_bag).is_valid(), "recreate_checksums unzipped failed"

def test_recreate_checksums_zipped_overwrite(bagger_fixture):
    bagger, _, bagdir, tempdir = bagger_fixture

    # arrange
    move(join(bagdir, "data", "mets.xml"), join(bagdir, "data", "mets-neu.xml"))
    zipped_bag = join(tempdir, "foo.ocrd.zip")
    make_archive(zipped_bag.replace('.zip', ''), 'zip', bagdir)

    # act
    bagger.recreate_checksums(zipped_bag, overwrite=True)

    # assert
    bag_dest = join(tempdir, "new_bag")
    unzip_file_to_dir(zipped_bag, bag_dest)
    assert Bag(bag_dest).is_valid(), "recreate_checksums zipped with overwrite failed"

def test_recreate_checksums_zipped(bagger_fixture):
    bagger, _, bagdir, tempdir = bagger_fixture

    # arrange
    move(join(bagdir, "data", "mets.xml"), join(bagdir, "data", "mets-neu.xml"))
    zipped_bag = join(tempdir, "foo.ocrd.zip")
    make_archive(zipped_bag.replace('.zip', ''), 'zip', bagdir)
    zipped_bag_dest = join(tempdir, "foo-new.ocrd.zip")

    # act
    bagger.recreate_checksums(zipped_bag, zipped_bag_dest)

    # assert
    bag_dest = join(tempdir, "new_bag")
    unzip_file_to_dir(zipped_bag_dest, bag_dest)
    assert Bag(bag_dest).is_valid(), "recreate_checksums zipped failed"

def test_basename_conflict(tmpdir):
    """
    Ensure that when downloading during bagging, there are no filename
    conflicts, i.e. all files are downloaded, none are overwritten.
    """
    bagger = WorkspaceBagger(Resolver())
    workspace = Workspace(Resolver(), directory=str(Path(__file__).parent.parent / 'data/bagger-conflict-workspace'))
    bagger.bag(workspace, 'bagger-conflict-test', skip_zip=True, dest=str(tmpdir / 'bag'))
    assert len(workspace.mets.find_all_files()) == 3
    assert len(list(Path(tmpdir, 'bag/data/A').iterdir())) == 3

def test_filter(tmpdir):
    # initLogging()
    bagger = WorkspaceBagger(Resolver())
    fgs = ['A', 'B', 'C', 'D', 'E']
    with pushd_popd(tmpdir):
        Path('workspace').mkdir()
        workspace = Resolver().workspace_from_nothing(tmpdir / 'workspace')
        for fg in fgs:
            Path(fg).mkdir()
            for i in range(3):
                workspace.add_file(fg, mimetype='foo/bar', file_id=f'{fg}_{i}', page_id=f'page{i}', local_filename=f'{fg}/file{i}.ext', content='')
        # print([str(x) for x in workspace.mets.find_all_files()])

        # test w/o filter
        bagger.bag(workspace, 'foo', skip_zip=True, dest=str(tmpdir / 'bag1'))
        for fg in fgs:
            assert len(list(Path(f'bag1/data/{fg}').iterdir())) == 3

        # test include
        bagger.bag(workspace, 'foo', skip_zip=True, dest=str(tmpdir / 'bag2'), include_fileGrp=['A'])
        assert len(list(Path(f'bag2/data/A').iterdir())) == 3
        for fg in ['B', 'C', 'D', 'E']:
            assert not Path(f'bag2/data/{fg}').exists()

        # test exclude
        bagger.bag(workspace, 'foo', skip_zip=True, dest=str(tmpdir / 'bag3'), exclude_fileGrp=['A'])
        assert not Path(f'bag3/data/A').exists()
        for fg in ['B', 'C', 'D', 'E']:
            assert len(list(Path(f'bag3/data/{fg}').iterdir())) == 3

        # test include + exclude
        bagger.bag(workspace, 'foo', skip_zip=True, dest=str(tmpdir / 'bag4'), exclude_fileGrp=['A'], include_fileGrp=['A'])
        for fg in fgs:
            assert not Path(f'bag4/data/{fg}').exists()

if __name__ == '__main__':
    main(__name__)
