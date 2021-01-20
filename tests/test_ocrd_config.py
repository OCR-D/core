from tests.base import main
from unittest import mock
from pathlib import Path

from ocrd_utils import pushd_popd
from ocrd.config import load_config_file

def test_config_loading():
    with pushd_popd(tempdir=True) as tempdir:
        Path('ocrd').mkdir()
        with open('ocrd/config.yml', 'w', encoding='utf-8') as f:
            f.write('resource_location: cache\n')
        obj = load_config_file(tempdir)
        assert obj.dump() == {'resource_location': 'cache'}

if __name__ == '__main__':
    main(__file__)
