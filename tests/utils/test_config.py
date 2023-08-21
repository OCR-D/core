from os import environ
from contextlib import contextmanager

from pytest import raises

from ocrd_utils.config import config

@contextmanager
def temp_env_var(k, v):
    v_before = environ.get(k, None)
    environ[k] = v
    yield
    if v_before is not None:
        environ[k] = v_before
    else:
        environ.pop(k)

def test_OCRD_METS_CACHING():
    with temp_env_var('OCRD_METS_CACHING', 'true'):
        assert config.OCRD_METS_CACHING == True
    with temp_env_var('OCRD_METS_CACHING', '1'):
        assert config.OCRD_METS_CACHING == True
    with temp_env_var('OCRD_METS_CACHING', '0'):
        assert config.OCRD_METS_CACHING == False
    with temp_env_var('OCRD_METS_CACHING', 'false'):
        assert config.OCRD_METS_CACHING == False
    with temp_env_var('OCRD_METS_CACHING', 'some other random value'):
        with raises(ValueError, match="'OCRD_METS_CACHING' set to invalid value 'some other random value'"):
            config.OCRD_METS_CACHING
