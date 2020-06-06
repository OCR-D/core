from click.testing import CliRunner
from ocrd.cli import log_cli
from os import environ as ENV

# pylint: disable=import-error, no-name-in-module
from tests.base import TestCase, main, assets, copy_of_directory

from ocrd_utils import setOverrideLogLevel
class TestLogCli(TestCase):

    def setUp(self):
        self.runner = CliRunner(mix_stderr=False)

    def tearDown(self):
        if 'OCRD_TOOL_NAME' in ENV:
            del(ENV['OCRD_TOOL_NAME'])

    def test_log_basic(self):
        result = self.runner.invoke(log_cli, ['info', 'foo bar'])
        # XXX TODO why is logged to STDERR, not STDOUT?
        self.assertIn('INFO root - foo bar', result.stderr)

    def test_log_name_param(self):
        result = self.runner.invoke(log_cli, ['--name', 'boo.far', 'info', 'foo bar'])
        self.assertIn('INFO boo.far - foo bar', result.stderr)

    def test_log_name_envvar(self):
        ENV['OCRD_TOOL_NAME'] = 'boo.far'
        result = self.runner.invoke(log_cli, ['info', 'foo bar'])
        self.assertIn('INFO boo.far - foo bar', result.stderr)

    def test_log_name_levels(self):
        ENV['OCRD_TOOL_NAME'] = 'ocrd.foo'
        self.assertIn('DEBUG ocrd.foo - foo', self.runner.invoke(log_cli, ['debug', 'foo']).stderr)
        self.assertIn('DEBUG ocrd.foo - foo', self.runner.invoke(log_cli, ['trace', 'foo']).stderr)
        self.assertIn('INFO ocrd.foo - foo', self.runner.invoke(log_cli, ['info', 'foo']).stderr)
        self.assertIn('WARNING ocrd.foo - foo', self.runner.invoke(log_cli, ['warning', 'foo']).stderr)
        self.assertIn('ERROR ocrd.foo - foo', self.runner.invoke(log_cli, ['error', 'foo']).stderr)
        self.assertIn('CRITICAL ocrd.foo - foo', self.runner.invoke(log_cli, ['critical', 'foo']).stderr)


if __name__ == '__main__':
    main()
