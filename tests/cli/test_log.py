import click
from ocrd.cli import log_cli
from os import environ as ENV

# pylint: disable=import-error, no-name-in-module
from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory

from ocrd.decorators import ocrd_loglevel
from ocrd_utils import initLogging, setOverrideLogLevel, logging, disableLogging

@click.group()
@ocrd_loglevel
def mock_ocrd_cli(log_level):
    pass
mock_ocrd_cli.add_command(log_cli)

class TestLogCli(TestCase):

    def _get_log_output(self, *args):
        disableLogging()
        code, out, err = self.invoke_cli(mock_ocrd_cli, args)
        print(code, out, err)
        return out + err

    def tearDown(self):
        if 'OCRD_TOOL_NAME' in ENV:
            del(ENV['OCRD_TOOL_NAME'])

    def test_loglevel(self):
        assert ' DEBUG root - foo' not in self._get_log_output('log', 'debug', 'foo')
        assert ' DEBUG root - foo' in self._get_log_output('-l', 'DEBUG', 'log', 'debug', 'foo')

    def test_log_basic(self):
        assert 'INFO root - foo bar' in self._get_log_output('log', 'info', 'foo bar')

    def test_log_name_param(self):
        assert 'INFO boo.far - foo bar' in self._get_log_output('log', '--name', 'boo.far', 'info', 'foo bar')

    def test_log_name_envvar(self):
        ENV['OCRD_TOOL_NAME'] = 'boo.far'
        assert 'INFO boo.far - foo bar' in self._get_log_output('log', 'info', 'foo bar')

    def test_log_name_levels(self):
        ENV['OCRD_TOOL_NAME'] = 'ocrd.foo'
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
