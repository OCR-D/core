# -*- coding: utf-8 -*-

from os.path import join as pjoin
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.base import TestCase, assets, main, copy_of_directory

from ocrd.resolver import Resolver
from ocrd_utils import pushd_popd, initLogging

METS_HEROLD = assets.url_of('SBB0000F29300010000/data/mets.xml')
FOLDER_KANT = assets.path_to('kant_aufklaerung_1784')

# pylint: disable=redundant-unittest-assert, broad-except, deprecated-method, too-many-public-methods

class TestResolver(TestCase):

    def setUp(self):
        initLogging()
        self.resolver = Resolver()
        super().setUp()

    def test_workspace_from_url_bad(self):
        with self.assertRaisesRegex(Exception, "Must pass 'mets_url'"):
            self.resolver.workspace_from_url(None)

    def test_workspace_from_url_tempdir(self):
        self.resolver.workspace_from_url(
            mets_basename='foo.xml',
            mets_url='https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xml')

    def test_workspace_from_url_download(self):
        url_src = 'https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xml'
        #url_src = 'http://digital.bibliothek.uni-halle.de/hd/oai/?verb=GetRecord&metadataPrefix=mets&mode=xml&identifier=9049'
        with TemporaryDirectory() as dst_dir:
            self.resolver.workspace_from_url(
                url_src,
                mets_basename='foo.xml',
                dst_dir=dst_dir,
                download=True)

    def test_workspace_from_url_no_clobber(self):
        with TemporaryDirectory() as dst_dir:
            src_mets = Path(assets.path_to('kant_aufklaerung_1784-binarized/data/mets.xml'))
            dst_mets = Path(dst_dir, 'mets.xml')
            dst_mets.write_text(src_mets.read_text())
            self.resolver.workspace_from_url(
                    'https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xml',
                    clobber_mets=False,
                    dst_dir=dst_dir)

    def test_workspace_from_url_404(self):
        with self.assertRaisesRegex(Exception, "HTTP request failed"):
            self.resolver.workspace_from_url(mets_url='https://raw.githubusercontent.com/OCR-D/assets/master/data/kant_aufklaerung_1784/data/mets.xmlX')

    def test_workspace_from_url_rel_dir(self):
        with TemporaryDirectory() as dst_dir:
            bogus_dst_dir = '../../../../../../../../../../../../../../../../%s'  % dst_dir[1:]
            with pushd_popd(FOLDER_KANT):
                ws1 = self.resolver.workspace_from_url('data/mets.xml', dst_dir=bogus_dst_dir)
                self.assertEqual(ws1.mets_target, pjoin(dst_dir, 'mets.xml'))
                self.assertEqual(ws1.directory, dst_dir)

    def test_workspace_from_url0(self):
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        #  print(workspace.mets)
        input_files = workspace.mets.find_all_files(fileGrp='OCR-D-IMG')
        #  print [str(f) for f in input_files]
        image_file = input_files[0]
        #  print(image_file)
        f = workspace.download_file(image_file)
        self.assertEqual('%s.tif' % f.ID, 'FILE_0001_IMAGE.tif')
        self.assertEqual(f.local_filename, 'OCR-D-IMG/FILE_0001_IMAGE.tif')
        #  print(f)

    # pylint: disable=protected-access
    def test_resolve_image0(self):
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        input_files = workspace.mets.find_all_files(fileGrp='OCR-D-IMG')
        f = input_files[0]
        print(f.url)
        img_pil1 = workspace._resolve_image_as_pil(f.url)
        print(f.url)
        self.assertEqual(img_pil1.size, (2875, 3749))
        img_pil2 = workspace._resolve_image_as_pil(f.url, [[0, 0], [1, 1]])
        print(f.url)
        self.assertEqual(img_pil2.size, (1, 1))
        img_pil2 = workspace._resolve_image_as_pil(f.url, [[0, 0], [1, 1]])

    # pylint: disable=protected-access
    def test_resolve_image_grayscale(self):
        img_url = assets.url_of('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-NRM/OCR-D-IMG-NRM_0017.png')
        workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))
        img_pil1 = workspace.resolve_image_as_pil(img_url)
        self.assertEqual(img_pil1.size, (1457, 2083))
        img_pil2 = workspace._resolve_image_as_pil(img_url, [[0, 0], [1, 1]])
        self.assertEqual(img_pil2.size, (1, 1))

    # pylint: disable=protected-access
    def test_resolve_image_bitonal(self):
        img_url = assets.url_of('kant_aufklaerung_1784-binarized/data/OCR-D-IMG-1BIT/OCR-D-IMG-1BIT_0017.png')
        workspace = self.resolver.workspace_from_url(METS_HEROLD)
        img_pil1 = workspace._resolve_image_as_pil(img_url)
        self.assertEqual(img_pil1.size, (1457, 2083))
        img_pil2 = workspace._resolve_image_as_pil(img_url, [[0, 0], [1, 1]])
        self.assertEqual(img_pil2.size, (1, 1))

    def test_workspace_from_nothing(self):
        ws1 = self.resolver.workspace_from_nothing(None)
        self.assertIsNotNone(ws1.mets)

    def test_workspace_from_nothing_makedirs(self):
        with TemporaryDirectory() as tempdir:
            non_existant_dir = Path(tempdir, 'target')
            ws1 = self.resolver.workspace_from_nothing(non_existant_dir)
            self.assertEqual(ws1.directory, non_existant_dir)

    def test_workspace_from_nothing_noclobber(self):
        with TemporaryDirectory() as tempdir:
            ws2 = self.resolver.workspace_from_nothing(tempdir)
            self.assertEqual(ws2.directory, tempdir)
            with self.assertRaisesRegex(Exception, "METS 'mets.xml' already exists in '%s' and clobber_mets not set" % tempdir):
                # must fail because tempdir was just created
                self.resolver.workspace_from_nothing(tempdir)

    def test_download_to_directory_badargs_url(self):
        with self.assertRaisesRegex(Exception, "'url' must be a string"):
            self.resolver.download_to_directory(None, None)

    def test_download_to_directory_badargs_directory(self):
        with self.assertRaisesRegex(Exception, "'directory' must be a string"):
            self.resolver.download_to_directory(None, 'foo')

    def test_download_to_directory_default(self):
        with copy_of_directory(FOLDER_KANT) as src:
            with TemporaryDirectory() as dst:
                fn = self.resolver.download_to_directory(dst, pjoin(src, 'data/mets.xml'))
                self.assertEqual(fn, 'mets.xml')
                self.assertTrue(Path(dst, fn).exists())

    def test_download_to_directory_basename(self):
        with copy_of_directory(FOLDER_KANT) as src:
            with TemporaryDirectory() as dst:
                fn = self.resolver.download_to_directory(dst, pjoin(src, 'data/mets.xml'), basename='foo')
                self.assertEqual(fn, 'foo')
                self.assertTrue(Path(dst, fn).exists())

    def test_download_to_directory_subdir(self):
        with copy_of_directory(FOLDER_KANT) as src:
            with TemporaryDirectory() as dst:
                fn = self.resolver.download_to_directory(dst, pjoin(src, 'data/mets.xml'), subdir='baz')
                self.assertEqual(fn, pjoin('baz', 'mets.xml'))
                self.assertTrue(Path(dst, fn).exists())

if __name__ == '__main__':
    main(__file__)
