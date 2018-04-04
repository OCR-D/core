from ocrd.model import OcrdMets

from test.base import TestCase, main, assets
METS_HEROLD = assets.url_of('SBB0000F29300010000/mets.xml')

class TestOcrdMets(TestCase):

    def runTest(self):
        mets = OcrdMets(filename=METS_HEROLD.replace('file://', ''))
        mets.add_file('OUTPUT', mimetype="bla/quux")
        #  print(mets.to_xml())
        #  print(mets.files_in_group('INPUT')[0])

if __name__ == '__main__':
    main()
