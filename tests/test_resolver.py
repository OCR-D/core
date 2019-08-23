from os import makedirs, walk
from os.path import join, exists
from shutil import copytree, rmtree
from re import sub
from tempfile import TemporaryDirectory

from tests.base import TestCase, assets, main

from ocrd.resolver import Resolver
from ocrd.workspace import Workspace
from ocrd_utils import pushd_popd
#  setOverrideLogLevel('DEBUG')


TMP_FOLDER = '/tmp/test-core-resolver'
METS_HEROLD = assets.url_of('SBB0000F29300010000/data/mets.xml')
FOLDER_KANT = assets.path_to('kant_aufklaerung_1784')
TEST_ZIP = assets.path_to('test.ocrd.zip')

# pylint: disable=redundant-unittest-assert, broad-except, deprecated-method, too-many-public-methods

class TestResolver(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.folder = join(TMP_FOLDER, 'kant_aufklaerung_1784')
        if exists(TMP_FOLDER):
            rmtree(TMP_FOLDER)
            makedirs(TMP_FOLDER)
        copytree(FOLDER_KANT, self.folder)

    def test_workspace_from_url_bad(self):
        with self.assertRaisesRegex(Exception, "Must pass mets_url and/or baseurl"):
            self.resolver.workspace_from_url(None)

    def test_workspace_from_url_tempdir(self):
        self.resolver.workspace_from_url(
            mets_basename='foo.xml',
            mets_url='https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xml')

    def test_workspace_from_url_download(self):
        with TemporaryDirectory() as dst_dir:
            self.resolver.workspace_from_url(
                mets_basename='foo.xml',
                dst_dir=dst_dir,
                download=True,
                mets_url='https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xml')

    def test_workspace_from_url_no_clobber(self):
        with self.assertRaisesRegex(Exception, "already exists but clobber_mets is false"):
            with TemporaryDirectory() as dst_dir:
                with open(join(dst_dir, 'mets.xml'), 'w') as f:
                    f.write('CONTENT')
                self.resolver.workspace_from_url(
                    dst_dir=dst_dir,
                    mets_url='https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xml')

    def test_workspace_from_url_404(self):
        with self.assertRaisesRegex(Exception, "Not found"):
            self.resolver.workspace_from_url(mets_url='https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xmlX')

    def test_workspace_from_url_rel_dir(self):
        with TemporaryDirectory() as dst_dir:
            with pushd_popd(FOLDER_KANT):
                self.resolver.workspace_from_url(None, baseurl='data', dst_dir='../../../../../../../../../../../../../../../../'+dst_dir[1:])

    def test_workspace_from_url(self):
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        #  print(METS_HEROLD)
        #  print(workspace.mets)
        input_files = workspace.mets.find_files(fileGrp='OCR-D-IMG')
        #  print [str(f) for f in input_files]
        image_file = input_files[0]
        #  print(image_file)
        f = workspace.download_file(image_file)
        self.assertEqual(f.ID, 'FILE_0001_IMAGE')
        self.assertEqual(f.local_filename, 'OCR-D-IMG/FILE_0001_IMAGE')
        #  print(f)

    # pylint: disable=protected-access
    def test_resolve_image(self):
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        input_files = workspace.mets.find_files(fileGrp='OCR-D-IMG')
        f = input_files[0]
        print(f.url)
        img_pil1 = workspace._resolve_image_as_pil(f.url)
        self.assertEqual(img_pil1.size, (2875, 3749))
        img_pil2 = workspace._resolve_image_as_pil(f.url, [[0, 0], [1, 1]])
        self.assertEqual(img_pil2.size, (1, 1))
        img_pil2 = workspace._resolve_image_as_pil(f.url, [[0, 0], [1, 1]])

    # pylint: disable=protected-access
    def test_resolve_image_grayscale(self):
        img_url = assets.url_of('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-NRM/OCR-D-IMG-NRM_0017')
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        img_pil1 = workspace._resolve_image_as_pil(img_url)
        self.assertEqual(img_pil1.size, (1457, 2083))
        img_pil2 = workspace._resolve_image_as_pil(img_url, [[0, 0], [1, 1]])
        self.assertEqual(img_pil2.size, (1, 1))

    # pylint: disable=protected-access
    def test_resolve_image_bitonal(self):
        img_url = assets.url_of('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-1BIT/OCR-D-IMG-1BIT_0017')
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        img_pil1 = workspace._resolve_image_as_pil(img_url)
        self.assertEqual(img_pil1.size, (1457, 2083))
        img_pil2 = workspace._resolve_image_as_pil(img_url, [[0, 0], [1, 1]])
        self.assertEqual(img_pil2.size, (1, 1))

    def test_workspace_from_nothing(self):
        ws1 = self.resolver.workspace_from_nothing(None)
        self.assertIsNotNone(ws1.mets)
        tmp_dir = join(TMP_FOLDER, 'from-nothing')
        ws2 = self.resolver.workspace_from_nothing(tmp_dir)
        self.assertEqual(ws2.directory, tmp_dir)
        try:
            ws2 = self.resolver.workspace_from_nothing(tmp_dir)
            self.assertTrue(False, "expecting to fail")
        except Exception as e:
            self.assertTrue('Not clobbering' in str(e))

    def test_download_to_directory_badargs_url(self):
        with self.assertRaisesRegex(Exception, "'url' must be a string"):
            self.resolver.download_to_directory(None, None)

    def test_download_to_directory_badargs_directory(self):
        with self.assertRaisesRegex(Exception, "'directory' must be a string"):
            self.resolver.download_to_directory(None, 'foo')

    def test_download_to_directory_default(self):
        tmp_dir = join(TMP_FOLDER, 'target')
        fn = self.resolver.download_to_directory(tmp_dir, 'file://' + join(self.folder, 'data/mets.xml'))
        self.assertEqual(fn, join(tmp_dir, 'file%s.data.mets.xml' % sub(r'[/_\.\-]', '.', self.folder)))

    def test_download_to_directory_basename(self):
        tmp_dir = join(TMP_FOLDER, 'target')
        fn = self.resolver.download_to_directory(tmp_dir, 'file://' + join(self.folder, 'data/mets.xml'), basename='foo')
        self.assertEqual(fn, join(tmp_dir, 'foo'))

    def test_download_to_directory_subdir(self):
        tmp_dir = join(TMP_FOLDER, 'target')
        fn = self.resolver.download_to_directory(tmp_dir, 'file://' + join(self.folder, 'data/mets.xml'), subdir='baz')
        self.assertEqual(fn, join(tmp_dir, 'baz', 'mets.xml'))

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
            self.assertEqual(f.url, '')

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
            self.assertEqual(str(ws1), 'Workspace[directory=%s, file_groups=[], files=[]]' % tempdir)

    def test_workspace_backup(self):
        with TemporaryDirectory() as tempdir:
            ws1 = self.resolver.workspace_from_nothing(directory=tempdir)
            ws1.automatic_backup = True
            ws1.save_mets()
            ws1.reload_mets()
            self.assertEqual(str(ws1), 'Workspace[directory=%s, file_groups=[], files=[]]' % tempdir)

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

if __name__ == '__main__':
    main()
