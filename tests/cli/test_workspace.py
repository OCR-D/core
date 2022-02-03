from os.path import join, exists
from pathlib import Path
from filecmp import dircmp
from shutil import copytree
from tempfile import TemporaryDirectory
from io import StringIO
from contextlib import contextmanager
import sys

from click.testing import CliRunner
import pytest

# pylint: disable=import-error, no-name-in-module
from tests.base import CapturingTestCase as TestCase, assets, copy_of_directory, main

from ocrd_utils import initLogging, pushd_popd, setOverrideLogLevel, disableLogging
from ocrd.cli.workspace import workspace_cli
from ocrd import Resolver

@contextmanager
def mock_stdin(inp):
    old_stdin = sys.stdin
    sys.stdin = StringIO(inp)
    yield
    sys.stdin = old_stdin

class TestCli(TestCase):

    def setUp(self):
        super().setUp()
        disableLogging()
        self.maxDiff = None
        self.resolver = Resolver()
        self.runner = CliRunner(mix_stderr=False)

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

            result = self.runner.invoke(workspace_cli, [
                '-d',
                tempdir,
                'remove',
                '--keep-file',
                ID
            ])
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

            result = self.runner.invoke(workspace_cli, [
                '-d',
                tempdir,
                'remove',
                '--force',
                ID
            ])
            self.assertEqual(result.exit_code, 0)

            # File should have been deleted
            self.assertFalse(exists(content_file))

    def test_add_url(self):
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        mimetype = 'image/tiff'
        url = 'http://remote/file.tif'
        with TemporaryDirectory() as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.save_mets()
            result = self.runner.invoke(workspace_cli, [
                '-d', tempdir,
                'add',
                '--file-grp', file_grp,
                '--page-id', page_id,
                '--file-id', ID,
                '--mimetype', mimetype,
                url])
            self.assertEqual(result.exit_code, 0)
            ws.reload_mets()
            f = ws.mets.find_all_files()[0]
            self.assertEqual(f.url, url)

    def test_add_nonexisting_checked(self):
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        mimetype = 'image/tiff'
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.save_mets()
            exit_code, out, err = self.invoke_cli(workspace_cli, [
                '-d', tempdir,
                'add',
                '-C',
                '--file-grp', file_grp,
                '--page-id', page_id,
                '--file-id', ID,
                '--mimetype', mimetype,
                'does-not-exist.xml'])
            self.assertEqual(exit_code, 1)
            self.assertIn("File 'does-not-exist.xml' does not exist, halt execution!", err)

    def test_add_519(self):
        """
        https://github.com/OCR-D/core/issues/519
        """
        with TemporaryDirectory() as tempdir:
            wsdir = Path(tempdir, "workspace")
            wsdir.mkdir()
            srcdir = Path(tempdir, "source")
            srcdir.mkdir()
            srcfile = Path(srcdir, "srcfile.jpg")
            srcfile_content = 'foo'
            srcfile.write_text(srcfile_content)
            with pushd_popd(str(wsdir)):
                exit_code, out, err = self.invoke_cli(workspace_cli, ['init'])
                exit_code, out, err = self.invoke_cli(workspace_cli, [
                    'add',
                    '-m', 'image/jpg',
                    '-G', 'MAX',
                    '-i', 'IMG_MAX_1818975',
                    '-C',
                    str(srcfile)
                    ])
                # print(out, err)
                self.assertEqual(exit_code, 0)
                self.assertTrue(Path(wsdir, 'MAX', 'srcfile.jpg').exists())
                self.assertEqual(Path(wsdir, 'MAX', 'srcfile.jpg').read_text(), srcfile_content)

    def test_add_existing_checked(self):
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        mimetype = 'image/tiff'
        with TemporaryDirectory() as tempdir:
            content_file = join(tempdir, 'test.tif')
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.save_mets()
            with open(content_file, 'w') as f:
                f.write('x')
            result = self.runner.invoke(workspace_cli, [
                '-d', tempdir,
                'add',
                '-C',
                '--file-grp', file_grp,
                '--page-id', page_id,
                '--file-id', ID,
                '--mimetype', mimetype,
                content_file])
            self.assertEqual(result.exit_code, 0)
            ws.reload_mets()
            f = ws.mets.find_all_files()[0]
            self.assertEqual(f.url, 'test.tif')


    def test_find_all_files(self):
        with TemporaryDirectory() as tempdir:
            wsdir = join(tempdir, 'ws')
            copytree(assets.path_to('SBB0000F29300010000/data'), wsdir)
            with pushd_popd(wsdir):
                result = self.runner.invoke(workspace_cli, ['find', '-G', 'OCR-D-IMG-BIN', '-k', 'fileGrp'])
                self.assertEqual(result.output, 'OCR-D-IMG-BIN\nOCR-D-IMG-BIN\n')
                self.assertEqual(result.exit_code, 0)

    def test_prune_files(self):
        with TemporaryDirectory() as tempdir:
            copytree(assets.path_to('SBB0000F29300010000/data'), join(tempdir, 'ws'))

            ws1 = self.resolver.workspace_from_url(join(tempdir, 'ws', 'mets.xml'))
            self.assertEqual(len(ws1.mets.find_all_files()), 35)

            result = self.runner.invoke(workspace_cli, ['-d', join(tempdir, 'ws'), 'prune-files'])
            self.assertEqual(result.exit_code, 0)

            ws2 = self.resolver.workspace_from_url(join(tempdir, 'ws', 'mets.xml'))
            self.assertEqual(len(ws2.mets.find_all_files()), 7)

    def test_clone_into_nonexisting_dir(self):
        """
        https://github.com/OCR-D/core/issues/330
        """
        with TemporaryDirectory() as tempdir:
            clone_to = join(tempdir, 'non-existing-dir')
            result = self.runner.invoke(workspace_cli, [
                'clone',
                '--download',
                assets.path_to('scribo-test/data/mets.xml'),
                clone_to
            ])
            self.assertEqual(result.exit_code, 0)

    def test_remove_file_group(self):
        """
        Test removal of filegrp
        """
        with TemporaryDirectory() as tempdir:
            wsdir = join(tempdir, 'ws')
            copytree(assets.path_to('SBB0000F29300010000/data'), wsdir)
            file_group = 'OCR-D-GT-PAGE'
            file_path = Path(tempdir, 'ws', file_group, 'FILE_0002_FULLTEXT.xml')
            self.assertTrue(file_path.exists())

            workspace = self.resolver.workspace_from_url(join(wsdir, 'mets.xml'))
            self.assertEqual(workspace.directory, wsdir)

            with self.assertRaisesRegex(Exception, "not empty"):
                workspace.remove_file_group(file_group)

            self.assertTrue(file_path.exists())
            self.assertEqual(len(workspace.mets.file_groups), 17)
            self.assertEqual(len(workspace.mets.find_all_files()), 35)

            workspace.remove_file_group(file_group, recursive=True, force=True)

            self.assertEqual(len(workspace.mets.file_groups), 16)
            self.assertEqual(len(workspace.mets.find_all_files()), 33)
            self.assertFalse(file_path.exists())

            # TODO ensure empty dirs are removed
            # self.assertFalse(file_path.parent.exists())


    def test_clone_relative(self):
        # Create a relative path to trigger make sure #319 is gone
        src_path = str(Path(assets.path_to('kant_aufklaerung_1784/data/mets.xml')).relative_to(Path.cwd()))
        with TemporaryDirectory() as tempdir:
            result = self.runner.invoke(workspace_cli, ['clone', '-a', src_path, tempdir])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(exists(join(tempdir, 'OCR-D-GT-PAGE/PAGE_0017_PAGE.xml')))

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

    def test_find_all_files_multiple_physical_pages_for_fileids(self):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as tempdir:
            result = self.runner.invoke(workspace_cli, ['-d', tempdir, 'find', '--page-id', 'PHYS_0005,PHYS_0005', '-k', 'url'])
            self.assertEqual(result.stdout, 'OCR-D-IMG/FILE_0005_IMAGE.tif\n')
            self.assertEqual(result.exit_code, 0)
            result = self.runner.invoke(workspace_cli, ['-d', tempdir, 'find', '--page-id', 'PHYS_0005,PHYS_0001', '-k', 'url'])
            self.assertEqual(len(result.stdout.split('\n')), 19)

    def test_mets_basename(self):
        with TemporaryDirectory() as tempdir:
            with pushd_popd(tempdir):
                result = self.runner.invoke(workspace_cli, ['-m', 'foo.xml', 'init'])
                self.assertEqual(result.exit_code, 0)
                self.assertTrue(exists('foo.xml'))
                self.assertFalse(exists('mets.xml'))

    def test_mets_basename_and_mets(self):
        with pushd_popd(tempdir=True) as tempdir:
            with self.assertRaisesRegex(ValueError, "Use either --mets or --mets-basename, not both"):
                self.invoke_cli(workspace_cli, ['-m', 'foo.xml', '-M', 'not-foo.xml', 'init'])

    def test_mets_basename_and_not_mets(self):
        with pushd_popd(tempdir=True) as tempdir:
            _, out, err = self.invoke_cli(workspace_cli, ['-d', 'foo', '-M', 'not-foo.xml', 'init'])
            self.assertEqual(out, join(tempdir, 'foo') + '\n')
            self.assertIn('--mets-basename is deprecated', err)

    def test_mets_get_id_set_id(self):
        with pushd_popd(tempdir=True):
            self.invoke_cli(workspace_cli, ['init'])
            disableLogging()
            mets_id = 'foo123'
            self.invoke_cli(workspace_cli, ['set-id', mets_id])
            disableLogging()
            _, out, _ = self.invoke_cli(workspace_cli, ['get-id'])
            self.assertEqual(out, mets_id + '\n')

    def test_mets_directory_incompatible(self):
          with pushd_popd(tempdir=True) as tempdir:
            with self.assertRaisesRegex(ValueError, "inconsistent with --directory"):
                self.invoke_cli(workspace_cli, ['-d', 'foo', '-m', '/somewhere/else', 'init'])

    def test_mets_directory_http(self):
          with pushd_popd(tempdir=True) as tempdir:
            with self.assertRaisesRegex(ValueError, r"--mets is an http\(s\) URL but no --directory was given"):
                self.invoke_cli(workspace_cli, ['-m', 'https://foo.bar/bla', 'init'])

    def test_bulk_add0(self):
        NO_FILES=100
        with TemporaryDirectory() as srcdir:
            Path(srcdir, "OCR-D-IMG").mkdir()
            Path(srcdir, "OCR-D-PAGE").mkdir()
            for i in range(NO_FILES):
                Path(srcdir, "OCR-D-IMG", "page_%04d.tif" % i).write_text('')
            for i in range(NO_FILES):
                Path(srcdir, "OCR-D-PAGE", "page_%04d.xml" % i).write_text('')
            with TemporaryDirectory() as wsdir:
                with pushd_popd(wsdir):
                    ws = self.resolver.workspace_from_nothing(directory=wsdir)
                    exit_code, out, err = self.invoke_cli(workspace_cli, [
                        'bulk-add',
                        '--ignore',
                        '--regex', r'^.*/(?P<fileGrp>[^/]+)/page_(?P<pageid>.*)\.(?P<ext>[^\.]*)$',
                        '--url', '{{ fileGrp }}/FILE_{{ pageid }}.{{ ext }}',
                        '--file-id', 'FILE_{{ fileGrp }}_{{ pageid }}',
                        '--page-id', 'PHYS_{{ pageid }}',
                        '--file-grp', '{{ fileGrp }}',
                        '%s/*/*' % srcdir
                    ])
                    # print('exit_code', exit_code)
                    # print('out', out)
                    # print('err', err)
                    ws.reload_mets()
                    self.assertEqual(len(ws.mets.file_groups), 2)
                    self.assertEqual(len(ws.mets.find_all_files()), 2 * NO_FILES)
                    self.assertEqual(len(ws.mets.find_all_files(mimetype='image/tiff')), NO_FILES)
                    self.assertEqual(len(ws.mets.find_all_files(ID='//FILE_OCR-D-IMG_000.*')), 10)
                    self.assertEqual(len(ws.mets.find_all_files(ID='//FILE_.*_000.*')), 20)
                    self.assertEqual(len(ws.mets.find_all_files(pageId='PHYS_0001')), 2)
                    self.assertEqual(ws.mets.find_all_files(ID='FILE_OCR-D-PAGE_0001')[0].url, 'OCR-D-PAGE/FILE_0001.xml')

    def test_bulk_add_missing_param(self):
        with pushd_popd(tempdir=True) as wsdir:
            ws = self.resolver.workspace_from_nothing(directory=wsdir)
            with pytest.raises(ValueError, match=r"OcrdFile attribute 'pageId' unset"):
                _, out, err = self.invoke_cli(workspace_cli, [
                    'bulk-add',
                    '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<fileid>.*) (?P<src>.*) (?P<url>.*) (?P<mimetype>.*)',
                    '-G', '{{ filegrp }}',
                    # '-g', '{{ pageid }}', # XXX skip --page-id
                    '-i', '{{ fileid }}',
                    '-m', '{{ mimetype }}',
                    '-u', "{{ url }}",
                    'a b c d e f', '1 2 3 4 5 6'])
                print('out', out)
                print('err', err)
                assert 0

    def test_bulk_add_gen_id(self):
        with pushd_popd(tempdir=True) as wsdir:
            ws = self.resolver.workspace_from_nothing(directory=wsdir)
            Path(wsdir, 'c').write_text('')
            _, out, err = self.invoke_cli(workspace_cli, [
                'bulk-add',
                '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<src>.*) (?P<url>.*) (?P<mimetype>.*)',
                '-G', '{{ filegrp }}',
                '-g', '{{ pageid }}',
                '-S', '{{ src }}',
                # '-i', '{{ fileid }}',  # XXX skip --file-id
                '-m', '{{ mimetype }}',
                '-u', "{{ url }}",
                'a b c d e'])
            ws.reload_mets()
            assert next(ws.mets.find_files()).ID == 'a.b.c.d.e'
            assert next(ws.mets.find_files()).url == 'd'

    def test_bulk_add_derive_url(self):
        with pushd_popd(tempdir=True) as wsdir:
            ws = self.resolver.workspace_from_nothing(directory=wsdir)
            Path(wsdir, 'srcdir').mkdir()
            Path(wsdir, 'srcdir', 'src.xml').write_text('')
            _, out, err = self.invoke_cli(workspace_cli, [
                'bulk-add',
                '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<src>.*)',
                '-G', '{{ filegrp }}',
                '-g', '{{ pageid }}',
                '-S', '{{ src }}',
                # '-u', "{{ url }}", # XXX skip --url
                'p0001 SEG srcdir/src.xml'])
            # print('out', out)
            # print('err', err)
            ws.reload_mets()
            assert next(ws.mets.find_files()).url == 'srcdir/src.xml'

    def test_bulk_add_stdin(self):
        resolver = Resolver()
        with pushd_popd(tempdir=True) as wsdir:
            ws = resolver.workspace_from_nothing(directory=wsdir)
            Path(wsdir, 'BIN').mkdir()
            Path(wsdir, 'BIN/FILE_0001_BIN.IMG-wolf.png').write_text('')
            Path(wsdir, 'BIN/FILE_0002_BIN.IMG-wolf.png').write_text('')
            Path(wsdir, 'BIN/FILE_0001_BIN.xml').write_text('')
            Path(wsdir, 'BIN/FILE_0002_BIN.xml').write_text('')
            with mock_stdin(
                    'PHYS_0001 BIN FILE_0001_BIN.IMG-wolf BIN/FILE_0001_BIN.IMG-wolf.png BIN/FILE_0001_BIN.IMG-wolf.png image/png\n'
                    'PHYS_0002 BIN FILE_0002_BIN.IMG-wolf BIN/FILE_0002_BIN.IMG-wolf.png BIN/FILE_0002_BIN.IMG-wolf.png image/png\n'
                    'PHYS_0001 BIN FILE_0001_BIN BIN/FILE_0001_BIN.xml BIN/FILE_0001_BIN.xml application/vnd.prima.page+xml\n'
                    'PHYS_0002 BIN FILE_0002_BIN BIN/FILE_0002_BIN.xml BIN/FILE_0002_BIN.xml application/vnd.prima.page+xml\n'):
                assert len(ws.mets.file_groups) == 0
                exit_code, out, err = self.invoke_cli(workspace_cli, [
                    'bulk-add',
                    '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<fileid>.*) (?P<src>.*) (?P<dest>.*) (?P<mimetype>.*)',
                    '-G', '{{ filegrp }}',
                    '-g', '{{ pageid }}',
                    '-i', '{{ fileid }}',
                    '-m', '{{ mimetype }}',
                    '-u', "{{ dest }}",
                    '-'])
                ws.reload_mets()
                assert len(ws.mets.file_groups) == 1
                assert len(list(ws.mets.find_files())) == 4
                f = next(ws.mets.find_files())
                assert f.mimetype == 'image/png'
                assert f.ID == 'FILE_0001_BIN.IMG-wolf'
                assert f.url == 'BIN/FILE_0001_BIN.IMG-wolf.png'

if __name__ == '__main__':
    main(__file__)
