from tempfile import mkdtemp
from tests.base import TestCase, main, assets
from shutil import rmtree
from os import environ as ENV, getcwd
from os.path import expanduser, join

from ocrd_utils.os import (
    list_resource_candidates,
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


if __name__ == '__main__':
    main(__file__)
