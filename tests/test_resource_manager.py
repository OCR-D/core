import os
import pathlib

from ocrd.resource_manager import OcrdResourceManager

from pytest import raises
from tests.base import main

CONST_RESOURCE_YML = 'resources.yml'
CONST_RESOURCE_URL_LAYOUT = 'https://ocr-d-repo.scc.kit.edu/models/dfki/layoutAnalysis/mapping_densenet.pickle'


def test_resources_manager_config_default():

    # act
    mgr = OcrdResourceManager()

    # assert
    default_config_dir = os.path.join(os.environ['HOME'], '.config', 'ocrd')
    f = pathlib.Path(default_config_dir) / CONST_RESOURCE_YML
    assert f.exists()
    assert f == mgr.user_list
    assert mgr.add_to_user_database('ocrd-foo', f)
    mgr.list_installed()
    proc = 'ocrd-anybaseocr-layout-analysis'
    # TODO mock request
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)


def test_resources_manager_from_environment(tmp_path, monkeypatch):

    # arrange
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path))
    monkeypatch.setenv('HOME', str(tmp_path))

    # act
    mgr = OcrdResourceManager()

    # assert
    f = tmp_path / 'ocrd' / CONST_RESOURCE_YML
    assert f.exists()
    assert f == mgr.user_list
    assert mgr.add_to_user_database('ocrd-foo', f)
    mgr.list_installed()
    proc = 'ocrd-anybaseocr-layout-analysis'
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)
    assert mgr.userdir == str(tmp_path)


def test_resources_manager_config_explicite(tmp_path):

    # act
    mgr = OcrdResourceManager(xdg_config_home=str(tmp_path))

    # assert
    f = tmp_path / 'ocrd' / CONST_RESOURCE_YML
    assert f.exists()
    assert f == mgr.user_list
    assert mgr.add_to_user_database('ocrd-foo', f)
    mgr.list_installed()
    proc = 'ocrd-anybaseocr-layout-analysis'
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)

def test_resources_manager_config_explicit_invalid(tmp_path):

    # act
    (tmp_path / 'ocrd').mkdir()
    (tmp_path / 'ocrd' / CONST_RESOURCE_YML).write_text('::INVALID::')

    # assert
    with raises(ValueError, match='is invalid'):
        OcrdResourceManager(xdg_config_home=tmp_path)

def test_find_resources(tmp_path):

    # act
    f = tmp_path / 'ocrd-foo' / 'foo.bar'
    f.parent.mkdir()
    f.write_text('foobar')
    mgr = OcrdResourceManager(xdg_config_home=tmp_path)

    # assert
    assert mgr.find_resources(executable='ocrd-foo') == []
    assert mgr.add_to_user_database('ocrd-foo', f, url='http://foo/bar')
    assert 'ocrd-foo' in [x for x, _ in mgr.find_resources()]
    assert 'ocrd-foo' in [x for x, _ in mgr.find_resources(url='http://foo/bar')]

def test_parameter_usage(tmp_path):
    mgr = OcrdResourceManager(xdg_config_home=tmp_path)
    assert mgr.parameter_usage('foo.bar') == 'foo.bar'
    assert mgr.parameter_usage('foo.bar', 'without-extension') == 'foo'
    with raises(ValueError, match='No such usage'):
        mgr.parameter_usage('foo.bar', 'baz')

def test_default_resource_dir(tmp_path):
    mgr = OcrdResourceManager(xdg_data_home=tmp_path)
    assert mgr.xdg_config_home != mgr.xdg_data_home
    assert mgr.default_resource_dir == str(mgr.xdg_data_home / 'ocrd-resources')

if __name__ == "__main__":
    main(__file__)
