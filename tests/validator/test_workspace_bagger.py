#  from os import unlink
from os.path import join
from shutil import copytree, rmtree
from tempfile import mkdtemp

from tests.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module

from ocrd.workspace import Workspace
from ocrd.workspace_bagger import WorkspaceBagger
from ocrd.resolver import Resolver

class TestOcrdZipValidator(TestCase):

    def setUp(self):
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

    def test_bag_zip_and_spill(self):
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', skip_zip=False, dest=join(self.tempdir, 'out.ocrd.zip'))
        self.bagger.spill(join(self.tempdir, 'out.ocrd.zip'), join(self.tempdir, 'out'))

    def test_bag_zip_and_spill_wo_dest(self):
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', skip_zip=False, dest=join(self.tempdir, 'out.ocrd.zip'))
        self.bagger.spill(join(self.tempdir, 'out.ocrd.zip'), self.tempdir)

    def test_bag_inplace(self):
        self.bagger.bag(self.workspace, 'kant_aufklaerung_1784', ocrd_manifestation_depth='partial', skip_zip=True, in_place=True)

if __name__ == '__main__':
    main()
