from tests.base import TestCase, main, create_ocrd_file, create_ocrd_file_with_defaults
from ocrd_models import OcrdMets

class TestOcrdFile(TestCase):

    def test_ocrd_file_without_id(self):
        with self.assertRaisesRegex(ValueError, "set ID"):
            create_ocrd_file('FOO')

    def test_ocrd_file_without_filegrp(self):
        with self.assertRaisesRegex(ValueError, "set fileGrp"):
            create_ocrd_file(None, ID='foo')

    def test_loctype(self):
        f = create_ocrd_file_with_defaults()
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
        f = create_ocrd_file_with_defaults()
        f.url = None
        f.url = 'http://foo'
        f.url = 'http://bar'
        self.assertEqual(f.url, 'http://bar')

    def test_constructor_url(self):
        f = create_ocrd_file_with_defaults(url="foo")
        self.assertEqual(f.url, 'foo')
        self.assertEqual(f.local_filename, 'foo')

    def test_set_id_none(self):
        f = create_ocrd_file_with_defaults()
        f.ID = 'foo12'
        self.assertEqual(f.ID, 'foo12')
        f.ID = None
        self.assertEqual(f.ID, 'foo12')

    def test_basename(self):
        f = create_ocrd_file_with_defaults(local_filename='/tmp/foo/bar/foo.bar')
        self.assertEqual(f.basename, 'foo.bar')

    def test_basename_from_url(self):
        f = create_ocrd_file_with_defaults(url="http://foo.bar/quux")
        self.assertEqual(f.basename, 'quux')

    def test_extension(self):
        f = create_ocrd_file_with_defaults(local_filename='/tmp/foo/bar/foo.bar')
        self.assertEqual(f.extension, '.bar')

    def test_extension_tar(self):
        f = create_ocrd_file_with_defaults(local_filename='/tmp/foo/bar/foo.tar.gz')
        self.assertEqual(f.extension, '.tar.gz')

    def test_basename_without_extension(self):
        f = create_ocrd_file_with_defaults(local_filename='/tmp/foo/bar/foo.bar')
        self.assertEqual(f.basename_without_extension, 'foo')

    def test_basename_without_extension_tar(self):
        f = create_ocrd_file_with_defaults(local_filename='/tmp/foo/bar/foo.tar.gz')
        self.assertEqual(f.basename_without_extension, 'foo')

    # XXX not possible anymore as of Fri Sep  3 13:11:00 CEST 2021
    # def test_fileGrp_wo_parent(self):
    #     with self.assertRaisesRegex(ValueError, "not related to METS"):
    #         f = OcrdFile(None)

    def test_ocrd_file_eq(self):
        mets = OcrdMets.empty_mets()
        f1 = mets.add_file('FOO', ID='FOO_1', mimetype='image/tiff')
        self.assertEqual(f1 == f1, True)
        self.assertEqual(f1 != f1, False)
        f2 = mets.add_file('FOO', ID='FOO_2', mimetype='image/tiff')
        self.assertEqual(f1 == f2, False)
        f3 = create_ocrd_file_with_defaults(ID='TEMP_1', mimetype='image/tiff')
        f4 = create_ocrd_file_with_defaults(ID='TEMP_1', mimetype='image/tif')
        # be tolerant of different equivalent mimetypes
        self.assertEqual(f3 == f4, True)
        f5 = mets.add_file('TEMP', ID='TEMP_1', mimetype='image/tiff')
        self.assertEqual(f3 == f5, True)

if __name__ == '__main__':
    main(__file__)
