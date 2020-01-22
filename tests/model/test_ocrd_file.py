from lxml import etree as ET
from tests.base import TestCase, main
from ocrd_models import OcrdFile

class TestOcrdFile(TestCase):

    def test_no_pageid_without_mets(self):
        f = OcrdFile(None)
        with self.assertRaisesRegex(Exception, ".*has no member 'mets' pointing.*"):
            print(f.pageId)
        with self.assertRaisesRegex(Exception, ".*has no member 'mets' pointing.*"):
            f.pageId = 'foo'

    def test_loctype(self):
        f = OcrdFile(None)
        self.assertEqual(f.loctype, 'OTHER')
        self.assertEqual(f.otherloctype, 'FILE')
        f.otherloctype = 'foo'
        self.assertEqual(f.otherloctype, 'foo')
        f.loctype = 'URN'
        self.assertEqual(f.loctype, 'URN')
        self.assertEqual(f.otherloctype, None)
        f.otherloctype = 'foo'
        self.assertEqual(f.loctype, 'OTHER')

    def test_set_url(self):
        f = OcrdFile(None)
        f.url = None
        f.url = 'http://foo'
        f.url = 'http://bar'
        self.assertEqual(f.url, 'http://bar')

    def test_constructor_url(self):
        f = OcrdFile(None, url="foo/bar")
        self.assertEqual(f.url, 'foo/bar')
        self.assertEqual(f.local_filename, 'foo/bar')

    def test_set_id_none(self):
        f = OcrdFile(None)
        f.ID = 'foo12'
        self.assertEqual(f.ID, 'foo12')
        f.ID = None
        self.assertEqual(f.ID, 'foo12')

    def test_basename(self):
        f = OcrdFile(None, local_filename='/tmp/foo/bar/foo.bar')
        self.assertEqual(f.basename, 'foo.bar')

    def test_basename_from_url(self):
        f = OcrdFile(None, url="http://foo.bar/quux")
        self.assertEqual(f.basename, 'quux')

    def test_extension(self):
        f = OcrdFile(None, local_filename='/tmp/foo/bar/foo.bar')
        self.assertEqual(f.extension, '.bar')

    def test_extension_tar(self):
        f = OcrdFile(None, local_filename='/tmp/foo/bar/foo.tar.gz')
        self.assertEqual(f.extension, '.tar.gz')

    def test_basename_without_extension(self):
        f = OcrdFile(None, local_filename='/tmp/foo/bar/foo.bar')
        self.assertEqual(f.basename_without_extension, 'foo')

    def test_basename_without_extension_tar(self):
        f = OcrdFile(None, local_filename='/tmp/foo/bar/foo.tar.gz')
        self.assertEqual(f.basename_without_extension, 'foo')

    def test_fileGrp_wo_parent(self):
        f = OcrdFile(None)
        self.assertEqual(f.fileGrp, 'TEMP')

if __name__ == '__main__':
    main()
