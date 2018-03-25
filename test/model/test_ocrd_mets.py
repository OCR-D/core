#  from pprint import pprint

from test.base import TestCase, main
from test.assets import METS_HEROLD
from ocrd.model import OcrdMets

class TestOcrdMets(TestCase):

    def test_basic(self):
        mets = OcrdMets(filename=METS_HEROLD.replace('file://', ''))
        mets.add_file('OUTPUT', mimetype="bla/quux")
        #  print(mets.to_xml())
        #  print(mets.files_in_group('INPUT')[0])

if __name__ == '__main__':
    main()
