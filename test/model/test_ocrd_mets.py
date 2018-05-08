from test.base import TestCase, main, assets

from ocrd.constants import MIMETYPE_PAGE
from ocrd.model import OcrdMets

class TestOcrdMets(TestCase):

    def setUp(self):
        self.mets = OcrdMets(filename=assets.url_of('SBB0000F29300010000/mets.xml'))

    def test_unique_identifier(self):
        self.assertEqual(self.mets.unique_identifier, 'http://resolver.staatsbibliothek-berlin.de/SBB0000F29300010000', 'Right identifier')

    def test_file_groups(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')

    def test_find_files(self):
        self.assertEqual(len(self.mets.find_files(fileGrp='OCR-D-IMG')), 2, '2 files in "OCR-D-IMG"')
        self.assertEqual(len(self.mets.find_files(groupId='FILE_0001_IMAGE')), 17, '17 files with GROUPID "FILE_0001_IMAGE"')
        self.assertEqual(len(self.mets.find_files(mimetype='image/tif')), 12, '12 image/tif')
        self.assertEqual(len(self.mets.find_files(mimetype=MIMETYPE_PAGE)), 20, '20 ' + MIMETYPE_PAGE)
        self.assertEqual(len(self.mets.find_files()), 34, '34 files total')

    def test_add_group(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')
        self.mets.add_file_group('TEST')
        self.assertEqual(len(self.mets.file_groups), 18, '18 file groups')

    def test_add_file(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')
        self.assertEqual(len(self.mets.find_files(fileGrp='OUTPUT')), 0, '0 files in "OUTPUT"')
        self.mets.add_file('OUTPUT', mimetype="bla/quux")
        self.assertEqual(len(self.mets.file_groups), 18, '18 file groups')
        self.assertEqual(len(self.mets.find_files(fileGrp='OUTPUT')), 1, '1 files in "OUTPUT"')

    def test_file_groupid(self):
        f = self.mets.find_files()[0]
        self.assertEqual(f.groupId, 'FILE_0001_IMAGE')
        f.groupId = 'foo'
        self.assertEqual(f.groupId, 'foo')

if __name__ == '__main__':
    main()
