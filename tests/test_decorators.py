import json
import logging
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from os.path import join

import click
from click.testing import CliRunner

from tests.base import CapturingTestCase as TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from tests.data import DummyProcessor, DUMMY_TOOL

from ocrd import Resolver
from ocrd.decorators import (
    ocrd_cli_options,
    ocrd_loglevel,
    ocrd_cli_wrap_processor,
)    # pylint: disable=protected-access
from ocrd_utils import pushd_popd, VERSION as OCRD_VERSION

@click.command()
@ocrd_cli_options
def cli_with_ocrd_cli_options(*args, **kwargs):      # pylint: disable=unused-argument
    pass

@click.command()
@ocrd_cli_options
def cli_param_dumper(*args, **kwargs):      # pylint: disable=unused-argument
    print(json.dumps(kwargs['parameter']))

@click.command()
@ocrd_loglevel
def cli_with_ocrd_loglevel(*args, **kwargs):         # pylint: disable=unused-argument
    pass

@click.command()
@ocrd_cli_options
def cli_dummy_processor(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)

DEFAULT_IN_OUT = ('-I', 'OCR-D-IMG', '-O', 'OUTPUT')

class TestDecorators(TestCase):

    def test_minimal(self):
        exit_code, out, err = self.invoke_cli(cli_with_ocrd_cli_options, ['-l', 'DEBUG'])
        print(out, err)
        assert not exit_code

    def test_loglevel_invalid(self):
        code, _, err = self.invoke_cli(cli_with_ocrd_loglevel, ['--log-level', 'foo'])
        assert code
        self.assertIn('invalid choice: foo', err)

    def test_loglevel_override(self):
        self.assertEqual(logging.getLogger('').getEffectiveLevel(), logging.INFO)
        self.assertEqual(logging.getLogger('PIL').getEffectiveLevel(), logging.INFO)
        code, _, _ = self.invoke_cli(cli_with_ocrd_loglevel, ['--log-level', 'DEBUG'])
        assert not code
        self.assertEqual(logging.getLogger('PIL').getEffectiveLevel(), logging.DEBUG)

    def test_processor_no_mets(self):
        """
        https://github.com/OCR-D/spec/pull/156
        """
        with TemporaryDirectory() as tempdir:
            with pushd_popd(tempdir):
                _, out_help, _ = self.invoke_cli(cli_dummy_processor, ['--help'])
                exit_code, out_none, _ = self.invoke_cli(cli_dummy_processor, [])
                self.assertEqual(exit_code, 1)
                self.assertEqual(out_help, out_none)

    def test_processor_dump_json(self):
        exit_code, out, err = self.invoke_cli(cli_dummy_processor, ['--dump-json'])
        print("exit_code=%s\nout=%s\nerr=%s" % (exit_code, out, err))
        self.assertFalse(exit_code)

    def test_processor_version(self):
        code, out, err = self.invoke_cli(cli_dummy_processor, ['--version'])
        print(code, out, err)
        self.assertEqual(out, 'Version 0.0.1, ocrd/core %s\n' % OCRD_VERSION)
        assert not code

    # TODO cannot be tested in this way because logging is reused and not part of output
    # (but perhaps one could use.invoke_cli() instead;
    #  anyway, now calling with non-existing local METS paths will only show the help text)
    # def test_processor_non_existing_mets(self):
    #     code, out, err = self.invoke_cli(cli_dummy_processor, ['-m', 'exist.xml', *DEFAULT_IN_OUT])
    #     print("code=%s\nout=%s\nerr=%s" % (code, out, err))
    #     self.assertIn('File does not exist: /does/not/exist.xml', out)
    #     self.assertEqual(code, 1)

    def test_processor_run(self):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as tempdir:
            with pushd_popd(tempdir):
                exit_code, out, err = self.invoke_cli(cli_dummy_processor, ['-p', '{"baz": "forty-two"}', '--mets', 'mets.xml', *DEFAULT_IN_OUT])
                assert not exit_code

    def test_param_merging(self):
        json1 = '{"foo": 23, "bar": 100}'
        json2 = '{"foo": 42}'
        _, out, _ = self.invoke_cli(cli_param_dumper, [*DEFAULT_IN_OUT, '-p', json1, '-p', json2])
        try:
            self.assertEqual(out, '{"foo": 42, "bar": 100}\n')
        except AssertionError:
            self.assertEqual(out, '{"bar": 100, "foo": 42}\n')



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

    def test_parameter_override_basic(self):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as tempdir:
            with pushd_popd(tempdir):
                code, out, err = self.invoke_cli(cli_dummy_processor, [
                    '-p', '{"baz": "forty-two"}',
                    '-P', 'baz', 'one',
                    '-P', 'baz', 'two',
                    *DEFAULT_IN_OUT
                ])
                print(out)
                self.assertEqual(out, '{"baz": "two"}\n')

    def test_parameter_override_wo_param(self):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as tempdir:
            with pushd_popd(tempdir):
                code, out, err = self.invoke_cli(cli_dummy_processor, [
                    '-P', 'baz', 'two',
                    *DEFAULT_IN_OUT
                ])
                print(out)
                self.assertEqual(out, '{"baz": "two"}\n')

if __name__ == '__main__':
    main(__file__)
