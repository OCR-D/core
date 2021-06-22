from tempfile import mkdtemp
from tests.base import TestCase, main, assets
from shutil import rmtree
from os import environ as ENV, getcwd
from os.path import expanduser, join

from ocrd_utils.os import (
    list_resource_candidates,
    resolve_mets_arguments
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

    def test_resolve_mets_arguments(self):
        assert resolve_mets_arguments('/', 'mets.xml', None) == ('/', '/mets.xml', 'mets.xml')
        with self.assertRaisesRegex(ValueError, "Use either --mets or --mets-basename, not both"):
            resolve_mets_arguments('/', '/foo/bar', 'foo.xml')
        with self.assertRaisesRegex(ValueError, "inconsistent with --directory"):
            resolve_mets_arguments('/foo', '/bar/foo.xml', None)
        assert resolve_mets_arguments('/foo', '/foo/foo.xml', None) == ('/foo', '/foo/foo.xml', 'foo.xml')



if __name__ == '__main__':
    main(__file__)
