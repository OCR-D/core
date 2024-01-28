from os.path import join
from shutil import copytree, rmtree
from tempfile import mkdtemp

from ocrd.resolver import Resolver
from ocrd.workspace import Workspace
from ocrd.workspace_bagger import WorkspaceBagger
from ocrd_validators import OcrdZipValidator
from tests.base import (  # pylint: disable=import-error,no-name-in-module
    TestCase, assets, main)

#  from bagit import BagValidationError # pylint: disable=no-name-in-module


class TestOcrdZipValidator(TestCase):

    def setUp(self):
        super().setUp()
        self.resolver = Resolver()
        self.bagger = WorkspaceBagger(self.resolver)
        self.tempdir = mkdtemp()
        self.bagdir = join(self.tempdir, 'kant_aufklaerung_1784')
        copytree(assets.path_to('kant_aufklaerung_1784'), self.bagdir)
        self.workspace_dir = join(self.bagdir, 'data')
        self.workspace = Workspace(self.resolver, directory=join(self.workspace_dir))

    def tearDown(self):
        rmtree(self.tempdir)

    def test_validation0(self):
        ocrdzip = self.bagger.bag(self.workspace, 'SBB0000F29300010000')
        report = OcrdZipValidator(self.resolver, ocrdzip).validate()
        self.assertEqual(report.is_valid, True)

    def test_validation_unzipped0(self):
        validator = OcrdZipValidator(self.resolver, self.bagdir)
        # import os
        # from ocrd_utils import pushd_popd
        # with pushd_popd(self.bagdir):
        #     os.system('find')
        # print(report)
        report = validator.validate(skip_unzip=True)
        self.assertEqual(report.is_valid, True)

    def test_validation_unzipped_skip_bag(self):
        validator = OcrdZipValidator(self.resolver, self.bagdir)
        report = validator.validate(skip_unzip=True, skip_bag=True)
        self.assertEqual(report.is_valid, True)
        print(report)


    def test_fail_validation_no_such_file(self):
        validator = OcrdZipValidator(self.resolver, '/does/not/exist.ocrd.zip')
        with self.assertRaisesRegex(IOError, "Can't find file"):
            validator.validate(skip_unzip=False)

    def test_fail_validation_unzipped_extra_files(self):
        validator = OcrdZipValidator(self.resolver, self.bagdir)
        extrapath = join(self.bagdir, 'data', 'EXTRA')
        with open(extrapath, 'w') as f:
            f.write('FAIL')
        with self.assertRaisesRegex(Exception, "Payload-Oxum validation failed"):
            validator.validate(skip_unzip=True)

    def test_fail_validation_extra_tagfile(self):
        extrapath = join(self.bagdir, 'NOT-ALLOWED')
        with open(extrapath, 'w') as f:
            f.write('FAIL')
        validator = OcrdZipValidator(self.resolver, self.bagdir)
        with self.assertRaisesRegex(Exception, "Existing tag file 'NOT-ALLOWED' is not listed in Tag-Files-Allowed."):
            validator.validate(skip_unzip=True)

if __name__ == '__main__':
    main()
