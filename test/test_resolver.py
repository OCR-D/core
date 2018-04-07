from ocrd.resolver import Resolver
from test.base import TestCase, assets, main
METS_HEROLD = assets.url_of('SBB0000F29300010000/mets.xml')
FOLDER_KANT = assets.url_of('kant_aufklaerung_1784')[len('file://'):]

class TestResolver(TestCase):

    def setUp(self):
        self.resolver = Resolver(cache_enabled=True)

    def test_workspace_from_folder(self):
        workspace = self.resolver.workspace_from_folder(FOLDER_KANT, clobber_mets=True)
        #  print(FOLDER_KANT)
        print(workspace)
        #  input_files = workspace.mets.find_files(fileGrp='OCR-D-IMG')
        #  print([str(f) for f in input_files])
        #  image_file = input_files[0]
        #  print(image_file)
        #  f = workspace.download_file(image_file)
        #  self.assertEqual(f.ID, 'FILE_0001_IMAGE')
        #  print(f)

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

if __name__ == '__main__':
    main()
