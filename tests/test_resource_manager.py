# -*- coding: utf-8 -*-

import os
import pathlib

from tests.base import main

CONST_RESOURCE_YML = 'resources.yml'
CONST_RESOURCE_URL_LAYOUT = 'https://ocr-d-repo.scc.kit.edu/models/dfki/layoutAnalysis/mapping_densenet.pickle'

def test_resources_manager_config_default():

    # arrange
    from ocrd.resource_manager import OcrdResourceManager

    # act
    mgr = OcrdResourceManager()

    #
    default_config_dir = os.path.join(os.environ['HOME'], '.config', 'ocrd')
    f = pathlib.Path(default_config_dir) / CONST_RESOURCE_YML
    assert f.exists()
    assert f == mgr.user_list
    assert mgr.add_to_user_database('ocrd-foo', f)
    mgr.list_installed()
    proc = 'ocrd-anybaseocr-layout-analysis'
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)


def test_resources_manager_from_environment(tmp_path, monkeypatch):

    # arrange
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    from ocrd.resource_manager import OcrdResourceManager
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path))

    # act
    mgr = OcrdResourceManager()

    #
    f = tmp_path / 'ocrd' / CONST_RESOURCE_YML
    assert f.exists()
    assert f == mgr.user_list
    assert mgr.add_to_user_database('ocrd-foo', f)
    mgr.list_installed()
    proc = 'ocrd-anybaseocr-layout-analysis'
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)


def test_resources_manager_config_explicite(tmp_path):

    # arrange
    from ocrd.resource_manager import OcrdResourceManager

    # act
    mgr = OcrdResourceManager(xdb_config_home=str(tmp_path), xdb_data_home=str(tmp_path))

    #
    f = tmp_path / 'ocrd' / CONST_RESOURCE_YML
    assert f.exists()
    assert f == mgr.user_list
    assert mgr.add_to_user_database('ocrd-foo', f)
    mgr.list_installed()
    proc = 'ocrd-anybaseocr-layout-analysis'
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)


if __name__ == "__main__":
    main(__file__)
