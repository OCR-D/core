from os.path import join, exists
from pathlib import Path
from filecmp import dircmp
from shutil import copytree
from tempfile import TemporaryDirectory

from click.testing import CliRunner

# pylint: disable=import-error, no-name-in-module
from tests.base import TestCase, main, assets, copy_of_directory

from ocrd_utils import initLogging
from ocrd.cli.workspace import workspace_cli
from ocrd.resolver import Resolver

class TestCli(TestCase):


    def setUp(self):
        self.maxDiff = None
        self.resolver = Resolver()
        initLogging()
        self.runner = CliRunner()

    def test_add(self):
        """
        Ensure that `ocrd workspace add` does the right thing
        """
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        content = 'x'
        mimetype = 'image/tiff'
        local_filename = join(file_grp, 'foo.xml')

        #  mets_api = None
        #  mets_cli = None

        with TemporaryDirectory() as tempdir:
            ws_api = self.resolver.workspace_from_nothing(directory=tempdir)
            ws_api.add_file(
                file_grp,
                ID=ID,
                content=content,
                pageId=page_id,
                mimetype=mimetype,
                local_filename=local_filename
            )
            ws_api.save_mets()
            #  mets_api = ws_api.mets.to_xml().decode('utf8')

        with TemporaryDirectory() as tempdir:
            ws_api = self.resolver.workspace_from_nothing(directory=tempdir)
            content_file = join(tempdir, 'testfile')
            with open(content_file, 'w') as f:
                f.write(content)
                result = self.runner.invoke(workspace_cli, [
                    '-d', tempdir,
                    'add',
                    '--file-grp', file_grp,
                    '--page-id', page_id,
                    '--file-id', ID,
                    '--mimetype', mimetype,
                    content_file
                ])
                self.assertEqual(result.exit_code, 0)
                # TODO too complex to compare :(
                #  with open(join(tempdir, 'mets.xml')) as f:
                #      mets_cli = f.read()
                #  print(mets_api)
                #  print(mets_cli)
                #  self.assertEqual(mets_api, mets_cli)
                #  print(result.output)
                #  with open(join(tempdir, 'mets.xml')) as f:
                #      print(f.read())
                self.assertEqual(result.exit_code, 0)


    def test_add_remove(self):
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        content = 'x'
        mimetype = 'image/tiff'
        with TemporaryDirectory() as tempdir:
            content_file = join(tempdir, 'testfile')
            with open(content_file, 'w') as f:
                f.write(content)

            result = self.runner.invoke(workspace_cli, ['init', tempdir])
            self.assertEqual(result.exit_code, 0)

            result = self.runner.invoke(workspace_cli, [
                '-d', tempdir,
                'add',
                '--file-grp', file_grp,
                '--page-id', page_id,
                '--file-id', ID,
                '--mimetype', mimetype,
                content_file
            ])
            self.assertEqual(result.exit_code, 0)

            result = self.runner.invoke(workspace_cli, ['-d', tempdir, 'remove', ID])
            self.assertEqual(result.exit_code, 0)

            # File should still exist
            self.assertTrue(exists(content_file))

    def test_add_remove_force(self):
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        content = 'x'
        mimetype = 'image/tiff'
        with TemporaryDirectory() as tempdir:
            content_file = join(tempdir, 'testfile')
            with open(content_file, 'w') as f:
                f.write(content)

            result = self.runner.invoke(workspace_cli, ['init', tempdir])
            self.assertEqual(result.exit_code, 0)

            result = self.runner.invoke(workspace_cli, [
                '-d', tempdir,
                'add',
                '--file-grp', file_grp,
                '--page-id', page_id,
                '--file-id', ID,
                '--mimetype', mimetype,
                content_file
            ])
            self.assertEqual(result.exit_code, 0)

            result = self.runner.invoke(workspace_cli, ['-d', tempdir, 'remove', '--force', ID])
            print(result)
            print(result.output)
            self.assertEqual(result.exit_code, 0)

            # File should have been deleted
            self.assertFalse(exists(content_file))

    def test_prune_files(self):
        with TemporaryDirectory() as tempdir:
            copytree(assets.path_to('SBB0000F29300010000/data'), join(tempdir, 'ws'))

            ws1 = self.resolver.workspace_from_url(join(tempdir, 'ws', 'mets.xml'))
            self.assertEqual(len(ws1.mets.find_files()), 35)

            result = self.runner.invoke(workspace_cli, ['-d', join(tempdir, 'ws'), 'prune-files'])
            self.assertEqual(result.exit_code, 0)

            ws2 = self.resolver.workspace_from_url(join(tempdir, 'ws', 'mets.xml'))
            self.assertEqual(len(ws2.mets.find_files()), 7)

    def test_remove_file_group(self):
        """
        Test removal of filegrp
        """
        with TemporaryDirectory() as tempdir:
            wsdir = join(tempdir, 'ws')
            copytree(assets.path_to('SBB0000F29300010000/data'), wsdir)
            file_group = 'OCR-D-GT-PAGE'
            file_path = join(tempdir, 'ws', file_group, 'FILE_0002_FULLTEXT.xml')
            self.assertTrue(exists(file_path))

            workspace = self.resolver.workspace_from_url(join(wsdir, 'mets.xml'))
            self.assertEqual(workspace.directory, wsdir)

            with self.assertRaisesRegex(Exception, "not empty"):
                workspace.remove_file_group(file_group)
            with self.assertRaisesRegex(Exception, "force without recursive"):
                workspace.remove_file_group(file_group, force=True)

            self.assertTrue(exists(file_path))
            self.assertEqual(len(workspace.mets.file_groups), 17)
            self.assertEqual(len(workspace.mets.find_files()), 35)

            workspace.remove_file_group(file_group, recursive=True, force=True)

            self.assertEqual(len(workspace.mets.file_groups), 16)
            self.assertEqual(len(workspace.mets.find_files()), 33)
            self.assertFalse(exists(file_path))

    def test_copy_vs_clone(self):
        src_dir = assets.path_to('kant_aufklaerung_1784/data')
        with TemporaryDirectory() as tempdir:
            # cloned without download
            shallowcloneddir = join(tempdir, 'cloned-shallow')
            # cloned with download
            fullcloneddir = join(tempdir, 'cloned-all')
            # copied
            copieddir = join(tempdir, 'copied')

            Path(fullcloneddir).mkdir()
            Path(shallowcloneddir).mkdir()


            result = self.runner.invoke(workspace_cli, ['clone', join(src_dir, 'mets.xml'), shallowcloneddir])
            self.assertEqual(result.exit_code, 0)

            result = self.runner.invoke(workspace_cli, ['clone', '-a', join(src_dir, 'mets.xml'), fullcloneddir])
            self.assertEqual(result.exit_code, 0)

            with copy_of_directory(src_dir, copieddir):
                shallow_vs_copied = dircmp(shallowcloneddir, copieddir)
                self.assertEqual(set(shallow_vs_copied.right_only), set(['OCR-D-GT-ALTO', 'OCR-D-GT-PAGE', 'OCR-D-IMG']))

                full_vs_copied = dircmp(fullcloneddir, copieddir)
                #  print(full_vs_copied)
                #  from ocrd_utils import pushd_popd
                #  with pushd_popd(tempdir):
                    #  import os
                    #  os.system("diff %s/mets.xml %s/mets.xml" % (fullcloneddir, copieddir))
                # XXX mets.xml will not have the exact same content because
                # URLs that are actually files will be marked up as such with
                # @LOCTYPE/@OTHERLOCTYPE
                #  self.assertEqual(full_vs_copied.diff_files, [])
                self.assertEqual(full_vs_copied.left_only, [])
                self.assertEqual(full_vs_copied.right_only, [])

if __name__ == '__main__':
    main()
