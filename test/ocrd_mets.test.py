from pprint import pprint

import base as unittest
from base import PWD
from ocrd.model.ocrd_mets import OcrdMets

METS_FILE = PWD + '/assets/herold/mets.xml'

class TestOcrdMets(unittest.TestCase):

    def test_basic(self):
        mets = OcrdMets(filename=METS_FILE)
        print(mets.files_in_group('INPUT')[0])

if __name__ == '__main__':
    unittest.main()
