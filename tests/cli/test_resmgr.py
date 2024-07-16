from pathlib import Path
from click.testing import CliRunner
from pytest import fixture
from tempfile import TemporaryDirectory

from ocrd_utils import disableLogging, directory_size
from ocrd.cli.resmgr import resmgr_cli
from ocrd.resource_manager import OcrdResourceManager

runner = CliRunner()
executable = 'ocrd-dummy'

@fixture
def mgr_with_tmp_path(tmp_path):
    print(tmp_path)
    mgr = OcrdResourceManager(xdg_data_home=tmp_path, userdir=tmp_path, xdg_config_home=tmp_path)
    env = {'XDG_DATA_HOME': str(tmp_path), 'XDG_CONFIG_HOME': str(tmp_path)}
    return tmp_path, mgr, env

def test_url_tool_name_unregistered(mgr_with_tmp_path):
    """
    We should add a test for the -n URL TOOL NAME use-case as well (both as an unregistered resource and as URL-override).
    """
    _, mgr, env = mgr_with_tmp_path
    print(mgr.list_installed(executable)[0][1])
    rsrcs_before = len(mgr.list_installed(executable)[0][1])

    # add an unregistered resource
    url = 'https://github.com/tesseract-ocr/tessdata_best/raw/main/dzo.traineddata'
    name = 'dzo.traineddata'
    r = runner.invoke(resmgr_cli, ['download', '--allow-uninstalled', '--any-url', url, executable, name], env=env)
    mgr.load_resource_list(mgr.user_list)

    rsrcs = mgr.list_installed(executable)[0][1]
    assert len(rsrcs) == rsrcs_before + 1
    assert rsrcs[-1]['name'] == name
    assert rsrcs[-1]['url'] == url

    # add resource with different URL but same name
    url2 = url.replace('dzo', 'bos')
    #
    # TODO(kba): Silently skipped since https://github.com/OCR-D/core/commit/d5173ada7d052c107c04da8732ccd30f61c4d9a1
    #            so we'd need to check the log output which is not captured by
    #            CliRunner, even though `mix_stderr == True`
    #
    # r = runner.invoke(resmgr_cli, ['download', '--allow-uninstalled', '--any-url', url2, executable, name], env=env)
    # assert 'already exists but --overwrite is not set' in r.output
    r = runner.invoke(resmgr_cli, ['download', '--overwrite', '--allow-uninstalled', '--any-url', url2, executable, name], env=env)
    # assert 'already exists but --overwrite is not set' not in r.output

    mgr.load_resource_list(mgr.user_list)

    rsrcs = mgr.list_installed(executable)[0][1]
    print(rsrcs)
    assert len(rsrcs) == rsrcs_before + 1
    assert rsrcs[-1]['name'] == name
    assert rsrcs[-1]['url'] == url2

def test_directory_copy(mgr_with_tmp_path):
    """
    https://github.com/OCR-D/core/issues/691#issuecomment-1038152665
    ocrd resmgr download -a -n ~/.local/share/ocrd-resources/ocrd-origami-segment/bbz ocrd-origami-segment bbz2
    """
    mgr_path, mgr, env = mgr_with_tmp_path
    proc = 'ocrd-foo-bar'
    res_name = 'baz'
    with TemporaryDirectory() as tmp_path:
        for i in range(10):
            with open(Path(tmp_path, f'f{i}'), 'w', encoding='utf-8') as f:
                f.write('foo')
        assert directory_size(tmp_path) == 30
        assert mgr.list_installed(executable=proc) == [(proc, [])]

        r = runner.invoke(
            resmgr_cli,
            ['download', '--allow-uninstalled', '--any-url', tmp_path, proc, res_name],
            env=env,
            catch_exceptions=False
        )
        assert not r.exception
        assert Path(mgr_path / 'ocrd-resources' / proc).exists()
        assert directory_size(mgr_path / 'ocrd-resources' / proc /  res_name) == 30

        #
        # TODO(kba): Silently skipped since https://github.com/OCR-D/core/commit/d5173ada7d052c107c04da8732ccd30f61c4d9a1
        #            so we'd need to check the log output which is not captured by
        #            CliRunner, even though `mix_stderr == True`
        #
        # r = runner.invoke(
        #     resmgr_cli,
        #     ['download', '--allow-uninstalled', '--any-url', tmp_path, proc, res_name],
        #     env=env,
        #     catch_exceptions=False
        # )
        # assert 'already exists but --overwrite is not set' in r.output
        r = runner.invoke(
            resmgr_cli,
            ['download', '--overwrite', '--allow-uninstalled', '--any-url', tmp_path, proc, res_name],
            env=env,
            catch_exceptions=False
        )
        assert 'already exists but --overwrite is not set' not in r.output
