from pathlib import Path
from click.testing import CliRunner
from pytest import fixture

from ocrd.cli.resmgr import resmgr_cli
from ocrd.resource_manager import OcrdResourceManager

runner = CliRunner()
executable = 'ocrd-tesserocr-recognize'

@fixture
def mgr_with_tmp_path(tmp_path):
    mgr = OcrdResourceManager(xdg_data_home=tmp_path, userdir=tmp_path, xdg_config_home=tmp_path)
    env = {'XDG_DATA_HOME': str(tmp_path), 'XDG_CONFIG_HOME': str(tmp_path)}
    return tmp_path, mgr, env

def test_url_tool_name_unregistered(mgr_with_tmp_path):
    """
    We should add a test for the -n URL TOOL NAME use-case as well (both as an unregistered resource and as URL-override).
    """
    tmp_path, mgr, env = mgr_with_tmp_path
    print(mgr.list_installed('ocrd-tesserocr-recognize')[0][1])
    rsrcs_before = len(mgr.list_installed('ocrd-tesserocr-recognize')[0][1])

    # add an unregistered resource
    url = 'https://github.com/tesseract-ocr/tessdata_best/raw/main/dzo.traineddata'
    name = 'dzo.traineddata'
    r = runner.invoke(resmgr_cli, ['download', '-a', '--any-url', url, executable, name], env=env)
    mgr.load_resource_list(mgr.user_list)
    print(r.output)
    with open(mgr.user_list, 'r') as f:
        print(f.read())

    # assert
    rsrcs = mgr.list_installed('ocrd-tesserocr-recognize')[0][1]
    assert len(rsrcs) == rsrcs_before + 1
    assert rsrcs[0]['name'] == name
    assert rsrcs[0]['url'] == url

    # add resource with different URL but sanem name
    url2 = url.replace('dzo', 'bos')
    r = runner.invoke(resmgr_cli, ['download', '--overwrite', '--any-url', url2, executable, name], env=env)
    mgr.load_resource_list(mgr.user_list)

    # assert
    rsrcs = mgr.list_installed('ocrd-tesserocr-recognize')[0][1]
    print(rsrcs)
    assert len(rsrcs) == rsrcs_before + 1
    assert rsrcs[0]['name'] == name
    assert rsrcs[0]['url'] == url2
