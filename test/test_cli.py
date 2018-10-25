from test.base import TestCase, main
import click
from click.testing import CliRunner
from ocrd.decorators import ocrd_cli_options
from ocrd.logging import setOverrideLogLevel, initLogging

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs): # pylint: disable=unused-argument
    pass

class TestCli(TestCase):

    def setUp(self):
        initLogging()
        self.runner = CliRunner()

    def test_minimal(self):
        result = self.runner.invoke(cli, [])
        self.assertEqual(result.exit_code, 0)

    def test_loglevel_invalid(self):
        result = self.runner.invoke(cli, ['--log-level', 'foo'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('invalid choice: foo', result.output)

    def test_loglevel_override(self):
        import logging
        self.assertEqual(logging.getLogger('').getEffectiveLevel(), logging.INFO)
        self.assertEqual(logging.getLogger('PIL').getEffectiveLevel(), logging.INFO)
        result = self.runner.invoke(cli, ['--log-level', 'DEBUG'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(logging.getLogger('PIL').getEffectiveLevel(), logging.DEBUG)
        setOverrideLogLevel('INFO')



if __name__ == '__main__':
    main()
