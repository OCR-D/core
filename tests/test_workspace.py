from os import walk
from os.path import join, exists, abspath, basename, dirname
from tempfile import TemporaryDirectory
from shutil import copyfile
from pathlib import Path

from tests.base import TestCase, assets, main

from ocrd.resolver import Resolver
from ocrd.workspace import Workspace

#  from ocrd_utils import setOverrideLogLevel
#  setOverrideLogLevel('DEBUG')

TMP_FOLDER = '/tmp/test-core-workspace'
SRC_METS = assets.path_to('kant_aufklaerung_1784/data/mets.xml')

SAMPLE_FILE_FILEGRP = 'OCR-D-IMG'
SAMPLE_FILE_ID = 'INPUT_0017'
SAMPLE_FILE_URL = join(SAMPLE_FILE_FILEGRP, '%s.tif' % SAMPLE_FILE_ID)

class TestWorkspace(TestCase):

    def setUp(self):
        self.resolver = Resolver()

    def test_workspace_add_file(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            fpath = join(tempdir, 'ID1.tif')
            ws1.add_file(
                'GRP',
                ID='ID1',
                mimetype='image/tiff',
                content='CONTENT',
                local_filename=fpath
            )
            f = ws1.mets.find_files()[0]
            self.assertEqual(f.ID, 'ID1')
            self.assertEqual(f.mimetype, 'image/tiff')
            self.assertEqual(f.url, fpath)
            self.assertEqual(f.local_filename, fpath)
            self.assertTrue(exists(fpath))

    def test_workspace_add_file_basename_no_content(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            ws1.add_file('GRP', ID='ID1', mimetype='image/tiff')
            f = ws1.mets.find_files()[0]
            self.assertEqual(f.url, None)

    def test_workspace_add_file_binary_content(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            fpath = join(tempdir, 'subdir', 'ID1.tif')
            ws1.add_file('GRP', ID='ID1', content=b'CONTENT', local_filename=fpath, url='http://foo/bar')
            self.assertTrue(exists(fpath))

    def test_workspacec_add_file_content_wo_local_filename(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            with self.assertRaisesRegex(Exception, "'content' was set but no 'local_filename'"):
                ws1.add_file('GRP', ID='ID1', content=b'CONTENT')


    def test_workspace_str(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            ws1.save_mets()
            ws1.reload_mets()
            self.assertEqual(str(ws1), 'Workspace[directory=%s, baseurl=None, file_groups=[], files=[]]' % tempdir)

    def test_workspace_backup(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            ws1.automatic_backup = True
            ws1.save_mets()
            ws1.reload_mets()
            self.assertEqual(str(ws1), 'Workspace[directory=%s, baseurl=None, file_groups=[], files=[]]' % tempdir)

    def test_download_url0(self):
        with TemporaryDirectory() as directory:
            ws1 = self.resolver.workspace_from_nothing(directory)
            fn = ws1.download_url(abspath(__file__))
            self.assertEqual(fn, join('TEMP', basename(__file__)))

    def test_download_url_without_baseurl(self):
        with TemporaryDirectory() as tempdir:
            dst_mets = join(tempdir, 'mets.xml')
            copyfile(SRC_METS, dst_mets)
            ws1 = self.resolver.workspace_from_url(dst_mets)
            with self.assertRaisesRegex(Exception, "Already tried prepending baseurl '%s'" % tempdir):
                ws1.download_url(SAMPLE_FILE_URL)

    def test_download_url_with_baseurl(self):
        with TemporaryDirectory() as tempdir:
            dst_mets = join(tempdir, 'mets.xml')
            copyfile(SRC_METS, dst_mets)
            ws1 = self.resolver.workspace_from_url(dst_mets, src_baseurl=dirname(SRC_METS))
            f = Path(ws1.download_url(SAMPLE_FILE_URL))
            self.assertEqual(f, Path('TEMP', '%s.tif' % SAMPLE_FILE_ID))
            self.assertTrue(Path(ws1.directory, f).exists())

    def test_227_1(self):
        def find_recursive(root):
            ret = []
            for _, _, f in walk(root):
                for file in f:
                    ret.append(file)
            return ret
        with TemporaryDirectory() as wsdir:
            with open(assets.path_to('SBB0000F29300010000/data/mets_one_file.xml'), 'r') as f_in:
                with open(join(wsdir, 'mets.xml'), 'w') as f_out:
                    f_out.write(f_in.read())
            self.assertEqual(len(find_recursive(wsdir)), 1)
            ws1 = Workspace(self.resolver, wsdir)
            for file in ws1.mets.find_files():
                ws1.download_file(file)
            self.assertEqual(len(find_recursive(wsdir)), 2)
            self.assertTrue(exists(join(wsdir, 'OCR-D-IMG/FILE_0005_IMAGE.tif')))

    #  def test_remove(self):
    #      with TemporaryDirectory() as tempdir:
    #          dst_dir =
    #          ws1 = self.resolver.workspace_from_url(SRC_METS, dst_dir=dst_dir)
    #          res = ws1.download_url(SAMPLE_FILE_URL)
    #          print('>>>>>> %s' % res)
    #          ocrd_file = ws1.remove_file(SAMPLE_FILE_ID)
    #          print(ocrd_file)
    #          import os
    #          self.assertTrue(exists(join(ws1.directory, ocrd_file.local_filename)))
    #          #  with copy_of_directory(FOLDER_KANT) as tempdir:

if __name__ == '__main__':
    main()
