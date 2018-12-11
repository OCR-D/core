from test.base import TestCase, main, assets

from ocrd.constants import MIMETYPE_PAGE, VERSION
from ocrd.model import OcrdMets, OcrdFile

# pylint: disable=protected-access,deprecated-method
class TestOcrdMets(TestCase):

    def setUp(self):
        self.mets = OcrdMets(filename=assets.url_of('SBB0000F29300010000/data/mets.xml'))

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
        self.assertEqual(len(self.mets.find_files(fileGrp='OCR-D-IMG')), 3, '3 files in "OCR-D-IMG"')
        self.assertEqual(len(self.mets.find_files(pageId='PHYS_0001')), 17, '17 files for page "PHYS_0001"')
        self.assertEqual(len(self.mets.find_files(mimetype='image/tiff')), 13, '13 image/tiff')
        self.assertEqual(len(self.mets.find_files(mimetype=MIMETYPE_PAGE)), 20, '20 ' + MIMETYPE_PAGE)
        self.assertEqual(len(self.mets.find_files()), 35, '35 files total')

    def test_find_files_local_only(self):
        self.assertEqual(len(self.mets.find_files(pageId='PHYS_0001', local_only=True)), 3, '3 local files for page "PHYS_0001"')

    def test_physical_pages(self):
        self.assertEqual(len(self.mets.physical_pages), 3, '3 physical pages')

    def test_physical_pages_from_empty_mets(self):
        mets = OcrdMets(content="<mets></mets>")
        self.assertEqual(len(mets.physical_pages), 0, 'no physical page')
        mets.add_file('OUTPUT', ID="foo123", pageId="foobar")
        self.assertEqual(len(mets.physical_pages), 1, '1 physical page')

    def test_add_group(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')
        self.mets.add_file_group('TEST')
        self.assertEqual(len(self.mets.file_groups), 18, '18 file groups')

    def test_no_pageid_without_mets(self):
        f = OcrdFile(None)
        with self.assertRaisesRegexp(Exception, ".*has no member 'mets' pointing.*"):
            print(f.pageId)
        with self.assertRaisesRegexp(Exception, ".*has no member 'mets' pointing.*"):
            f.pageId = 'foo'

    def test_add_file(self):
        self.assertEqual(len(self.mets.file_groups), 17, '17 file groups')
        self.assertEqual(len(self.mets.find_files(fileGrp='OUTPUT')), 0, '0 files in "OUTPUT"')
        f = self.mets.add_file('OUTPUT', ID="foo123", mimetype="bla/quux", pageId="foobar")
        self.assertEqual(f.pageId, 'foobar', 'pageId set')
        self.assertEqual(len(self.mets.file_groups), 18, '18 file groups')
        self.assertEqual(len(self.mets.find_files(fileGrp='OUTPUT')), 1, '1 files in "OUTPUT"')
        self.mets.set_physical_page_for_file('barfoo', f, order='300', orderlabel="page 300")
        self.assertEqual(f.pageId, 'barfoo', 'pageId changed')

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

    def test_add_file_no_id(self):
        with self.assertRaisesRegexp(Exception, "Must set ID of the mets:file"):
            self.mets.add_file('FOO')

    def test_add_file_no_pageid(self):
        f = self.mets.add_file('OUTPUT', mimetype="bla/quux", ID="foo3")
        self.assertEqual(f.pageId, None, 'No pageId')

    def test_file_pageid(self):
        f = self.mets.find_files()[0]
        self.assertEqual(f.pageId, 'PHYS_0001')
        f.pageId = 'foo'
        self.assertEqual(f.pageId, 'foo')

    def test_agent(self):
        #  Processor(workspace=self.workspace)
        mets = self.mets
        beforelen = len(mets.agents)
        mets.add_agent('foo bar v0.0.1', 'OTHER', 'OTHER', 'YETOTHERSTILL')
        #  print(['%s'%x for x in mets.agents])
        self.assertEqual(len(mets.agents), beforelen + 1)

    def test_metshdr(self):
        """
        Test whether metsHdr is created on-demand
        """
        mets = OcrdMets(content="<mets></mets>")
        self.assertFalse(mets._tree.getroot().getchildren())
        mets.add_agent()
        self.assertEqual(len(mets._tree.getroot().getchildren()), 1)

if __name__ == '__main__':
    main()
