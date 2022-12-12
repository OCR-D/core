from os import makedirs
from os.path import join, abspath, exists
from shutil import copytree, rmtree, move, make_archive
from tempfile import mkdtemp
from bagit import _load_tag_file, Bag

from tests.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module

from ocrd.workspace import Workspace
from ocrd.workspace_bagger import WorkspaceBagger, BACKUPDIR
from ocrd.resolver import Resolver
from ocrd_utils import unzip_file_to_dir

README_FILE = abspath('README.md')

class TestWorkspaceBagger(TestCase):

    def setUp(self):
        super().setUp()
        pass
        if exists(BACKUPDIR):
            rmtree(BACKUPDIR)
        self.resolver = Resolver()
        self.bagger = WorkspaceBagger(self.resolver)
        self.tempdir = mkdtemp()
        self.bagdir = join(self.tempdir, 'bag')
        copytree(assets.path_to('kant_aufklaerung_1784'), self.bagdir)
        self.workspace_dir = join(self.bagdir, 'data')
        self.workspace = Workspace(self.resolver, directory=self.workspace_dir)

    def tearDown(self):
        rmtree(self.tempdir)

    def test_bag_zip_and_spill(self):
        self.workspace.mets.find_all_files(ID='INPUT_0017')[0].url = 'bad-scheme://foo'
        self.workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://google.com'
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', skip_zip=False, dest=join(self.tempdir, 'out.ocrd.zip'))
        self.bagger.spill(join(self.tempdir, 'out.ocrd.zip'), join(self.tempdir, 'out'))

    def test_bag_zip_and_spill_wo_dest(self):
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', skip_zip=False, dest=join(self.tempdir, 'out.ocrd.zip'))
        self.bagger.spill(join(self.tempdir, 'out.ocrd.zip'), self.tempdir)

    def test_bag_wo_dest(self):
        makedirs(BACKUPDIR)
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', skip_zip=True)

    def test_bag_wo_dest_zip(self):
        makedirs(BACKUPDIR)
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', skip_zip=True)

    def test_bag_partial_http_nostrict(self):
        self.bagger.strict = False
        makedirs(BACKUPDIR)
        self.workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://google.com'
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784')

    def test_bag_full(self):
        self.bagger.strict = True
        f = self.workspace.mets.find_all_files(ID='INPUT_0017')[0]
        f.url = 'bad-scheme://foo'
        f.local_filename = None
        with self.assertRaisesRegex(Exception, "Not an http URL"):
            self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', skip_zip=False)
        self.bagger.strict = False

    def test_spill_dest_not_dir(self):
        with self.assertRaisesRegex(Exception, "Not a directory: /dev/stdout"):
            self.bagger.spill('x', '/dev/stdout')

    def test_spill_derived_dest_exists(self):
        dest = join(self.bagdir, 'foo')
        makedirs(dest)
        with self.assertRaisesRegex(Exception, "Directory exists: %s" % dest):
            self.bagger.spill('/path/to/foo.ocrd.zip', self.bagdir)

    def test_spill_derived_dest(self):
        bag_dest = join(self.bagdir, 'foo.ocrd.zip')
        spill_dest = join(self.bagdir, 'foo')
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', skip_zip=False, dest=bag_dest)
        self.bagger.spill(bag_dest, self.bagdir)
        self.assertTrue(exists(spill_dest))

    def test_bag_with_changed_metsname(self):
        # arrange
        workspace_dir = join(self.bagdir, "changed-mets-test")
        bag_dest = join(self.bagdir, 'bagged-workspace')
        copytree(join(assets.path_to('kant_aufklaerung_1784'), "data"), workspace_dir)
        new_metsname = "other-metsname.xml"
        old_metspath = join(workspace_dir, "mets.xml")
        new_metspath = join(workspace_dir, new_metsname)
        move(old_metspath, new_metspath)
        workspace = Workspace(self.resolver, directory=workspace_dir, mets_basename=new_metsname)

        # act
        self.bagger.bag(workspace, "changed-mets-test", dest=bag_dest, ocrd_mets=new_metsname, skip_zip=True)

        # assert
        bag_metspath = join(bag_dest, "data", new_metsname)
        self.assertTrue(exists(bag_metspath), f"Mets not existing. Expected: {bag_metspath}")

        bag_info_path = join(bag_dest, "bag-info.txt")
        tags = _load_tag_file(bag_info_path)
        self.assertTrue("Ocrd-Mets" in tags, "expect 'Ocrd-Mets'-key in bag-info.txt")
        self.assertEqual(tags["Ocrd-Mets"], new_metsname, "Ocrd-Mets key present but wrong value")

    def test_spill_with_changed_metsname(self):
        # arrange
        new_metsname = "other-metsname.xml"
        example_workspace_dir = join(self.bagdir, "example_workspace_dir")
        makedirs(join(example_workspace_dir))
        bag_dest = join(self.bagdir, 'foo.ocrd.zip')
        workspace = self.resolver.workspace_from_nothing(example_workspace_dir, new_metsname)
        self.bagger.bag(workspace, "mets-changed-test", bag_dest, new_metsname)

        # act
        spill_dest = join(self.bagdir, 'spilled_changed_mets')
        self.bagger.spill(bag_dest, spill_dest)

        # assert
        self.assertTrue(exists(spill_dest), "spill-destination-directory was not created")
        self.assertFalse(exists(join(spill_dest, "mets.xml")), "'mets.xml' should not be present")
        self.assertTrue(exists(join(spill_dest, new_metsname)),
                        "expected mets-file to be '{new_metsname}'")

    def test_recreate_checksums_param_validation(self):
        with self.assertRaisesRegex(Exception, "For checksum recreation 'dest' must be provided"):
            self.bagger.recreate_checksums("src/path")
        with self.assertRaisesRegex(Exception, "Setting 'dest' and 'overwrite' is a contradiction"):
            self.bagger.recreate_checksums("src/path", "dest/path", overwrite=True)

    def test_recreate_checksums_overwrite_unzipped(self):
        # arrange
        assert Bag(self.bagdir).is_valid(), "tests arrangements for recreate_checksums failed"
        move(join(self.bagdir, "data", "mets.xml"), join(self.bagdir, "data", "mets-neu.xml"))
        assert not Bag(self.bagdir).is_valid(), "tests arrangements for recreate_checksums failed"

        # act
        self.bagger.recreate_checksums(self.bagdir, overwrite=True)

        # assert
        assert Bag(self.bagdir).is_valid(), "recreate_checksums unzippd with overwrite failed"

    def test_recreate_checksums_unzipped(self):
        # arrange
        move(join(self.bagdir, "data", "mets.xml"), join(self.bagdir, "data", "mets-neu.xml"))
        new_bag = join(self.tempdir, "new_bag")

        # act
        self.bagger.recreate_checksums(self.bagdir, new_bag)

        # assert
        assert Bag(new_bag).is_valid(), "recreate_checksums unzipped failed"

    def test_recreate_checksums_zipped_overwrite(self):
        # arrange
        move(join(self.bagdir, "data", "mets.xml"), join(self.bagdir, "data", "mets-neu.xml"))
        zipped_bag = join(self.tempdir, "foo.ocrd.zip")
        make_archive(zipped_bag.replace('.zip', ''), 'zip', self.bagdir)

        # act
        self.bagger.recreate_checksums(zipped_bag, overwrite=True)

        # assert
        bag_dest = join(self.tempdir, "new_bag")
        unzip_file_to_dir(zipped_bag, bag_dest)
        assert Bag(bag_dest).is_valid(), "recreate_checksums zipped with overwrite failed"

    def test_recreate_checksums_zipped(self):
        # arrange
        move(join(self.bagdir, "data", "mets.xml"), join(self.bagdir, "data", "mets-neu.xml"))
        zipped_bag = join(self.tempdir, "foo.ocrd.zip")
        make_archive(zipped_bag.replace('.zip', ''), 'zip', self.bagdir)
        zipped_bag_dest = join(self.tempdir, "foo-new.ocrd.zip")

        # act
        self.bagger.recreate_checksums(zipped_bag, zipped_bag_dest)

        # assert
        bag_dest = join(self.tempdir, "new_bag")
        unzip_file_to_dir(zipped_bag_dest, bag_dest)
        assert Bag(bag_dest).is_valid(), "recreate_checksums zipped failed"


if __name__ == '__main__':
    main()
