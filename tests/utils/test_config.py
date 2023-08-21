from os import environ
from contextlib import contextmanager

from pytest import raises

from ocrd_utils.config import config, OcrdEnvConfig

@contextmanager
def temp_env_var(k, v):
    v_before = environ.get(k, None)
    environ[k] = v
    yield
    if v_before is not None:
        environ[k] = v_before
    else:
        environ.pop(k)

def test_str():
    c = OcrdEnvConfig()
    v = c.add('OCRD_FOO_BAR_ETC', description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus lacinia, eros id accumsan tempor, arcu augue viverra est, quis ultrices lectus eros et quam. Donec vel metus iaculis, maximus enim eget, mattis leo. Morbi molestie placerat dolor non finibus. Vivamus egestas rutrum est quis gravida. Vivamus sed cursus lectus. Etiam sed felis nisl. Suspendisse massa nunc, eleifend vitae pretium sit amet, porta et velit. Pellentesque risus justo, tincidunt at mattis ac, sollicitudin sit amet quam. Donec euismod suscipit bibendum.", default=(True, lambda: 42))
    print(c.describe('OCRD_FOO_BAR_ETC'))
    assert c.describe('OCRD_FOO_BAR_ETC') == """\
  OCRD_FOO_BAR_ETC
    Lorem ipsum dolor sit amet, consectetur
    adipiscing elit. Phasellus lacinia, eros id
    accumsan tempor, arcu augue viverra est, quis
    ultrices lectus eros et quam. Donec vel metus
    iaculis, maximus enim eget, mattis leo. Morbi
    molestie placerat dolor non finibus. Vivamus
    egestas rutrum est quis gravida. Vivamus sed
    cursus lectus. Etiam sed felis nisl.
    Suspendisse massa nunc, eleifend vitae pretium
    sit amet, porta et velit. Pellentesque risus
    justo, tincidunt at mattis ac, sollicitudin
    sit amet quam. Donec euismod suscipit
    bibendum. (Default: "42")"""

def test_OCRD_METS_CACHING():
    with temp_env_var('OCRD_METS_CACHING', 'true'):
        assert config.OCRD_METS_CACHING == True
    with temp_env_var('OCRD_METS_CACHING', '1'):
        assert config.OCRD_METS_CACHING == True
    with temp_env_var('OCRD_METS_CACHING', '0'):
        assert config.OCRD_METS_CACHING == False
    with temp_env_var('OCRD_METS_CACHING', 'false'):
        assert config.OCRD_METS_CACHING == False
    with temp_env_var('OCRD_METS_CACHING', 'some other value'):
        with raises(ValueError, match="'OCRD_METS_CACHING' set to invalid value 'some other value'"):
            config.OCRD_METS_CACHING

def test_OCRD_PROFILE():
    with temp_env_var('OCRD_PROFILE', ''):
        config.OCRD_PROFILE
    with temp_env_var('OCRD_PROFILE', 'CPU'):
        config.OCRD_PROFILE
    with temp_env_var('OCRD_PROFILE', 'RSS,CPU'):
        config.OCRD_PROFILE
    with temp_env_var('OCRD_PROFILE', 'some other value'):
        with raises(ValueError, match="'OCRD_PROFILE' set to invalid value 'some other value'"):
            config.OCRD_PROFILE
