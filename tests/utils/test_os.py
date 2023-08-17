from tempfile import mkdtemp
from tests.base import TestCase, main, assets
from shutil import rmtree
from pathlib import Path
from os import environ as ENV, getcwd
from os.path import expanduser, join

from ocrd_utils.os import (
    list_resource_candidates,
    guess_media_type,
)

class TestOsUtils(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.tempdir_path = mkdtemp()
        ENV['OCRD_DUMMY_PATH'] = self.tempdir_path
        super().setUp()

    def tearDown(self):
        rmtree(self.tempdir_path)
        del ENV['OCRD_DUMMY_PATH']

    def test_resolve_basic(self):
        def dehomify(s):
            return s.replace(ENV['HOME'], '$HOME').replace(expanduser('~'), '$HOME')
        fname = 'foo.bar'
        cands = list_resource_candidates('ocrd-dummy', fname)
        cands = [dehomify(x) for x in cands]
        print(cands)
        self.assertEqual(cands, [join(x, fname) for x in [
            dehomify(join(getcwd())),
            dehomify(self.tempdir_path),
            '$HOME/.local/share/ocrd-resources/ocrd-dummy',
            '/usr/local/share/ocrd-resources/ocrd-dummy',
        ]])

    def test_guess_media_type(self):
        testdata = Path(__file__).parent / '../data'
        assert guess_media_type(__file__) == 'text/x-python'
        assert guess_media_type(testdata / 'filename.tar.gz') == 'application/gzip'
        assert guess_media_type(testdata / 'filename.tar.xz') == 'application/x-xz'
        assert guess_media_type(testdata / 'filename.zip') == 'application/zip'
        assert guess_media_type(testdata / 'mets-with-metsDocumentID.xml') == 'application/xml'
        assert guess_media_type(testdata / 'mets-with-metsDocumentID.xml', application_xml='text/x-mets') == 'text/x-mets'


if __name__ == '__main__':
    main(__file__)
