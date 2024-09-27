import os
from tempfile import TemporaryDirectory
from pathlib import Path
from os.path import join
from shutil import copytree
import pytest

from ocrd_utils import pushd_popd
from ocrd.resolver import Resolver
from ocrd_validators import WorkspaceValidator
from ocrd_validators.page_validator import ConsistencyError

from tests.base import TestCase, assets, main, copy_of_directory # pylint: disable=import-error,no-name-in-module

class TestWorkspaceValidator(TestCase):

    def setUp(self):
        super().setUp()
        self.resolver = Resolver()

    def test_check_file_grp_basic(self):
        workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))
        report = WorkspaceValidator.check_file_grp(workspace, 'foo', 'bar')
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0], "Input fileGrp[@USE='foo'] not in METS!")
        report = WorkspaceValidator.check_file_grp(workspace, 'OCR-D-IMG', 'OCR-D-IMG-BIN')
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0], "Output fileGrp[@USE='OCR-D-IMG-BIN'] already in METS!")
        report = WorkspaceValidator.check_file_grp(workspace, 'OCR-D-IMG,FOO', 'FOO')
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0], "Input fileGrp[@USE='FOO'] not in METS!")
        report = WorkspaceValidator.check_file_grp(workspace, 'OCR-D-IMG,FOO', None)
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0], "Input fileGrp[@USE='FOO'] not in METS!")
        report = WorkspaceValidator.check_file_grp(workspace, None, '')
        self.assertTrue(report.is_valid)

    def test_check_file_grp_page_id_str(self):
        workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))
        report = WorkspaceValidator.check_file_grp(workspace, 'OCR-D-IMG', 'OCR-D-IMG-BIN', page_id='PHYS_0001')
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0], "Output fileGrp[@USE='OCR-D-IMG-BIN'] already contains output for page PHYS_0001")

    def test_check_file_grp_page_id_list(self):
        workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))
        report = WorkspaceValidator.check_file_grp(workspace, 'OCR-D-IMG', 'OCR-D-IMG-BIN', page_id=['PHYS_0001'])
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)

    def test_check_file_grp_page_id_valid(self):
        workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))
        report = WorkspaceValidator.check_file_grp(workspace, 'OCR-D-IMG', 'OCR-D-IMG-BIN', page_id='PHYS_0005')
        self.assertTrue(report.is_valid)

    def test_simple(self):
        report = WorkspaceValidator.validate(self.resolver, assets.url_of('SBB0000F29300010000/data/mets_one_file.xml'), download=True)
        self.assertTrue(report.is_valid)

    def test_validate_twice(self):
        validator = WorkspaceValidator(self.resolver, assets.url_of('SBB0000F29300010000/data/mets_one_file.xml'), download=True)
        report = validator._validate() # pylint: disable=protected-access
        report = validator._validate() # pylint: disable=protected-access
        print(report.errors)
        self.assertTrue(report.is_valid)

    def test_validate_empty(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 3) # no-files, missing id, missing fileGrp
            self.assertIn('no unique identifier', report.errors[0])
            self.assertIn('No files', report.errors[1])
            workspace.mets.unique_identifier = 'foobar'
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 2)

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
            self.assertIn("fileGrp USE 'FOO' does not begin with 'OCR-D-'", report.notices[0])

    def test_validate_file_groups_unspecified(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file_group('OCR-D-INVALID-FILEGRP')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            print(report.notices)
            self.assertEqual(len(report.errors), 1)
            self.assertEqual(len(report.notices), 1)
            self.assertEqual(report.notices[0], "Unspecified USE category 'INVALID' in fileGrp 'OCR-D-INVALID-FILEGRP'")
            self.assertIn('No files', report.errors[0])

    def test_validate_file_groups_bad_name(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file_group('OCR-D-GT-X')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'))
            self.assertEqual(len(report.errors), 1)
            self.assertEqual(len(report.notices), 1)
            self.assertIn("Invalid USE name 'X' in fileGrp", report.notices[0])
            self.assertIn('No files', report.errors[0])

    @pytest.mark.skip(reason="missing pageId means document-global now")
    def test_validate_files_nopageid(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file('OCR-D-GT-PAGE', ID='file1', mimetype='image/png', url='http://foo')
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'), skip=['pixel_density', 'imagefilename'])
            self.assertEqual(len(report.errors), 1)
            self.assertIn("does not manifest any physical page.", report.errors[0])

    def test_validate_weird_urls(self):
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file('OCR-D-GT-PAGE', ID='file1', mimetype='image/png', pageId='page1', url='file:/java-file-url')
            f = workspace.mets.add_file('OCR-D-GT-PAGE', ID='file2', mimetype='image/png', pageId='page2', url='nothttp://unusual.scheme')
            f._el.set('GROUPID', 'donotuse') # pylint: disable=protected-access
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'), skip=['pixel_density'])
            assert not report.is_valid
            assert len(report.errors) == 1
            assert "invalid (Java-specific) file URL" in report.errors[0]
            assert len(report.warnings) == 1
            assert "non-HTTP" in report.warnings[0]

    @pytest.mark.skip("Not usable as such anymore, because we properly distinguish .url and .local_filename now. Requires a server to test")
    def test_validate_pixel_no_download(self):
        imgpath = assets.path_to('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-BIN/BIN_0020.png')
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file('OCR-D-GT-BIN', ID='file1', mimetype='image/png', pageId='page1', local_filename=imgpath)
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'), skip=[], download=False)
            self.assertEqual(len(report.errors), 0)
            self.assertEqual(len(report.warnings), 0)
            self.assertEqual(len(report.notices), 0)

    def test_validate_pixel_density_too_low(self):
        imgpath = assets.path_to('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-BIN/BIN_0017.png')
        with TemporaryDirectory() as tempdir:
            workspace = self.resolver.workspace_from_nothing(directory=tempdir)
            workspace.mets.unique_identifier = 'foobar'
            workspace.mets.add_file('OCR-D-GT-BIN', ID='file1', mimetype='image/png', pageId='page1', local_filename=imgpath)
            workspace.save_mets()
            report = WorkspaceValidator.validate(self.resolver, join(tempdir, 'mets.xml'), skip=[], download=True)
            self.assertEqual(len(report.notices), 2)
            self.assertIn("xResolution", report.notices[0])
            self.assertIn("yResolution", report.notices[1])
            self.assertEqual(len(report.warnings), 0)
            self.assertEqual(len(report.errors), 0)

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
                'imagefilename',
            ]
        )
        print(report.errors)
        self.assertTrue(report.is_valid)

    def test_dimensions(self):
        with TemporaryDirectory() as tempdir:
            wsdir = join(tempdir, 'foo')
            copytree(assets.path_to('kant_aufklaerung_1784/data'), wsdir)
            with pushd_popd(wsdir):
                os.system("""sed -i.bak 's,imageHeight="2083",imageHeight="1234",' OCR-D-GT-PAGE/PAGE_0017_PAGE.xml""")
                report = WorkspaceValidator.validate(
                    self.resolver,
                    join(wsdir, 'mets.xml'),
                    src_dir=wsdir,
                    skip=['page', 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'imagefilename', 'page_xsd', 'mets_xsd'],
                    download=True
                )
                self.assertIn("PAGE 'PAGE_0017_PAGE': @imageHeight != image's actual height (1234 != 2083)", report.errors)
                #  print(report.errors)
                self.assertEqual(len(report.errors), 1)
                self.assertEqual(report.is_valid, False)
                report2 = WorkspaceValidator.validate(self.resolver, join(wsdir, 'mets.xml'), src_dir=wsdir, skip=[
                    'page', 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'imagefilename',
                    'dimension', 'page_xsd', 'mets_xsd'
                    ], download=False)
            self.assertEqual(report2.is_valid, True)

    def test_src_dir(self):
        report = WorkspaceValidator.validate(
            self.resolver, None, src_dir=assets.path_to('kant_aufklaerung_1784/data'),
            skip=['imagefilename'],
            download=True,
        )
        print(report.errors)
        self.assertEqual(len([e for e in report.errors if isinstance(e, ConsistencyError)]), 42, '42 textequiv consistency errors')

    def test_imagefilename(self):
        report = WorkspaceValidator.validate(
            self.resolver, None, src_dir=assets.path_to('kant_aufklaerung_1784/data'),
            skip=['page', 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'page_xsd', 'mets_xsd'],
            download=False,
        )
        self.assertEqual(len(report.errors), 0)

    def test_pcgtsid(self):
        with copy_of_directory(assets.path_to('kant_aufklaerung_1784/data')) as wsdir:
            with pushd_popd(wsdir):
                # remove the @pcGtsId attribute for testing
                os.system("""sed -i.bak 's,pcGtsId.*,pcGtsId="foo">,' OCR-D-GT-PAGE/PAGE_0017_PAGE.xml""")
                report = WorkspaceValidator.validate(self.resolver, join(wsdir, 'mets.xml'))
                self.assertIn('pc:PcGts/@pcGtsId differs from mets:file/@ID: "foo" !== "PAGE_0017_PAGE"', report.warnings)

    def test_symlink(self):
        """
        Data from https://github.com/OCR-D/core/issues/802
        """
        report = WorkspaceValidator.validate(
            Resolver(), None, src_dir=str(Path(__file__).parent.parent / "data/symlink-workspace"),
            skip=['page', 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'page_xsd', 'mets_xsd'],
            download=False,
        )
        print(report.errors)
        assert report.is_valid


if __name__ == '__main__':
    main(__file__)
