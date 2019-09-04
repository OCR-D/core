from tempfile import TemporaryDirectory
from pathlib import Path

import click
from click.testing import CliRunner

from tests.base import TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module

from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_loglevel, ocrd_cli_wrap_processor
from ocrd_utils.logging import setOverrideLogLevel, initLogging
from ocrd_utils import pushd_popd

@click.command()
@ocrd_cli_options
def cli_with_ocrd_cli_options(*args, **kwargs):      # pylint: disable=unused-argument
    pass

@click.command()
@ocrd_loglevel
def cli_with_ocrd_loglevel(*args, **kwargs):         # pylint: disable=unused-argument
    pass

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

    def test_processor_dump_json(self):
        result = self.runner.invoke(cli_dummy_processor, ['--dump-json'])
        self.assertEqual(result.exit_code, 0)

    def test_processor_version(self):
        result = self.runner.invoke(cli_dummy_processor, ['--version'])
        self.assertEqual(result.exit_code, 0)

    def test_processor_non_existing_mets(self):
        result = self.runner.invoke(cli_dummy_processor, ['--mets', 'file:///does/not/exist.xml'])
        self.assertIn('File does not exist: file:///does/not/exist.xml', result.output)
        self.assertEqual(result.exit_code, 1)

    def test_processor_run(self):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as tempdir:
            with pushd_popd(tempdir):
                result = self.runner.invoke(cli_dummy_processor, ['--mets', 'mets.xml'])
                self.assertEqual(result.exit_code, 0)

    def test_parameters(self):
        from ocrd.decorators import _parse_json_string_or_file      # pylint: disable=protected-access
        self.assertEqual(_parse_json_string_or_file(None, None), {})
        self.assertEqual(_parse_json_string_or_file(None, None, '{}'), {})
        self.assertEqual(_parse_json_string_or_file(None, None, '{"foo": 32}'), {'foo': 32})
        self.assertEqual(_parse_json_string_or_file(None, None, '{"foo": 32}'), {'foo': 32})
        with TemporaryDirectory() as tempdir:
            paramfile = Path(tempdir, '{}') # XXX yes, the file is called '{}'
            with open(paramfile, 'w') as f:
                f.write('{"bar": 42}')
            self.assertEqual(_parse_json_string_or_file(None, None, paramfile), {'bar': 42})
            with pushd_popd(tempdir):
                self.assertEqual(_parse_json_string_or_file(None, None), {'bar': 42})


if __name__ == '__main__':
    main()
