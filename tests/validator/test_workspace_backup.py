from os.path import join
from shutil import copytree, rmtree
from tempfile import mkdtemp

from tests.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module

from ocrd.workspace_backup import WorkspaceBackupManager
from ocrd import Workspace
from ocrd.resolver import Resolver

class TestWorkspaceBackup(TestCase):

    def setUp(self):
        super().setUp()
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
        self.assertEqual(first, '55c54aa8e10b13e495eebe292bb00250478dc9f365ea21afc2b297fe889a5a0c')
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
