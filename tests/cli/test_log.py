import click
from os import environ as ENV

# pylint: disable=import-error, no-name-in-module
from tests.base import main, assets, copy_of_directory, ocrd_logging_enabled, temp_env_var, _invoke_cli

from ocrd.cli import log_cli
from ocrd.decorators import ocrd_loglevel
from ocrd_utils import setOverrideLogLevel, logging, getLogger
import logging as python_logging

@click.group()
@ocrd_loglevel
def mock_ocrd_cli(log_level):
    pass
mock_ocrd_cli.add_command(log_cli)

def test_loglevel(invoke_cli):
    assert 'DEBUG ocrd.log_cli - foo' not in invoke_cli(mock_ocrd_cli, ['log', 'warning', 'foo'])[2]
    assert 'DEBUG ocrd.log_cli - foo' in invoke_cli(mock_ocrd_cli, ['-l', 'DEBUG', 'log', 'debug', 'foo'])[2]

def test_log_basic(invoke_cli):
    assert 'INFO ocrd.log_cli - foo bar' in invoke_cli(mock_ocrd_cli, ['log', 'info', 'foo bar'])[2]

def test_log_name_param(invoke_cli):
    assert 'INFO ocrd.boo.far - foo bar' in invoke_cli(mock_ocrd_cli, ['log', '--name', 'boo.far', 'info', 'foo bar'])[2]

def test_log_name_envvar(invoke_cli):
    with temp_env_var('OCRD_TOOL_NAME', 'boo.far'):
        assert 'INFO ocrd.boo.far - foo bar' in invoke_cli(mock_ocrd_cli, ['log', 'info', 'foo bar'])[2]

def test_log_name_levels(invoke_cli):
    with temp_env_var('OCRD_TOOL_NAME', 'foo'):
        assert 'DEBUG ocrd.foo - foo' in invoke_cli(mock_ocrd_cli, ['-l', 'DEBUG', 'log', 'debug', 'foo'])[2]
        assert 'DEBUG ocrd.foo - foo' in invoke_cli(mock_ocrd_cli, ['-l', 'DEBUG', 'log', 'trace', 'foo'])[2]
        assert 'INFO ocrd.foo - foo' in  invoke_cli(mock_ocrd_cli, ['log', 'info', 'foo'])[2]
        assert 'WARNING ocrd.foo - foo' in  invoke_cli(mock_ocrd_cli, ['log', 'warning', 'foo'])[2]
        assert 'ERROR ocrd.foo - foo' in  invoke_cli(mock_ocrd_cli, ['log', 'error', 'foo'])[2]
        assert 'CRITICAL ocrd.foo - foo' in  invoke_cli(mock_ocrd_cli, ['log', 'critical', 'foo'])[2]

def test_log_error(invoke_cli):
    assert 'Logging error' not in invoke_cli(mock_ocrd_cli, ['log', '-n', 'foo',  'info', 'foo bar', 'foo bar'])[2]

def test_log_override(invoke_cli):
    assert 'DEBUG' not in invoke_cli(mock_ocrd_cli, ['-l', 'INFO', 'log', 'debug', 'foo'])[2]


# if __name__ == '__main__':
#     main(__file__)
