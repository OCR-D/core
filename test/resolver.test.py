import base as unittest
from base import PWD
from ocrd.resolver import Resolver

METS_URL = 'file://' + PWD + '/assets/herold/mets.xml'

class TestResolver(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_URL)
        input_files = workspace.list_input_files()
        mets_file = input_files[0]
        f = workspace.download_file(mets_file)
        print(mets_file)
        print(f)

if __name__ == '__main__':
    unittest.main()
