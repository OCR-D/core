from tempfile import mkdtemp
from tests.base import TestCase, main, assets
from tests.data import DUMMY_TOOL
from shutil import rmtree
from pathlib import Path
from os import environ as ENV, getcwd
from os.path import expanduser, join
import sys

from ocrd_utils.os import (
    list_resource_candidates,
    list_all_resources,
    redirect_stderr_and_stdout_to_file,
    guess_media_type,
)
from ocrd_utils import config

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
            if ENV['HOME'] == '/' or expanduser('~') == '/':
                return s
            return s.replace(ENV['HOME'], '$HOME').replace(expanduser('~'), '$HOME')
        fname = 'foo.bar'
        cands = list_resource_candidates('ocrd-dummy', fname)
        cands = [dehomify(x) for x in cands]
        print(cands)
        self.assertEqual(cands, [join(x, fname) for x in [
            dehomify(join(getcwd())),
            dehomify(self.tempdir_path),
            dehomify(join(config.XDG_DATA_HOME, 'ocrd-resources', 'ocrd-dummy')),
            '/usr/local/share/ocrd-resources/ocrd-dummy',
        ]])

    def test_resolve_installed(self):
        tmpdir = Path(self.tempdir_path)
        (tmpdir / 'some.json').write_bytes(b'')
        cands = list(list_all_resources('ocrd-dummy'))
        # finds the file via env location
        assert len(cands) == 1
        cands = list(list_all_resources('ocrd-dummy', moduled=self.tempdir_path))
        # same file now also appears as moduled
        assert len(cands) == 2
        tmpdir = tmpdir / 'ocrd-resources' / 'ocrd-dummy'
        tmpdir.mkdir(parents=True)
        (tmpdir / 'another.json').write_bytes(b'')
        cands = list(list_all_resources('ocrd-dummy', xdg_data_home=self.tempdir_path))
        # absent an actual ocrd-tool.json, directories are allowed as well as files
        # so this finds some.json and ocrd-resources/ in the env location,
        # and another.json in the data location
        assert len(cands) == 3
        dummy_tool = dict(DUMMY_TOOL)
        dummy_tool['parameters']['fileparam'] = {
            'type': 'string',
            'format': 'uri',
            'content-type': 'application/zip'
        }
        cands = list(list_all_resources('ocrd-dummy', ocrd_tool=dummy_tool, xdg_data_home=self.tempdir_path))
        # we now expect only zip files, not directories
        # but JSON is always allowed (for potential preset files)
        assert len(cands) == 2

    def test_guess_media_type(self):
        testdata = Path(__file__).parent / '../data'
        assert guess_media_type(__file__) == 'text/x-python'
        assert guess_media_type(testdata / 'filename.tar.gz') == 'application/gzip'
        assert guess_media_type(testdata / 'filename.tar.xz') == 'application/x-xz'
        assert guess_media_type(testdata / 'filename.zip') == 'application/zip'
        assert guess_media_type(testdata / 'mets-with-metsDocumentID.xml') == 'application/xml'
        assert guess_media_type(testdata / 'mets-with-metsDocumentID.xml', application_xml='text/x-mets') == 'text/x-mets'

    def test_redirect_stderr_and_stdout_to_file(self):
        # TODO test logging is redirected properly without running into
        # pytest's capturing intricacies
        fname = '/tmp/test-redirect.txt'
        Path(fname).write_bytes(b'')
        with redirect_stderr_and_stdout_to_file(fname):
            print('one')
            sys.stdout.write('two\n')
            sys.stderr.write('three\n')
            print('four', file=sys.stderr)
        assert Path(fname).read_text(encoding='utf-8') == 'one\ntwo\nthree\nfour\n'

if __name__ == '__main__':
    main(__file__)
