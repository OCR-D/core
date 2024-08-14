from contextlib import contextmanager
from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory

import os, sys
from os import environ
import traceback
import subprocess
import tempfile
import pathlib
import yaml
import json
from pathlib import Path

from ocrd.cli.bashlib import bashlib_cli

from ocrd.constants import BASHLIB_FILENAME
from ocrd_utils.constants import VERSION, MIMETYPE_PAGE
from ocrd_validators.constants import BAGIT_TXT
from ocrd_models.constants import TAG_MODS_IDENTIFIER

from ocrd_utils import pushd_popd

class TestBashlibCli(TestCase):

    def invoke_bash(self, script, *args, executable=None):
        # pattern input=script would not work with additional args
        scriptfile = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        scriptfile.write(script)
        scriptfile.close()
        env = dict(os.environ)
        if isinstance(executable, str):
            # ocrd-tool needs executable in PATH
            scriptdir = os.path.dirname(scriptfile.name)
            if os.path.lexists(executable):
                os.unlink(executable)
            os.symlink(scriptfile.name, executable)
            os.chmod(scriptfile.name, 0x755)
            cwd = os.getcwd()
            path = env['PATH']
            env.update(PATH=f'{path}:{cwd}')
        try:
            result = subprocess.run(['bash', scriptfile.name] + list(args), env=env,
                                    # py37+: text=True, capture_output=True
                                    universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            traceback.print_exc()
            return -1, "", str(e)
        finally:
            os.remove(scriptfile.name)

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
                assert ("[url]='' [local_filename]='OCR-D-IMG/INPUT_0017.tif' [ID]='INPUT_0017' [mimetype]='image/tiff' "
                        "[pageId]='PHYS_0017' [outputFileId]='OUTPUT_PHYS_0017'") in out

    def test_bashlib_defs(self):
        exit_code, out, err = self.invoke_bash(
            "source $(ocrd bashlib filename) && type -t ocrd__wrap && type -t ocrd__minversion")
        assert exit_code == 0
        assert len(err) == 0
        assert 'function' in out

    def test_bashlib_minversion(self):
        exit_code, out, err = self.invoke_bash(
            "source $(ocrd bashlib filename) && ocrd__minversion 2.29.0")
        assert exit_code == 0
        exit_code, out, err = self.invoke_bash(
            "source $(ocrd bashlib filename) && ocrd__minversion " + VERSION)
        assert exit_code > 0
        assert "ERROR: ocrd/core is too old" in err

    def test_bashlib_cp_processor(self):
        # script = (Path(__file__).parent.parent / 'data/bashlib_cp_processor.sh').read_text()
        # ocrd_tool = json.loads((Path(__file__).parent.parent / 'data/bashlib_cp_processor.ocrd-tool.json').read_text())
        scriptdir = Path(__file__).parent.parent / 'data'

        with copy_of_directory(assets.path_to('kant_aufklaerung_1784/data')) as wsdir, pushd_popd(wsdir):
            with open(f'{scriptdir}/ocrd-cp', 'r', encoding='utf-8') as script_f:
                script = script_f.read()
            with open(f'{scriptdir}/ocrd-cp.ocrd-tool.json', 'r', encoding='utf-8') as tool_in, \
                open(f'{wsdir}/ocrd-tool.json', 'w', encoding='utf-8') as tool_out:
                tool_out.write(tool_in.read())
            # run on 1 input
            exit_code, out, err = self.invoke_bash(
                script, '-I', 'OCR-D-GT-PAGE', '-O', 'OCR-D-GT-PAGE2', '-P', 'message', 'hello world',
                executable='ocrd-cp')
            print({'exit_code': exit_code, 'out': out, 'err': err})
            assert 'single input fileGrp' in err
            assert 'processing PAGE-XML' in err
            assert exit_code == 0
            assert 'hello world' in out
            path = pathlib.Path('OCR-D-GT-PAGE2')
            assert path.is_dir()
            assert next(path.glob('*.xml'), None)
            # run on 2 inputs
            exit_code, out, err = self.invoke_bash(
                script, '-I', 'OCR-D-IMG,OCR-D-GT-PAGE', '-O', 'OCR-D-IMG2',
                executable='ocrd-cp')
            assert 'multiple input fileGrps' in err
            assert exit_code == 0
            assert 'ignoring application/vnd.prima.page+xml' in err
            path = pathlib.Path('OCR-D-IMG2')
            assert path.is_dir()
            assert next(path.glob('*.tif'), None)

if __name__ == "__main__":
    main(__file__)

