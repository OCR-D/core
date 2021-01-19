from tests.base import main
from unittest import mock

import ocrd_utils

def test_config_loading():
    XDG_CONFIG_HOME_before = ocrd_utils.XDG_CONFIG_HOME
    with ocrd_utils.pushd_popd(tempdir=True) as tempdir:
        ocrd_utils.XDG_CONFIG_HOME = tempdir
        with open('ocrd.yml', 'w', encoding='utf-8') as f:
            f.write('resource_location: cache\n')
        from ocrd.config import load_config_file
        obj = load_config_file()
        assert obj.dump() == {'resource_location': 'cache'}
    ocrd_utils.XDG_CONFIG_HOME = XDG_CONFIG_HOME_before

if __name__ == '__main__':
    main(__file__)
