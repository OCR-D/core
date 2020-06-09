
import click
from contextlib import contextmanager
from click.testing import CliRunner
from tempfile import TemporaryDirectory
from os.path import join, exists

from tests.base import TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module

from ocrd import Processor, Resolver
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
    'parameters': {
        'foo': {
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
                result = self.runner.invoke(cli_dummy_processor, ['-p', '{"foo": 42}', '--mets', 'mets.xml', '-I', 'OCR-D-IMG'])
                self.assertEqual(result.exit_code, 0)


    @contextmanager
    def _sample_ws_for_overwrite(self):
        resolver = Resolver()
        with TemporaryDirectory() as tempdir:
            ws = resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('IN-GRP',  pageId='pID1', ID='fID1', mimetype='image/tiff', content='CONTENT', local_filename=join(tempdir, 'ID1.tif'))
            ws.add_file('OUT-GRP', pageId='pID2', ID='fID2', mimetype='image/tiff', content='CONTENT', local_filename=join(tempdir, 'ID2.tif'))
            ws.add_file('OUT-GRP', pageId='pID3', ID='fID3', mimetype='image/tiff', content='CONTENT', local_filename=join(tempdir, 'ID3.tif'))
            ws.add_file('OUT-GRP', pageId='pID4', ID='fID4', mimetype='image/tiff', content='CONTENT', local_filename=join(tempdir, 'ID4.tif'))
            ws.save_mets()
            yield ws

    def test_overwrite_fail(self):
        with self._sample_ws_for_overwrite() as ws:
            with self.assertRaisesRegex(Exception, 'already in METS'):
                ocrd_cli_wrap_processor(
                    DummyProcessor,
                    ocrd_tool=DUMMY_TOOL,
                    mets=ws.mets_target,
                    input_file_grp='IN-GRP',
                    output_file_grp='OUT-GRP',
                )
            # with overwrite, it shouldn't fail
            ocrd_cli_wrap_processor(
                DummyProcessor,
                ocrd_tool=DUMMY_TOOL,
                mets=ws.mets_target,
                input_file_grp='IN-GRP',
                output_file_grp='OUT-GRP',
                overwrite=True
            )

    # XXX We cannot currently pre-emptively delete files because #505
    # def test_overwrite_group(self):
    #     with self._sample_ws_for_overwrite() as ws:
    #         self.assertTrue(exists(join(ws.directory, 'ID1.tif')), 'files exist')
    #         self.assertTrue(exists(join(ws.directory, 'ID2.tif')), 'files exist')
    #         self.assertTrue(exists(join(ws.directory, 'ID3.tif')), 'files exist')
    #         self.assertTrue(exists(join(ws.directory, 'ID4.tif')), 'files exist')
    #         ocrd_cli_wrap_processor(
    #             DummyProcessor,
    #             ocrd_tool=DUMMY_TOOL,
    #             mets=ws.mets_target,
    #             parameter={"foo": 42},
    #             input_file_grp='IN-GRP',
    #             output_file_grp='OUT-GRP',
    #             overwrite=True,
    #         )
    #         self.assertTrue(exists(join(ws.directory, 'ID1.tif')), 'files exist')
    #         # self.assertFalse(exists(join(ws.directory, 'ID2.tif')), 'files deleted')
    #         # self.assertFalse(exists(join(ws.directory, 'ID3.tif')), 'files deleted')
    #         # self.assertFalse(exists(join(ws.directory, 'ID4.tif')), 'files deleted')

    # XXX We cannot currently pre-emptively delete files because #505
    # as it is the test therefore makes no sense
    # def test_overwrite_group_page_id(self):
    #     with self._sample_ws_for_overwrite() as ws:
    #         self.assertTrue(exists(join(ws.directory, 'ID1.tif')), 'files exist')
    #         self.assertTrue(exists(join(ws.directory, 'ID2.tif')), 'files exist')
    #         self.assertTrue(exists(join(ws.directory, 'ID3.tif')), 'files exist')
    #         self.assertTrue(exists(join(ws.directory, 'ID4.tif')), 'files exist')
    #         ocrd_cli_wrap_processor(
    #             DummyProcessor,
    #             ocrd_tool=DUMMY_TOOL,
    #             mets=ws.mets_target,
    #             parameter={"foo": 42},
    #             input_file_grp='IN-GRP',
    #             output_file_grp='OUT-GRP',
    #             overwrite=True,
    #             page_id='pID2,pID4'
    #         )
    #         self.assertTrue(exists(join(ws.directory, 'ID1.tif')), 'files exist')
    #         self.assertFalse(exists(join(ws.directory, 'ID2.tif')), 'files deleted')
    #         self.assertTrue(exists(join(ws.directory, 'ID3.tif')), 'files exist')
    #         self.assertFalse(exists(join(ws.directory, 'ID4.tif')), 'files deleted')


if __name__ == '__main__':
    main(__file__)
