from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory

from pkg_resources import parse_version
import subprocess
import yaml
import pytest

from ocrd.cli.bashlib import bashlib_cli

from ocrd.constants import BASHLIB_FILENAME
from ocrd_utils.constants import VERSION, MIME_TO_EXT, MIMETYPE_PAGE
from ocrd_validators.constants import BAGIT_TXT
from ocrd_models.constants import TAG_MODS_IDENTIFIER

class TestBashlibCli(TestCase):

    def invoke_bash(self, script):
        result = subprocess.run('bash -c "source $(ocrd bashlib filename) && %s"' % script, 
                                universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return result.returncode, result.stdout, result.stderr
            
    def setUp(self):
        self.maxDiff = None
        super().setUp()

    def test_filename(self):
        exit_code, out, err = self.invoke_cli(bashlib_cli, ['filename'])
        print("out=%s\berr=%s" % (out, err))
        assert out.endswith('ocrd/lib.bash\n')

    def test_constants(self):
        def _test_constant(name, val):
            _, out, err = self.invoke_cli(bashlib_cli, ['constants', name])
            print("err=%s" % err)
            assert out == '%s\n' % val
        _test_constant('BASHLIB_FILENAME', BASHLIB_FILENAME)
        _test_constant('VERSION', VERSION)
        _test_constant('MIMETYPE_PAGE', MIMETYPE_PAGE)
        _test_constant('BAGIT_TXT', BAGIT_TXT)
        _test_constant('TAG_MODS_IDENTIFIER', TAG_MODS_IDENTIFIER)

    def test_constants_dict(self):
        _, out, err = self.invoke_cli(bashlib_cli, ['constants', 'MIME_TO_EXT'])
        assert '[image/tiff]=.tif' in out

    def test_constants_all(self):
        _, out, err = self.invoke_cli(bashlib_cli, ['constants', '*'])
        out = yaml.safe_load(out)
        assert 'VERSION' in out
        assert len(out) >= 40

    def test_constants_fail(self):
        exit_code, out, err = self.invoke_cli(bashlib_cli, ['constants', '1234!@#$--'])
        assert exit_code == 1
        assert err == "ERROR: name '1234!@#$--' is not a known constant\n"

    def test_input_files(self):
        with copy_of_directory(assets.path_to('kant_aufklaerung_1784/data')) as wsdir:
            with pushd_popd(wsdir):
                _, out, err = self.invoke_cli(bashlib_cli, ['input-files', '-I', 'OCR-D-IMG'])
                assert "[url]='OCR-D-IMG/INPUT_0017.tif' [ID]='INPUT_0017' [mimetype]='image/tiff'"
                       "[pageId]='PHYS_0017' [outputFileId]='OUTPUT_PHYS_0017'" in out

    def test_bashlib_defs(self):
        exit_code, out, err = self.invoke_bash("type -t ocrd__wrap && type -t ocrd__minversion")
        assert exit_code == 0
        assert len(err) == 0
        assert 'function' in out

    def test_bashlib_minversion(self):
        exit_code, out, err = self.invoke_bash("ocrd__minversion 2.29.0")
        assert exit_code == 0
        version = parse_version(VERSION)
        exit_code, out, err = self.invoke_bash("ocrd__minversion %d.%d.%d" % (version.major, version.minor+1, 0))
        assert exit_code > 0
        assert "ERROR: ocrd/core is too old" in err

if __name__ == "__main__":
    main(__file__)

