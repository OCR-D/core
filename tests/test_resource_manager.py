from contextlib import contextmanager
from pathlib import Path
from tests.base import TestCase, main # pylint: disable=import-error,no-name-in-module

from pytest import fixture

from ocrd_utils import pushd_popd, initLogging
import ocrd_utils.constants
from ocrd.resource_manager import OcrdResourceManager

@contextmanager
def monkey_patch_temp_xdg():
    with pushd_popd(tempdir=True) as tempdir:
        old_config = ocrd_utils.constants.XDG_CONFIG_HOME
        old_data = ocrd_utils.constants.XDG_DATA_HOME
        ocrd_utils.constants.XDG_CONFIG_HOME = tempdir
        ocrd_utils.constants.XDG_DATA_HOME = tempdir
        yield tempdir
        ocrd_utils.constants.XDG_CONFIG_HOME = old_config
        ocrd_utils.constants.XDG_DATA_HOME = old_data

def test_config_created():
    with monkey_patch_temp_xdg() as tempdir:
        mgr = OcrdResourceManager()
        assert Path(tempdir, 'ocrd', 'resources.yml').exists()

def test_add_to_user_database_new():
    with monkey_patch_temp_xdg() as tempdir:
        mgr = OcrdResourceManager()
        ret = mgr.add_to_user_database('ocrd-foo', Path(tempdir, 'ocrd', 'resources.yml'))
        ret = mgr.add_to_user_database('ocrd-foo', Path(tempdir, 'ocrd', 'resources.yml'))
        assert ret
        mgr.list_installed()

def test_add_to_user_database_existing():
    with monkey_patch_temp_xdg() as tempdir:
        mgr = OcrdResourceManager()
        proc = 'ocrd-anybaseocr-layout-analysis'
        url = 'https://ocr-d-repo.scc.kit.edu/models/dfki/layoutAnalysis/mapping_densenet.pickle'
        fpath = mgr.download(proc, url, mgr.location_to_resource_dir('data'))
        assert fpath.exists()
        ret = mgr.add_to_user_database(proc, fpath)
        ret = mgr.add_to_user_database(proc, fpath)
        assert ret

if __name__ == "__main__":
    main(__file__)
