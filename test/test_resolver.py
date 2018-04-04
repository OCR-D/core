from ocrd.resolver import Resolver
from test.base import TestCase, assets, main
METS_HEROLD = assets.url_of('SBB0000F29300010000/mets.xml')

class TestResolver(TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD)
        #  print(METS_HEROLD)
        #  print(workspace.mets)
        input_files = workspace.mets.files_in_group('OCR-D-IMG')
        #  print [str(f) for f in input_files]
        image_file = input_files[0]
        #  print(image_file)
        f = workspace.download_file(image_file)
        self.assertEqual(f.ID, 'FILE_0001_IMAGE')
        #  print(f)

if __name__ == '__main__':
    main()
