from test.base import TestCase, main, assets

from ocrd.constants import MIMETYPE_PAGE, VERSION
from ocrd.model import OcrdMets

class TestOcrdMets(TestCase):

    def setUp(self):
        self.mets = OcrdMets(filename=assets.url_of('SBB0000F29300010000/mets.xml'))

    def test_unique_identifier(self):
        self.assertEqual(self.mets.unique_identifier, 'http://resolver.staatsbibliothek-berlin.de/SBB0000F29300010000', 'Right identifier')
        self.mets.unique_identifier = 'foo'
        self.assertEqual(self.mets.unique_identifier, 'foo', 'Right identifier after change')

    def test_unique_identifier_from_nothing(self):
        mets = OcrdMets.empty_mets()
        self.assertEqual(mets.unique_identifier, None, 'no identifier')
        mets.unique_identifier = 'foo'
        self.assertEqual(mets.unique_identifier, 'foo', 'Right identifier after change')
        as_string = mets.to_xml().decode('utf-8')
        self.assertIn('ocrd/core v%s' % VERSION, as_string)
        self.assertIn('CREATEDATE="2018-', as_string)

    def test_file_groups(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')

    def test_find_files(self):
        self.assertEqual(len(self.mets.find_files(fileGrp='OCR-D-IMG')), 2, '2 files in "OCR-D-IMG"')
        self.assertEqual(len(self.mets.find_files(groupId='FILE_0001_IMAGE')), 17, '17 files with GROUPID "FILE_0001_IMAGE"')
        self.assertEqual(len(self.mets.find_files(mimetype='image/tiff')), 12, '12 image/tiff')
        self.assertEqual(len(self.mets.find_files(mimetype=MIMETYPE_PAGE)), 20, '20 ' + MIMETYPE_PAGE)
        self.assertEqual(len(self.mets.find_files()), 34, '34 files total')

    def test_add_group(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')
        self.mets.add_file_group('TEST')
        self.assertEqual(len(self.mets.file_groups), 18, '18 file groups')

    def test_add_file(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')
        self.assertEqual(len(self.mets.find_files(fileGrp='OUTPUT')), 0, '0 files in "OUTPUT"')
        f = self.mets.add_file('OUTPUT', mimetype="bla/quux", groupId="foobar")
        self.assertEqual(f.groupId, 'foobar', 'GROUPID set')
        self.assertEqual(len(self.mets.file_groups), 18, '18 file groups')
        self.assertEqual(len(self.mets.find_files(fileGrp='OUTPUT')), 1, '1 files in "OUTPUT"')

    def test_add_file_no_groupid(self):
        f = self.mets.add_file('OUTPUT', mimetype="bla/quux")
        self.assertEqual(f.groupId, None, 'No GROUPID')

    def test_add_file_ID_fail(self):
        f = self.mets.add_file('OUTPUT', ID='best-id-ever', mimetype="beep/boop")
        self.assertEqual(f.ID, 'best-id-ever', "ID kept")
        with self.assertRaises(Exception) as cm:
            self.mets.add_file('OUTPUT', ID='best-id-ever', mimetype="boop/beep")
        self.assertEqual(str(cm.exception), "File with ID='best-id-ever' already exists")
        f2 = self.mets.add_file('OUTPUT', ID='best-id-ever', mimetype="boop/beep", force=True)
        self.assertEqual(f._el, f2._el)

    def test_filegrp_from_file(self):
        f = self.mets.find_files(fileGrp='OCR-D-IMG')[0]
        self.assertEqual(f.fileGrp, 'OCR-D-IMG')

    def test_file_groupid(self):
        f = self.mets.find_files()[0]
        self.assertEqual(f.groupId, 'FILE_0001_IMAGE')
        f.groupId = 'foo'
        self.assertEqual(f.groupId, 'foo')

if __name__ == '__main__':
    main()
