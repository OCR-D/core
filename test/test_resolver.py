import test.base as unittest
from test.base import PWD
from ocrd.resolver import Resolver

METS_URL = 'file://' + PWD + '/assets/herold/mets.xml'

class TestResolver(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_URL)
        input_files = workspace.mets.files_in_group('INPUT')
        #  print [str(f) for f in input_files]
        mets_file = input_files[0]
        f = workspace.download_file(mets_file)
        self.assertEquals(f.ID, 'FILE_0001_IMAGE')
        #  print(f)

if __name__ == '__main__':
    unittest.main()
