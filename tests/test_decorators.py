import click
from click.testing import CliRunner

from tests.base import TestCase, main

from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_loglevel, ocrd_cli_wrap_processor
from ocrd_utils.logging import setOverrideLogLevel, initLogging

@click.command()
@ocrd_cli_options
def cli_with_ocrd_cli_options(*args, **kwargs): pass # pylint: disable=unused-argument, multiple-statements

@click.command()
@ocrd_loglevel
def cli_with_ocrd_loglevel(*args, **kwargs): pass # pylint: disable=unused-argument, multiple-statements

DUMMY_TOOL = {'executable': 'ocrd-test', 'steps': ['recognition/post-correction']}

class DummyProcessor(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

    def process(self):
        #  print('# nope')
        pass

@click.command()
@ocrd_cli_options
def cli_dummy_processor(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)


class TestDecorators(TestCase):

    def setUp(self):
        initLogging()
        self.runner = CliRunner()

    def test_minimal(self):
        result = self.runner.invoke(cli_with_ocrd_cli_options, [])
        self.assertEqual(result.exit_code, 0)

    def test_loglevel_invalid(self):
        result = self.runner.invoke(cli_with_ocrd_loglevel, ['--log-level', 'foo'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('invalid choice: foo', result.output)

    def test_loglevel_override(self):
        import logging
        self.assertEqual(logging.getLogger('').getEffectiveLevel(), logging.INFO)
        self.assertEqual(logging.getLogger('PIL').getEffectiveLevel(), logging.INFO)
        result = self.runner.invoke(cli_with_ocrd_loglevel, ['--log-level', 'DEBUG'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(logging.getLogger('PIL').getEffectiveLevel(), logging.DEBUG)
        setOverrideLogLevel('INFO')

    def test_processor(self):
        result = self.runner.invoke(cli_dummy_processor, ['--dump-json'])
        self.assertEqual(result.exit_code, 0)
        result = self.runner.invoke(cli_dummy_processor, ['--version'])
        self.assertEqual(result.exit_code, 0)

if __name__ == '__main__':
    main()
