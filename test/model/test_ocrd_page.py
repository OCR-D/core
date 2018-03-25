from test.base import TestCase, main
from test.assets import METS_HEROLD_PAGE_5
from ocrd.model import OcrdPage

class TestOcrdPage(TestCase):

    def runTest(self):
        page = OcrdPage(filename=METS_HEROLD_PAGE_5.replace('file://', ''))
        #  mets.add_file('OUTPUT', mimetype="bla/quux")
        #  print(mets.to_xml())
        #  print(mets.files_in_group('INPUT')[0])

if __name__ == '__main__':
    main()
