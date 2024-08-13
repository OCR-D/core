import json
from contextlib import ExitStack

from tempfile import TemporaryDirectory
from pathlib import Path
from os import environ
from tests.base import CapturingTestCase as TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from tests.data import DummyProcessor, DummyProcessorWithRequiredParameters, DummyProcessorWithOutput, IncompleteProcessor

from ocrd_utils import MIMETYPE_PAGE, pushd_popd, initLogging, disableLogging
from ocrd.resolver import Resolver
from ocrd.processor.base import Processor, run_processor, run_cli

from unittest import mock
import pytest

class TestProcessor(TestCase):

    def setUp(self):
        super().setUp()
        # make sure we get an isolated temporary copy of the testdata each time
        # as long as we are not using pytest but unittest, we need to manage contexts
        # (enterContext is only supported starting with py311)
        with ExitStack() as stack:
            self.resolver = Resolver()
            self.workdir = stack.enter_context(copy_of_directory(assets.path_to('SBB0000F29300010000/data')))
            stack.enter_context(pushd_popd(self.workdir))
            self.workspace = self.resolver.workspace_from_url('mets.xml')
            self.addCleanup(stack.pop_all().close)

    def test_incomplete_processor(self):
        proc = IncompleteProcessor(None)
        proc.input_file_grp = 'OCR-D-IMG'
        proc.output_file_grp = 'DUMMY'
        proc.page_id = None
        with self.assertRaises(NotImplementedError):
            proc.process_workspace(self.workspace)

    def test_no_resolver(self):
        with self.assertRaisesRegex(Exception, 'pass a resolver to create a workspace'):
            run_processor(DummyProcessor)

    def test_no_mets_url(self):
        with self.assertRaisesRegex(Exception, 'pass mets_url to create a workspace'):
            run_processor(DummyProcessor, resolver=self.resolver)

    def test_no_input_file_grp(self):
        processor = run_processor(DummyProcessor,
                                  resolver=self.resolver,
                                  workspace=self.workspace)
        with self.assertRaisesRegex(Exception, 'Processor is missing input fileGrp'):
            _ = processor.input_files

    def test_with_mets_url_input_files(self):
        assert len(list(self.workspace.mets.find_files(fileGrp='OCR-D-SEG-PAGE'))) == 2
        processor = run_processor(DummyProcessor,
                                  input_file_grp='OCR-D-SEG-PAGE',
                                  resolver=self.resolver,
                                  workspace=self.workspace)
        processor.workspace = self.workspace
        assert len(processor.input_files) == 2
        assert [f.mimetype for f in processor.input_files] == [MIMETYPE_PAGE, MIMETYPE_PAGE]

    def test_parameter(self):
        with TemporaryDirectory():
            jsonpath = 'params.json'
            with open(jsonpath, 'w') as f:
                f.write('{"baz": "quux"}')
            with open(jsonpath, 'r') as f:
                processor = run_processor(
                    DummyProcessor,
                    parameter=json.load(f),
                    input_file_grp="OCR-D-IMG",
                    resolver=self.resolver,
                    workspace=self.workspace
                )
                self.assertEqual(processor.parameter['baz'], 'quux')

    def test_verify(self):
        proc = DummyProcessor(None)
        with self.assertRaises(AttributeError):
            proc.verify()
        proc.workspace = self.workspace
        proc.input_file_grp = "OCR-D-IMG"
        proc.output_file_grp = "DUMMY"
        self.assertEqual(proc.verify(), True)

    def test_json(self):
        DummyProcessor(None).dump_json()

    def test_params_missing_required(self):
        with self.assertRaisesRegex(Exception, 'is a required property'):
            DummyProcessorWithRequiredParameters(None)

    def test_params_preset_resolve(self):
        with pushd_popd(tempdir=True) as tempdir:
            with mock.patch.dict(environ, {'XDG_DATA_HOME': str(tempdir)}):
                path = Path(tempdir) / 'ocrd-resources' / 'ocrd-dummy'
                path.mkdir(parents=True)
                path = str(path / 'preset.json')
                with open(path, 'w') as out:
                    # it would be nicer to test some existing processor which does take params
                    out.write('{}')
                assert 0 == run_cli("ocrd-dummy",
                                    resolver=Resolver(),
                                    mets_url=self.workspace.mets_target,
                                    input_file_grp="OCR-D-IMG",
                                    output_file_grp="DUMMY",
                                    parameter=path)
                assert 0 == run_cli("ocrd-dummy",
                                    resolver=Resolver(),
                                    mets_url=self.workspace.mets_target,
                                    input_file_grp="OCR-D-IMG",
                                    output_file_grp="DUMMY",
                                    parameter='preset.json',
                                    overwrite=True)

    def test_params(self):
        class ParamTestProcessor(Processor):
            @property
            def ocrd_tool(self):
                return {}
        proc = ParamTestProcessor(None)
        self.assertEqual(proc.parameter, {})

    def test_run_agent(self):
        no_agents_before = len(self.workspace.mets.agents)
        run_processor(DummyProcessor, workspace=self.workspace, input_file_grp="OCR-D-IMG")
        self.assertEqual(len(self.workspace.mets.agents), no_agents_before + 1, 'one more agent')
        #  print(self.workspace.mets.agents[no_agents_before])

    def test_run_input(self):
        run_processor(DummyProcessor, workspace=self.workspace, input_file_grp="OCR-D-IMG")
        assert len(self.workspace.mets.agents) > 0
        assert len(self.workspace.mets.agents[-1].notes) > 0
        assert ({'{https://ocr-d.de}option': 'input-file-grp'}, 'OCR-D-IMG') in self.workspace.mets.agents[-1].notes

    def test_run_output0(self):
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar1', pageId='phys_0001')
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar2', pageId='phys_0002')
            run_processor(DummyProcessorWithOutput, workspace=ws,
                          input_file_grp="GRP1",
                          output_file_grp="OCR-D-OUT")
            assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 2

    def test_run_output_overwrite(self):
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar1', pageId='phys_0001')
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar2', pageId='phys_0002')
            ws.overwrite_mode = True
            ws.add_file('OCR-D-OUT', mimetype=MIMETYPE_PAGE, ID='OCR-D-OUT_phys_0001', pageId='phys_0001')
            ws.overwrite_mode = False
            with pytest.raises(Exception) as exc:
                run_processor(DummyProcessorWithOutput, workspace=ws,
                              input_file_grp="GRP1",
                              output_file_grp="OCR-D-OUT")
                assert str(exc.value) == "File with ID='OCR-D-OUT_phys_0001' already exists"
            ws.overwrite_mode = True
            run_processor(DummyProcessorWithOutput, workspace=ws,
                          input_file_grp="GRP1",
                          output_file_grp="OCR-D-OUT")
            assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 2

    def test_run_cli(self):
        with TemporaryDirectory() as tempdir:
            run_processor(DummyProcessor, workspace=self.workspace,
                          input_file_grp='OCR-D-IMG',
                          output_file_grp='OUTPUT')
            run_cli(
                'echo',
                mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'),
                resolver=Resolver(),
                workspace=None,
                page_id='page1',
                log_level='DEBUG',
                input_file_grp='INPUT',
                output_file_grp='OUTPUT',
                parameter='/path/to/param.json',
                working_dir=tempdir
            )
            run_cli(
                'echo',
                mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'),
                resolver=Resolver(),
            )

    def test_zip_input_files(self):
        class ZipTestProcessor(Processor):
            @property
            def ocrd_tool(self):
                return {}
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar1', page_id='phys_0001')
            ws.add_file('GRP2', mimetype='application/alto+xml', file_id='foobar2', page_id='phys_0001')
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar3', page_id='phys_0002')
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='foobar4', page_id='phys_0002')
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(page_id=page_id):
                    proc = ZipTestProcessor(None)
                    proc.workspace = ws
                    proc.input_file_grp = 'GRP1,GRP2'
                    proc.page_id = page_id
                    tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files()]
                    assert ('foobar1', 'foobar2') in tuples
                    assert ('foobar3', 'foobar4') in tuples
                    tuples = [(one.ID, two) for one, two in proc.zip_input_files(mimetype=MIMETYPE_PAGE)]
                    assert ('foobar1', None) in tuples
                    tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files(mimetype=r'//application/(vnd.prima.page|alto)\+xml')]
                    assert ('foobar1', 'foobar2') in tuples
                    assert ('foobar3', 'foobar4') in tuples

    def test_zip_input_files_multi_mixed(self):
        class ZipTestProcessor(Processor):
            @property
            def ocrd_tool(self):
                return {}
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar1', page_id='phys_0001')
            ws.add_file('GRP1', mimetype='image/png', file_id='foobar1img1', page_id='phys_0001')
            ws.add_file('GRP1', mimetype='image/png', file_id='foobar1img2', page_id='phys_0001')
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='foobar2', page_id='phys_0001')
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar3', page_id='phys_0002')
            ws.add_file('GRP2', mimetype='image/tiff', file_id='foobar4', page_id='phys_0002')
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(page_id=page_id):
                    proc = ZipTestProcessor(None)
                    proc.workspace = ws
                    proc.input_file_grp = 'GRP1,GRP2'
                    proc.page_id = page_id
                    print("unfiltered")
                    tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files()]
                    assert ('foobar1', 'foobar2') in tuples
                    assert ('foobar3', 'foobar4') in tuples
                    print("PAGE-filtered")
                    tuples = [(one.ID, two) for one, two in proc.zip_input_files(mimetype=MIMETYPE_PAGE)]
                    assert ('foobar3', None) in tuples
            ws.add_file('GRP2', mimetype='image/tiff', file_id='foobar4dup', page_id='phys_0002')
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(page_id=page_id):
                    proc = ZipTestProcessor(None)
                    proc.workspace = ws
                    proc.input_file_grp = 'GRP1,GRP2'
                    proc.page_id = page_id
                    tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files(on_error='first')]
                    assert ('foobar1', 'foobar2') in tuples
                    assert ('foobar3', 'foobar4') in tuples
                    tuples = [(one.ID, two) for one, two in proc.zip_input_files(on_error='skip')]
                    assert ('foobar3', None) in tuples
                    with self.assertRaisesRegex(Exception, "No PAGE-XML for page .* in fileGrp .* but multiple matches."):
                        tuples = proc.zip_input_files(on_error='abort')
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='foobar2dup', page_id='phys_0001')
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(page_id=page_id):
                    proc = ZipTestProcessor(None)
                    proc.workspace = ws
                    proc.input_file_grp = 'GRP1,GRP2'
                    proc.page_id = page_id
                    with self.assertRaisesRegex(Exception, "Multiple PAGE-XML matches for page"):
                        tuples = proc.zip_input_files()

    def test_zip_input_files_require_first(self):
        class ZipTestProcessor(Processor):
            @property
            def ocrd_tool(self):
                return {}
        self.capture_out_err()
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar1', page_id=None)
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='foobar2', page_id='phys_0001')
            for page_id in [None, 'phys_0001']:
                with self.subTest(page_id=page_id):
                    proc = ZipTestProcessor(None)
                    proc.workspace = ws
                    proc.input_file_grp = 'GRP1,GRP2'
                    proc.page_id = page_id
                    assert [(one, two.ID) for one, two in proc.zip_input_files(require_first=False)] == [(None, 'foobar2')]
        r = self.capture_out_err()
        assert 'ERROR ocrd.processor.base - found no page phys_0001 in file group GRP1' in r.err

if __name__ == "__main__":
    main(__file__)
