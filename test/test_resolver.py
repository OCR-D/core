import os
from shutil import copytree, rmtree

from ocrd.model import OcrdExif
from ocrd.resolver import Resolver
from test.base import TestCase, assets, main

TMP_FOLDER = '/tmp/test-pyocrd-resolver'
METS_HEROLD = assets.url_of('SBB0000F29300010000/mets.xml')
FOLDER_KANT = assets.url_of('kant_aufklaerung_1784')[len('file://'):]
TEST_ZIP = assets.url_of('test.ocrd.zip')[len('file://'):]

class TestResolver(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.folder = os.path.join(TMP_FOLDER, 'kant_aufklaerung_1784')
        if os.path.exists(TMP_FOLDER):
            rmtree(TMP_FOLDER)
            os.makedirs(TMP_FOLDER)
        copytree(FOLDER_KANT, self.folder)

    def test_unpack_workspace(self):
        workspace = self.resolver.unpack_workspace_from_filename(TEST_ZIP)
        files = workspace.mets.find_files(mimetype='image/tiff')
        self.assertEqual(len(files), 2, '2 TIF')
        for f in files:
            workspace.download_file(f)
        print([OcrdExif.from_filename(f.local_filename).to_xml() for f in files])

    def test_workspace_from_folder(self):
        workspace = self.resolver.workspace_from_folder(self.folder, clobber_mets=True)
        #  print([ f.url for f in workspace.mets.find_files() ])
        self.assertEqual(len(workspace.mets.find_files()), 6, '6 files total')

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
        #  print(f)

    def test_pack_workspace(self):
        workspace = self.resolver.workspace_from_folder(self.folder, clobber_mets=True)
        zpath = self.resolver.pack_workspace(workspace, zpath='/tmp/test-pyocrd-resolver.zip')
        print(zpath)

if __name__ == '__main__':
    main()
