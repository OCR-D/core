import click
from click.testing import CliRunner
from ocrd.cli import log_cli
from os import environ as ENV

# pylint: disable=import-error, no-name-in-module
from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory

from ocrd.decorators import ocrd_loglevel
from ocrd_utils import initLogging

@click.group()
@ocrd_loglevel
def mock_ocrd_cli(log_level):
    pass
mock_ocrd_cli.add_command(log_cli)

class TestLogCli(TestCase):

    def setUp(self):
        self.runner = CliRunner(mix_stderr=False)
        initLogging()

    def test_loglevel(self):
        _, _, err = self.invoke_cli(mock_ocrd_cli, ['log', 'debug', 'foo'])
        self.assertNotIn(' DEBUG root - foo', err)
        _, _, err = self.invoke_cli(mock_ocrd_cli, ['-l', 'DEBUG', 'log', 'debug', 'foo'])
        self.assertIn(' DEBUG root - foo', err)

    def tearDown(self):
        if 'OCRD_TOOL_NAME' in ENV:
            del(ENV['OCRD_TOOL_NAME'])

    def test_log_basic(self):
        exit_code, out, err = self.invoke_cli(log_cli, ['info', 'foo bar'])
        self.assertIn('INFO root - foo bar', err)

    def test_log_name_param(self):
        exit_code, out, err = self.invoke_cli(log_cli, ['--name', 'boo.far', 'info', 'foo bar'])
        self.assertIn('INFO boo.far - foo bar', err)

    def test_log_name_envvar(self):
        ENV['OCRD_TOOL_NAME'] = 'boo.far'
        exit_code, out, err  = self.invoke_cli(log_cli, ['info', 'foo bar'])
        self.assertIn('INFO boo.far - foo bar', err)

    def test_log_name_levels(self):
        ENV['OCRD_TOOL_NAME'] = 'ocrd.foo'
        self.assertIn('DEBUG ocrd.foo - foo', self.invoke_cli(mock_ocrd_cli, ['-l', 'DEBUG', 'log', 'debug', 'foo'])[2])
        self.assertIn('DEBUG ocrd.foo - foo', self.invoke_cli(log_cli, ['trace', 'foo'])[2])
        self.assertIn('INFO ocrd.foo - foo', self.invoke_cli(log_cli, ['info', 'foo'])[2])
        self.assertIn('WARNING ocrd.foo - foo', self.invoke_cli(log_cli, ['warning', 'foo'])[2])
        self.assertIn('ERROR ocrd.foo - foo', self.invoke_cli(log_cli, ['error', 'foo'])[2])
        self.assertIn('CRITICAL ocrd.foo - foo', self.invoke_cli(log_cli, ['critical', 'foo'])[2])

    def test_log_error(self):
        code, out, err  = self.invoke_cli(log_cli, ['-n', 'foo',  'info', 'foo bar', 'foo bar'])
        print('code=%s out=%s err=%s' % (code, out, err))
        assert 'Logging error' not in err


if __name__ == '__main__':
    main(__file__)
