from tempfile import TemporaryDirectory
from os.path import join

from tests.base import TestCase, assets, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd_validators import WorkspaceValidator
from ocrd_models.constants import METS_XML_EMPTY

class TestWorkspaceValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()

    def test_simple(self):
        report = WorkspaceValidator.validate(self.resolver, assets.url_of('SBB0000F29300010000/data/mets_one_file.xml'), download=True)
        self.assertTrue(report.is_valid)

    def test_validate_twice(self):
        validator = WorkspaceValidator(self.resolver, assets.url_of('SBB0000F29300010000/data/mets_one_file.xml'), download=True)
        report = validator._validate() # pylint: disable=protected-access
        report = validator._validate() # pylint: disable=protected-access
        self.assertTrue(report.is_valid)

    def test_validate_empty(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 2)
            self.assertIn('no unique identifier', report.errors[0])
            self.assertIn('No files', report.errors[1])
            workspace.mets.unique_identifier = 'foobar'
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 1)

    def test_validate_file_groups_non_ocrd(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file_group('FOO')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 1)
            self.assertIn('No files', report.errors[0])
            self.assertEqual(len(report.notices), 1)
            self.assertIn("USE does not begin with 'OCR-D-'", report.notices[0])

    def test_validate_file_groups_unspecified(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file_group('OCR-D-INVALID-FILEGRP')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 2)
            self.assertEqual(report.errors[0], "Unspecified USE category 'INVALID' in fileGrp 'OCR-D-INVALID-FILEGRP'")
            self.assertIn('No files', report.errors[1])

    def test_validate_file_groups_bad_name(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file_group('OCR-D-GT-X')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 2)
            self.assertIn("Invalid USE name 'X' in fileGrp", report.errors[0])
            self.assertIn('No files', report.errors[1])

    def test_validate_files_nopageid(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file('OCR-D-GT-PAGE', ID='file1', mimetype='image/png')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'), skip=['pixel_density'])
            print(report.errors)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("does not manifest any physical page.", report.errors[0])

    def test_bad_workspace(self):
        report = WorkspaceValidator.validate(self.resolver, 'non existe')
        self.assertFalse(report.is_valid)
        self.assertIn('Failed to instantiate workspace:', report.errors[0])

    def test_skip_page(self):
        report = WorkspaceValidator.validate(
            self.resolver, None, src_dir=assets.path_to('kant_aufklaerung_1784/data'),
            download=True,
            skip=[
                'page',
                'mets_unique_identifier',
                'mets_file_group_names',
                'mets_files',
                'pixel_density',
            ]
        )
        self.assertTrue(report.is_valid)

    def test_src_dir(self):
        report = WorkspaceValidator.validate(
            self.resolver, None, src_dir=assets.path_to('kant_aufklaerung_1784/data'),
            download=True,
        )
        self.assertEqual(len(report.errors), 42)

if __name__ == '__main__':
    main()
