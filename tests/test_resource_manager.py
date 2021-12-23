# -*- coding: utf-8 -*-

import os
import pathlib

from ocrd.resource_manager import OcrdResourceManager

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
    fpath = mgr.download(proc, CONST_RESOURCE_URL_LAYOUT, mgr.location_to_resource_dir('data'))
    assert fpath.exists()
    assert mgr.add_to_user_database(proc, fpath)


def test_resources_manager_from_environment(tmp_path, monkeypatch):

    # arrange
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path))

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


if __name__ == "__main__":
    main(__file__)
