import base as unittest
from base import PWD
from ocrd.resolver import Resolver

METS_URL = 'file://' + PWD + '/assets/herold/mets.xml'

class TestResolver(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver()
        workspace = resolver.create_workspace(METS_URL)
        f = workspace.download_input(workspace.list_input_files()[0])
        print(f)

if __name__ == '__main__':
    unittest.main()
