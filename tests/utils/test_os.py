from tempfile import mkdtemp
from tests.base import TestCase, main, assets
from shutil import rmtree
from os import environ as ENV, getcwd
from os.path import expanduser, join

from ocrd_utils.os import (
    list_resource_candidates
)

class TestOsUtils(TestCase):

    def setUp(self):
        self.tempdir_path = mkdtemp()
        self.tempdir_venv = mkdtemp()
        ENV['OCRD_DUMMY_PATH'] = self.tempdir_path
        self.VIRTUAL_ENV = ENV['VIRTUAL_ENV']
        ENV['VIRTUAL_ENV'] = self.tempdir_venv

    def tearDown(self):
        rmtree(self.tempdir_path)
        rmtree(self.tempdir_venv)
        del ENV['OCRD_DUMMY_PATH']
        ENV['VIRTUAL_ENV'] = self.VIRTUAL_ENV

    def test_resolve_basic(self):
        fname = 'foo.bar'
        cands = list_resource_candidates('ocrd-dummy', fname)
        print(getcwd())
        cands = [x.replace(getcwd(), '$PWD').replace(expanduser('~'), '$HOME') for x in cands]
        self.assertEqual(cands, [join(x, fname) for x in [
            '$PWD',
            self.tempdir_path,
            join(self.tempdir_venv, 'share', 'ocrd-dummy'),
            '$HOME/.local/share/ocrd-dummy',
            '$HOME/.config/ocrd-dummy',
            '$HOME/.cache/ocrd-dummy',
        ]])



if __name__ == '__main__':
    main(__file__)
