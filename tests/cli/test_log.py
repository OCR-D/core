import click
from os import environ as ENV

# pylint: disable=import-error, no-name-in-module
from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory, ocrd_logging_enabled, temp_env_var

from ocrd.cli import log_cli
from ocrd.decorators import ocrd_loglevel
from ocrd_utils import setOverrideLogLevel, logging, disableLogging
import logging as python_logging

@click.group()
@ocrd_loglevel
def mock_ocrd_cli(log_level):
    pass
mock_ocrd_cli.add_command(log_cli)

class TestLogCli(TestCase):

    def _get_log_output(self, *args):
        # assert 0
        code, out, err = self.invoke_cli(mock_ocrd_cli, args)
        # print({'code': code, 'out': out, 'err': err})
        print('out', out)
        print('err', err)
        return err

    def test_loglevel(self):
        assert 'DEBUG ocrd.log_cli - foo' not in self._get_log_output('log', 'debug', 'foo')
        assert 'DEBUG ocrd.log_cli - foo' in self._get_log_output('-l', 'DEBUG', 'log', 'debug', 'foo')

    def test_log_basic(self):
        assert 'INFO ocrd.log_cli - foo bar' in self._get_log_output('log', 'info', 'foo bar')

    def test_log_name_param(self):
        assert 'INFO ocrd.boo.far - foo bar' in self._get_log_output('log', '--name', 'boo.far', 'info', 'foo bar')

    def test_log_name_envvar(self):
        with temp_env_var('OCRD_TOOL_NAME', 'boo.far'):
            assert 'INFO ocrd.boo.far - foo bar' in self._get_log_output('log', 'info', 'foo bar')

    def test_log_name_levels(self):
        with temp_env_var('OCRD_TOOL_NAME', 'foo'):
            assert 'DEBUG ocrd.foo - foo' in self._get_log_output('-l', 'DEBUG', 'log', 'debug', 'foo')
            assert 'DEBUG ocrd.foo - foo' in self._get_log_output('-l', 'DEBUG', 'log', 'trace', 'foo')
            assert 'INFO ocrd.foo - foo' in  self._get_log_output('log', 'info', 'foo')
            assert 'WARNING ocrd.foo - foo' in  self._get_log_output('log', 'warning', 'foo')
            assert 'ERROR ocrd.foo - foo' in  self._get_log_output('log', 'error', 'foo')
            assert 'CRITICAL ocrd.foo - foo' in  self._get_log_output('log', 'critical', 'foo')

    def test_log_error(self):
        assert 'Logging error' not in self._get_log_output('log', '-n', 'foo',  'info', 'foo bar', 'foo bar')

    def test_log_override(self):
        assert 'DEBUG' not in self._get_log_output('-l', 'INFO', 'log', 'debug', 'foo')


if __name__ == '__main__':
    main(__file__)
