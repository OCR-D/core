from os.path import join
from shutil import copytree, rmtree
from tempfile import mkdtemp

from tests.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module

from ocrd.workspace_backup import WorkspaceBackupManager
from ocrd import Workspace
from ocrd.resolver import Resolver

class TestWorkspaceBackup(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.tempdir = mkdtemp()
        self.workspace_dir = join(self.tempdir, 'kant_aufklaerung_1784')
        copytree(assets.path_to('kant_aufklaerung_1784/data'), self.workspace_dir)
        self.workspace = Workspace(self.resolver, directory=join(self.workspace_dir))
        self.mgr = WorkspaceBackupManager(self.workspace)

    def tearDown(self):
        rmtree(self.tempdir)

    def test_backup_mgr(self):
        #  bk = WorkspaceBackup.from_path(self.workspace_dir)
        self.mgr.restore('whatever')
        self.mgr.undo()
        self.assertEqual(self.mgr.list(), [])
        first = self.mgr.add()
        self.assertEqual(first, '94d33aa8773bbbf78919f89a01f03392ad39bb295859cca065d2d8eb8a4811e9')
        self.assertEqual(len(self.mgr.list()), 1)
        self.mgr.add()
        self.assertEqual(len(self.mgr.list()), 1)
        self.workspace.mets.add_file('FOO', ID='x123')
        self.assertEqual(self.workspace.mets.file_groups, ['OCR-D-IMG', 'OCR-D-GT-PAGE', 'OCR-D-GT-ALTO', 'FOO'])
        self.mgr.undo()
        self.mgr.add()
        self.assertEqual(len(self.mgr.list()), 3)
        self.assertEqual(self.workspace.mets.file_groups, ['OCR-D-IMG', 'OCR-D-GT-PAGE', 'OCR-D-GT-ALTO'])
        self.workspace.mets.add_file('FOO', ID='x123')
        self.mgr.restore(first, choose_first=True)
        self.assertEqual(self.workspace.mets.file_groups, ['OCR-D-IMG', 'OCR-D-GT-PAGE', 'OCR-D-GT-ALTO'])
        self.workspace.mets.add_file('FOO', ID='x123')
        with self.assertRaisesRegex(Exception, 'Not unique'):
            self.mgr.restore(first, choose_first=False)

if __name__ == '__main__':
    main()
