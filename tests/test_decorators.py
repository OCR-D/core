
import click
from click.testing import CliRunner

from tests.base import CapturingTestCase as TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module

from ocrd import Processor
from ocrd.decorators import (
    ocrd_cli_options,
    ocrd_loglevel,
    ocrd_cli_wrap_processor,
)    # pylint: disable=protected-access
from ocrd_utils.logging import initLogging
from ocrd_utils import pushd_popd, VERSION as OCRD_VERSION

@click.command()
@ocrd_cli_options
def cli_with_ocrd_cli_options(*args, **kwargs):      # pylint: disable=unused-argument
    pass

@click.command()
@ocrd_loglevel
def cli_with_ocrd_loglevel(*args, **kwargs):         # pylint: disable=unused-argument
    pass

DUMMY_TOOL = {
    'executable': 'ocrd-test',
    'steps': ['recognition/post-correction'],
    'description': 'A dummy processor for testing sigh',
    'parameters': {
        'foo': {
            'type': 'number',
            'description': 'dummy parameter for a dummy procesor',
            'required': True
        }
    }
}

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
        initLogging()

    def test_processor_no_mets(self):
        """
        https://github.com/OCR-D/spec/pull/156
        """
        _, out_help, _ = self.invoke_cli(cli_dummy_processor, ['--help'])
        exit_code, out_none, _ = self.invoke_cli(cli_dummy_processor, [])
        self.assertEqual(exit_code, 1)
        self.assertEqual(out_help, out_none)

    def test_processor_dump_json(self):
        result = self.runner.invoke(cli_dummy_processor, ['--dump-json'])
        self.assertEqual(result.exit_code, 0)

    def test_processor_version(self):
        result = self.runner.invoke(cli_dummy_processor, ['--version'])
        self.assertEqual(result.output, 'Version 0.0.1, ocrd/core %s\n' % OCRD_VERSION)
        self.assertEqual(result.exit_code, 0)

    # XXX cannot be tested in this way because logging is reused and not part of output
    #  def test_processor_non_existing_mets(self):
    #      result = self.runner.invoke(cli_dummy_processor, ['--mets', 'file:///does/not/exist.xml'])
    #      #  self.assertIn('File does not exist: file:///does/not/exist.xml', result.output)
    #      self.assertEqual(result.exit_code, 1)

    def test_processor_run(self):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as tempdir:
            with pushd_popd(tempdir):
                exit_code, out, err = self.invoke_cli(cli_dummy_processor, ['-p', '{"foo": 42}', '--mets', 'mets.xml', '-I', 'OCR-D-IMG'])
                self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    main(__file__)
