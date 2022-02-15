from os import makedirs
from os.path import join, abspath, exists
from shutil import copytree, rmtree
from tempfile import mkdtemp

from tests.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module

from ocrd.workspace import Workspace
from ocrd.workspace_bagger import WorkspaceBagger, BACKUPDIR
from ocrd.resolver import Resolver

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

    def test_bad_manifestation_depth(self):
        with self.assertRaisesRegex(Exception, "manifestation_depth must be 'full' or 'partial'"):
            self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='foo')

    def test_bad_inplace_and_dest(self):
        with self.assertRaisesRegex(Exception, "Setting 'dest' and 'in_place' is a contradiction"):
            self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', in_place=True, dest='/x/y/z')

    def test_bad_skip_zip_and_dest(self):
        with self.assertRaisesRegex(Exception, "Setting 'skip_zip' and not 'in_place' is a contradiction"):
            self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', in_place=True, skip_zip=False)

    def test_bag_inplace(self):
        self.bagger.bag(
            self.workspace,
            'kant_aufklaerung_1784',
            ocrd_manifestation_depth='partial',
            skip_zip=True,
            in_place=True,
            ocrd_base_version_checksum='123',
            tag_files=[
                README_FILE
            ],
        )

    def test_bag_zip_and_spill(self):
        self.workspace.mets.find_all_files(ID='INPUT_0017')[0].url = 'bad-scheme://foo'
        self.workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://google.com'
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='full', skip_zip=False, dest=join(self.tempdir, 'out.ocrd.zip'))
        self.bagger.spill(join(self.tempdir, 'out.ocrd.zip'), join(self.tempdir, 'out'))

    def test_bag_zip_and_spill_wo_dest(self):
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', in_place=False, skip_zip=False, dest=join(self.tempdir, 'out.ocrd.zip'))
        self.bagger.spill(join(self.tempdir, 'out.ocrd.zip'), self.tempdir)

    def test_bag_wo_dest(self):
        makedirs(BACKUPDIR)
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', in_place=True, skip_zip=True)

    def test_bag_wo_dest_zip(self):
        makedirs(BACKUPDIR)
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', in_place=False, skip_zip=True)

    def test_bag_partial_http_nostrict(self):
        self.bagger.strict = False
        makedirs(BACKUPDIR)
        self.workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://google.com'
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', in_place=False)

    def test_bag_partial_http_strict(self):
        self.bagger.strict = True
        makedirs(BACKUPDIR)
        self.workspace.mets.find_all_files(ID='INPUT_0020')[0].url = 'http://google.com'
        with self.assertRaisesRegex(Exception, "Not fetching non-local files"):
            self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', in_place=False)

    def test_bag_full(self):
        self.bagger.strict = True
        f = self.workspace.mets.find_all_files(ID='INPUT_0017')[0]
        f.url = 'bad-scheme://foo'
        f.local_filename = None
        with self.assertRaisesRegex(Exception, "Not an http URL"):
            self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='full', skip_zip=False)

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
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', in_place=False, skip_zip=False, dest=bag_dest)
        self.bagger.spill(bag_dest, self.bagdir)
        self.assertTrue(exists(spill_dest))

if __name__ == '__main__':
    main()
