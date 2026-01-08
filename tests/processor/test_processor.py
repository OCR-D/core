from functools import cached_property
import json
from PIL import Image
from io import BytesIO
from contextlib import ExitStack
from concurrent.futures import TimeoutError

from tempfile import TemporaryDirectory
from pathlib import Path
from os import environ
from tests.base import CapturingTestCase as TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from tests.data import (
    DummyProcessor,
    DummyProcessorWithRequiredParameters,
    DummyProcessorWithOutput,
    DummyProcessorWithTwoOutputs,
    DummyProcessorWithOutputDocfile,
    DummyProcessorWithOutputLegacy,
    DummyProcessorWithOutputSleep,
    DummyProcessorWithOutputTF,
    DummyProcessorWithOutputFailures,
    DummyProcessorWithOutputMultiInput,
    IncompleteProcessor
)
from tests.test_mets_server import fixture_start_mets_server

from ocrd_utils import MIMETYPE_PAGE, pushd_popd, initLogging, disableLogging, config
from ocrd_modelfactory import page_from_file
from ocrd_models.ocrd_page import to_xml
from ocrd.resolver import Resolver
from ocrd.processor import Processor, run_processor, run_cli, NonUniqueInputFile
from ocrd.processor.base import IncompleteProcessorImplementation
from ocrd.processor.helpers import get_processor

from unittest import mock
import pytest

class TestProcessor(TestCase):

    def run(self, result=None):
        with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as workdir:
            with pushd_popd(workdir):
                self.resolver = Resolver()
                self.workspace = self.resolver.workspace_from_url('mets.xml')
                super().run(result=result)

    def setUp(self):
        super().setUp()
        initLogging()

    def tearDown(self):
        super().tearDown()
        config.reset_defaults()
        disableLogging()

    def test_incomplete_processor(self):
        proc = IncompleteProcessor(None)
        proc.input_file_grp = 'OCR-D-IMG'
        proc.output_file_grp = 'DUMMY'
        proc.page_id = None
        with self.assertRaises(IncompleteProcessorImplementation):
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
                parameter = json.load(f)
                processor = run_processor(
                    DummyProcessor,
                    parameter=parameter,
                    input_file_grp="OCR-D-IMG",
                    resolver=self.resolver,
                    workspace=self.workspace
                )
                self.assertEqual(processor.parameter['baz'], 'quux')
                processor = get_processor(
                    DummyProcessor,
                    parameter=parameter)
                with self.assertRaises(TypeError):
                    processor.parameter['baz'] = 'xuuq'
                processor.parameter = { **parameter, 'baz': 'xuuq' }
                self.assertEqual(processor.parameter['baz'], 'xuuq')

    def test_instance_caching(self):
        class DyingDummyProcessor(DummyProcessor):
            max_instances = 10
            def shutdown(self):
                # fixme: will only print _after_ pytest exits, so too late for assertions
                #print(self.parameter['baz'])
                pass
        self.capture_out_err()
        # customize (as processor implementors would)
        firstp = None
        for i in range(DyingDummyProcessor.max_instances + 2):
            p = get_processor(
                DyingDummyProcessor,
                parameter={'baz': str(i)},
                instance_caching=True
            )
            if i == 0:
                firstp = p
        lastp = p
        p = get_processor(DyingDummyProcessor,
                parameter={'baz': '0'},
                instance_caching=True
            )
        # should not be cached anymore
        self.assertNotEqual(firstp, p)
        p = get_processor(DyingDummyProcessor,
                parameter={'baz': str(i)},
                instance_caching=True
            )
        # should still be cached
        self.assertEqual(lastp, p)
        from ocrd.processor.helpers import get_cached_processor
        get_cached_processor.__wrapped__.cache_clear()
        p = get_processor(DyingDummyProcessor,
                parameter={'baz': str(i)},
                instance_caching=True
            )
        # should not be cached anymore
        self.assertNotEqual(lastp, p)
        # fixme: will only print _after_ pytest exits, so too late for assertions
        #out, err = self.capture_out_err()
        #assert '0' in out.split('\n')

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
        proc = DummyProcessorWithRequiredParameters(None)
        assert proc.parameter is None
        with self.assertRaisesRegex(ValueError, 'is a required property'):
            proc.parameter = {}
        with self.assertRaisesRegex(ValueError, 'is a required property'):
            get_processor(DummyProcessorWithRequiredParameters)
        with self.assertRaisesRegex(ValueError, 'is a required property'):
            get_processor(DummyProcessorWithRequiredParameters, parameter={})
        with self.assertRaisesRegex(ValueError, 'is a required property'):
            run_processor(DummyProcessorWithRequiredParameters,
                          workspace=self.workspace, input_file_grp="OCR-D-IMG")
        proc.parameter = {'i-am-required': 'foo'}
        proc.input_file_grp = "OCR-D-IMG"
        proc.output_file_grp = "OCR-D-OUT"
        proc.page_id = []
        proc.process_workspace(self.workspace)
        run_processor(DummyProcessorWithRequiredParameters,
                      workspace=self.workspace,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT",
                      parameter={'i-am-required': 'foo'})

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
            @cached_property
            def ocrd_tool(self):
                return {}
        proc = ParamTestProcessor(None)
        self.assertEqual(proc.parameter, None)
        # get_processor will set to non-none and validate
        proc = get_processor(ParamTestProcessor)
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
            file1 = ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar1', page_id='phys_0001',
                                url=assets.path_to('SBB0000F29300010000/data/OCR-D-GT-PAGE/FILE_0001_FULLTEXT.xml'))
            file2 = ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar2', page_id='phys_0002',
                                url=assets.path_to('SBB0000F29300010000/data/OCR-D-GT-PAGE/FILE_0002_FULLTEXT.xml'))
            run_processor(DummyProcessorWithOutput, workspace=ws,
                          input_file_grp="GRP1",
                          output_file_grp="OCR-D-OUT")
            assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 0, "no output because no download"
            ws.download_file(file1)
            ws.download_file(file2)
            run_processor(DummyProcessorWithOutput, workspace=ws,
                          input_file_grp="GRP1",
                          output_file_grp="OCR-D-OUT")
            assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 2

    def test_run_output_docfile(self):
        ws = self.workspace
        run_processor(DummyProcessorWithOutputDocfile, workspace=ws,
                      input_file_grp="OCR-D-GT-PAGE",
                      output_file_grp="OCR-D-OUT",
                      parameter={"file_id": "FULLDOWNLOAD"})
        assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 3
        docfile = next(ws.mets.find_files(fileGrp="OCR-D-OUT", mimetype="text/plain"), None)
        assert docfile is not None
        assert docfile.pageId is None

    def test_run_output_legacy(self):
        ws = self.workspace
        run_processor(DummyProcessorWithOutputLegacy,
                      workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT")
        assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))

    def test_run_output_missing(self):
        ws = self.workspace
        # do not raise for number of failures:
        config.OCRD_MAX_MISSING_OUTPUTS = -1
        config.OCRD_MISSING_OUTPUT = 'SKIP'
        run_processor(DummyProcessorWithOutputFailures, workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT")
        # only half succeed
        assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG")) // 2
        config.OCRD_MISSING_OUTPUT = 'ABORT'
        config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
        with pytest.raises(Exception) as exc:
            run_processor(DummyProcessorWithOutputFailures, workspace=ws,
                          input_file_grp="OCR-D-IMG",
                          output_file_grp="OCR-D-OUT")
        assert "intermittent" in str(exc.value)
        config.OCRD_MISSING_OUTPUT = 'COPY'
        config.OCRD_EXISTING_OUTPUT = 'SKIP'
        run_processor(DummyProcessorWithOutputFailures, workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT")
        assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
        # do raise for number of failures:
        config.OCRD_MAX_MISSING_OUTPUTS = 0.4
        config.OCRD_MISSING_OUTPUT = 'SKIP'
        with pytest.raises(Exception) as exc:
            run_processor(DummyProcessorWithOutputFailures, workspace=ws,
                          input_file_grp="OCR-D-IMG",
                          output_file_grp="OCR-D-OUT")
        assert "too many failures" in str(exc.value)

    def test_run_output_timeout(self):
        ws = self.workspace
        args = [DummyProcessorWithOutputSleep]
        kwargs = dict(workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT",
                      parameter={"sleep": 1})
        # do not raise for number of failures:
        config.OCRD_MAX_MISSING_OUTPUTS = -1
        config.OCRD_MISSING_OUTPUT = 'ABORT'
        config.OCRD_PROCESSING_PAGE_TIMEOUT = 3
        run_processor(*args, **kwargs)
        assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
        config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
        config.OCRD_PROCESSING_PAGE_TIMEOUT = 1
        with pytest.raises(TimeoutError) as exc:
            kwargs['parameter']['sleep'] = 3
            run_processor(*args, **kwargs)
        # cannot run processors multithreaded
        from pebble import ThreadPool
        with ThreadPool(1) as pool:
            task = pool.schedule(run_processor, args=args, kwargs=kwargs)
            with pytest.raises(ValueError) as exc:
                task.result()
            # interrupt n/a on other threads
            assert 'main thread' in str(exc.value)

    def test_run_output_overwrite(self):
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            file1 = ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar1', page_id='phys_0001',
                                url=assets.path_to('SBB0000F29300010000/data/OCR-D-GT-PAGE/FILE_0001_FULLTEXT.xml'))
            file2 = ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='foobar2', page_id='phys_0002',
                                url=assets.path_to('SBB0000F29300010000/data/OCR-D-GT-PAGE/FILE_0002_FULLTEXT.xml'))
            ws.download_file(file1)
            ws.download_file(file2)
            config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
            ws.add_file('OCR-D-OUT', mimetype=MIMETYPE_PAGE, file_id='OCR-D-OUT_phys_0001', page_id='phys_0001')
            config.OCRD_EXISTING_OUTPUT = 'ABORT'
            with pytest.raises(Exception) as exc:
                run_processor(DummyProcessorWithOutput, workspace=ws,
                              input_file_grp="GRP1",
                              output_file_grp="OCR-D-OUT")
            assert "already exists" in str(exc.value)
            config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
            run_processor(DummyProcessorWithOutput, workspace=ws,
                          input_file_grp="GRP1",
                          output_file_grp="OCR-D-OUT")
            assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 2

    def test_run_output_tensorflow(self):
        from pebble import ThreadPool
        ws = self.workspace
        args = [DummyProcessorWithOutputTF]
        kwargs = dict(workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT",
                      instance_caching=True)
        # do not raise for number of failures:
        config.OCRD_MAX_MISSING_OUTPUTS = -1
        config.OCRD_MISSING_OUTPUT = 'ABORT'
        #config.OCRD_PROCESSING_PAGE_TIMEOUT = 3
        proc1 = run_processor(*args, **kwargs)
        assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
        config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
        config.OCRD_PROCESSING_PAGE_TIMEOUT = 3
        proc2 = run_processor(*args, **kwargs)
        # instance caching works
        assert proc1 is proc2
        # cannot run processors multithreaded
        with ThreadPool(1) as pool:
            task = pool.schedule(run_processor, args=args, kwargs=kwargs)
            with pytest.raises(ValueError) as exc:
                task.result()
            # interrupt n/a on other threads
            assert 'main thread' in str(exc.value)
        # cannot run TF1 models multithreaded
        class ThreadedDummyProcessorWithOutputTF(DummyProcessorWithOutputTF):
            def process_page_pcgts(self, pcgts, page_id=None):
                with ThreadPool(1) as pool:
                    task = pool.schedule(super().process_page_pcgts, args=[pcgts], kwargs=dict(page_id=page_id))
                    return task.result()
        args = [ThreadedDummyProcessorWithOutputTF]
        with pytest.raises(ValueError) as exc:
            proc3 = run_processor(*args, **kwargs)
        # graph n/a on other threads
        assert 'is not an element of this graph' in str(exc.value)

    def test_run_multi_output(self):
        ws = self.workspace
        with pushd_popd(ws.directory):
            run_processor(DummyProcessorWithTwoOutputs, workspace=ws,
                          input_file_grp="OCR-D-IMG",
                          output_file_grp="OCR-D-OUT-L,OCR-D-OUT-R")
            output_files = ws.mets.find_all_files(fileGrp="OCR-D-OUT-L")
            assert len(output_files) == 3
            output_pcgts0 = page_from_file(output_files[0])
            assert output_pcgts0.pcGtsId == output_files[0].ID
            assert output_pcgts0.Page.get_custom() == "left side"
            output_files = ws.mets.find_all_files(fileGrp="OCR-D-OUT-R")
            assert len(output_files) == 3
            output_pcgts0 = page_from_file(output_files[0])
            assert output_pcgts0.pcGtsId == output_files[0].ID
            assert output_pcgts0.Page.get_custom() == "right side"
            config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
            run_processor(DummyProcessorWithTwoOutputs, workspace=ws,
                          input_file_grp="OCR-D-IMG",
                          output_file_grp="OCR-D-OUT-L,OCR-D-OUT-R")
            config.OCRD_EXISTING_OUTPUT = 'SKIP'
            run_processor(DummyProcessorWithTwoOutputs, workspace=ws,
                          input_file_grp="OCR-D-IMG",
                          output_file_grp="OCR-D-OUT-L,OCR-D-OUT-R")
            config.OCRD_EXISTING_OUTPUT = 'ABORT'
            with pytest.raises(AssertionError) as exc:
                run_processor(DummyProcessorWithTwoOutputs, workspace=ws,
                              input_file_grp="OCR-D-IMG",
                              output_file_grp="OCR-D-OUT-L,OCR-D-OUT-R")
            assert "output fileGrp OCR-D-OUT-L already exists" in str(exc.value)
            with pytest.raises(AssertionError) as exc:
                run_processor(DummyProcessorWithTwoOutputs, workspace=ws,
                              input_file_grp="OCR-D-IMG",
                              output_file_grp="OCR-D-OUT")
            assert "Unexpected number of output file groups" in str(exc.value)

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
            ws.add_file('GRP3', mimetype=MIMETYPE_PAGE, file_id='foobar5', page_id='phys_0003')
            for page_id in [None, 'phys_0001,phys_0002', '~phys_0003']:
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
                proc = ZipTestProcessor(None)
                proc.workspace = ws
                proc.input_file_grp = 'GRP1,GRP2'
                proc.page_id = page_id
                with self.subTest(msg='mixed MIME unfiltered', page_id=page_id):
                    tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files()]
                    assert ('foobar1', 'foobar2') in tuples
                    assert ('foobar3', 'foobar4') in tuples
                with self.subTest(msg='mixed MIME PAGE-filtered', page_id=page_id):
                    tuples = [(one.ID, two) for one, two in proc.zip_input_files(mimetype=MIMETYPE_PAGE)]
                    assert ('foobar3', None) in tuples
            # add clashing image that is not mitigated by the presence of a PAGE file
            ws.add_file('GRP2', mimetype='image/tiff', file_id='foobar4dup', page_id='phys_0002')
            for page_id in [None, 'phys_0001,phys_0002']:
                proc = ZipTestProcessor(None)
                proc.workspace = ws
                proc.input_file_grp = 'GRP1,GRP2'
                proc.page_id = page_id
                with self.subTest(msg='image file clash', page_id=page_id):
                    tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files(on_error='first')]
                    assert ('foobar1', 'foobar2') in tuples
                    assert ('foobar3', 'foobar4') in tuples
                    tuples = [(one.ID, two) for one, two in proc.zip_input_files(on_error='skip')]
                    assert ('foobar3', None) in tuples
                    tuples = [(one.ID, two) for one, two in proc.zip_input_files(on_error='skip', mimetype=MIMETYPE_PAGE)]
                    assert ('foobar3', None) in tuples
                    with self.assertRaisesRegex(NonUniqueInputFile, "Could not determine unique input file"):
                        tuples = proc.zip_input_files(on_error='abort')
            # add clashing PAGE
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='foobar2dup', page_id='phys_0001')
            for page_id in [None, 'phys_0001,phys_0002']:
                proc = ZipTestProcessor(None)
                proc.workspace = ws
                proc.input_file_grp = 'GRP1,GRP2'
                proc.page_id = page_id
                with self.subTest(msg='PAGE file clash', page_id=page_id):
                    with self.assertRaisesRegex(NonUniqueInputFile, "Could not determine unique input file"):
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
            ws.add_file('GRP3', mimetype=MIMETYPE_PAGE, file_id='foobar3', page_id='phys_0002')
            for page_id in [None, 'phys_0001', '~phys_0002']:
                with self.subTest(page_id=page_id):
                    proc = ZipTestProcessor(None)
                    proc.workspace = ws
                    proc.input_file_grp = 'GRP1,GRP2'
                    proc.page_id = page_id
                    assert [(one, two.ID) for one, two in proc.zip_input_files(require_first=False)] == [(None, 'foobar2')]
        r = self.capture_out_err()
        assert 'ERROR ocrd.processor.base - Found no file for page phys_0001 in file group GRP1' in r.err

    def test_run_output_multi_input(self):
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            pil_image = Image.new('RGB', (100, 100))
            png_bytes = BytesIO()
            pil_image.save(png_bytes, format='PNG')
            tif_bytes = BytesIO()
            pil_image.save(tif_bytes, format='TIFF')
            file1 = ws.add_file('GRP1', mimetype='image/png', file_id='GRP1_foobar1img2', page_id='phys_0001',
                                local_filename='GRP1/foobar1img2.png', content=png_bytes.getvalue())
            file1 = ws.add_file('GRP1', mimetype='image/png', file_id='GRP1_foobar1img1', page_id='phys_0001',
                                local_filename='GRP1/foobar1img1.png', content=png_bytes.getvalue())
            file1 = ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='GRP1_foobar1', page_id='phys_0001',
                                local_filename='GRP1/foobar1.xml', content=to_xml(page_from_file(file1)))
            file1 = ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='GRP2_foobar2', page_id='phys_0001',
                                local_filename='GRP1/foobar1.xml')
            file2 = ws.add_file('GRP2', mimetype='image/tiff', file_id='GRP2_foobar4', page_id='phys_0002',
                                local_filename='GRP2/foobar4.tif', content=tif_bytes.getvalue())
            file2 = ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, file_id='GRP1_foobar3', page_id='phys_0002',
                                local_filename='GRP1/foobar3.xml', content=to_xml(page_from_file(file2)))
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(msg='mixed MIME unfiltered', page_id=page_id):
                    proc = run_processor(DummyProcessorWithOutputMultiInput, workspace=ws,
                                         input_file_grp="GRP1,GRP2",
                                         output_file_grp="OCR-D-OUT",
                                         parameter=dict())
                    input_files = proc.tuples
                    assert len(input_files) == 2
                    assert [tuple(input_file.ID.split('_')[1] if input_file else None
                                  for input_file in ift)
                            for ift in input_files] == [('foobar1', 'foobar2'), ('foobar3', 'foobar4')]
                    output_files = ws.mets.find_all_files(fileGrp="OCR-D-OUT")
                    assert len(output_files) == 2
                    assert page_from_file(output_files[0]).pcGtsId == output_files[0].ID
                    assert output_files[0].ID == 'OCR-D-OUT_foobar1'
                    assert output_files[1].ID == 'OCR-D-OUT_foobar3'
                    for output_file in output_files:
                        assert ws.remove_file(output_file.ID).ID == output_file.ID
                with self.subTest(msg='mixed MIME PAGE-filtered', page_id=page_id):
                    proc = run_processor(DummyProcessorWithOutputMultiInput, workspace=ws,
                                         input_file_grp="GRP1,GRP2",
                                         output_file_grp="OCR-D-OUT",
                                         parameter=dict(mimetype=MIMETYPE_PAGE))
                    input_files = proc.tuples
                    assert len(input_files) == 2
                    assert [tuple(input_file.ID.split('_')[1] if input_file else None
                                  for input_file in ift)
                            for ift in input_files] == [('foobar1', 'foobar2'), ('foobar3', None)]
                    output_files = ws.mets.find_all_files(fileGrp="OCR-D-OUT")
                    assert len(output_files) == 2
                    assert page_from_file(output_files[0]).pcGtsId == output_files[0].ID
                    assert output_files[0].ID == 'OCR-D-OUT_foobar1'
                    assert output_files[1].ID == 'OCR-D-OUT_foobar3'
                    for output_file in output_files:
                        assert ws.remove_file(output_file.ID).ID == output_file.ID
                with self.subTest(msg='mixed MIME PAGE-filtered non-first', page_id=page_id):
                    proc = run_processor(DummyProcessorWithOutputMultiInput, workspace=ws,
                                         input_file_grp="GRP2,GRP1",
                                         output_file_grp="OCR-D-OUT",
                                         parameter=dict(mimetype=MIMETYPE_PAGE, require_first=False))
                    input_files = proc.tuples
                    assert len(input_files) == 2
                    assert [tuple(input_file.ID.split('_')[1] if input_file else None
                                  for input_file in ift)
                            for ift in input_files] == [('foobar2', 'foobar1'), (None, 'foobar3')]
                    output_files = ws.mets.find_all_files(fileGrp="OCR-D-OUT")
                    assert len(output_files) == 2
                    assert page_from_file(output_files[0]).pcGtsId == output_files[0].ID
                    assert output_files[0].ID == 'OCR-D-OUT_foobar2'
                    assert output_files[1].ID == 'OCR-D-OUT_foobar3'
                    for output_file in output_files:
                        assert ws.remove_file(output_file.ID).ID == output_file.ID
            # add clashing image that is not mitigated by the presence of a PAGE file
            file2 = ws.add_file('GRP2', mimetype='image/tiff', file_id='GRP2_foobar4dup', page_id='phys_0002',
                                local_filename='GRP2/foobar4.tif')
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(msg='image file clash', page_id=page_id):
                    proc = run_processor(DummyProcessorWithOutputMultiInput, workspace=ws,
                                         input_file_grp="GRP1,GRP2",
                                         output_file_grp="OCR-D-OUT",
                                         parameter=dict(on_error='last'))
                    input_files = proc.tuples
                    assert len(input_files) == 2
                    assert [tuple(input_file.ID.split('_')[1] if input_file else None
                                  for input_file in ift)
                            for ift in input_files] == [('foobar1', 'foobar2'), ('foobar3', 'foobar4dup')]
                    output_files = ws.mets.find_all_files(fileGrp="OCR-D-OUT")
                    assert len(output_files) == 2
                    assert page_from_file(output_files[0]).pcGtsId == output_files[0].ID
                    assert output_files[0].ID == 'OCR-D-OUT_foobar1'
                    assert output_files[1].ID == 'OCR-D-OUT_foobar3'
                    for output_file in output_files:
                        assert ws.remove_file(output_file.ID).ID == output_file.ID
                    with pytest.raises(NonUniqueInputFile) as exc:
                        run_processor(DummyProcessorWithOutputMultiInput, workspace=ws,
                                      input_file_grp="GRP1,GRP2",
                                      output_file_grp="OCR-D-OUT",
                                      parameter=dict(on_error='abort'))
                    assert "Could not determine unique input file" in str(exc.value)
            # add clashing PAGE
            file1 = ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, file_id='GRP2_foobar2dup', page_id='phys_0001',
                                local_filename='GRP1/foobar1.xml')
            for page_id in [None, 'phys_0001,phys_0002']:
                with self.subTest(msg='PAGE file clash', page_id=page_id):
                    with pytest.raises(NonUniqueInputFile) as exc:
                        run_processor(DummyProcessorWithOutputMultiInput, workspace=ws,
                                      input_file_grp="GRP1,GRP2",
                                      output_file_grp="OCR-D-OUT",
                                      parameter=dict())
                    assert "Could not determine unique input file" in str(exc.value)

@pytest.fixture
def workspace_sbb():
    initLogging()
    with copy_of_directory(assets.path_to('SBB0000F29300010000/data')) as workdir:
        with pushd_popd(workdir):
            resolver = Resolver()
            workspace = resolver.workspace_from_url('mets.xml')
            yield workspace
    disableLogging()

@pytest.fixture
def workspace_kant():
    initLogging()
    with copy_of_directory(assets.path_to('kant_aufklaerung_1784/data')) as workdir:
        with pushd_popd(workdir):
            resolver = Resolver()
            workspace = resolver.workspace_from_url('mets.xml')
            yield workspace
    disableLogging()

def test_run_output_logging(workspace_sbb, caplog):
    caplog.set_level(10)
    def only_profile(logrec):
        return logrec.name == 'ocrd.process.profile'
    with caplog.filtering(only_profile):
        proc = run_processor(DummyProcessorWithRequiredParameters,
                      workspace=workspace_sbb,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT",
                      parameter={'i-am-required': 'foo'})
    assert len(caplog.records) == 1
    #assert isinstance(proc.parameter, dict)
    msg = caplog.records[0].message
    assert msg.startswith("Executing processor 'ocrd-test' took")

def test_run_output_metsserver(start_mets_server):
    mets_server_url, ws = start_mets_server
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 0
    # do not raise for number of failures:
    config.OCRD_MAX_MISSING_OUTPUTS = -1
    run_processor(DummyProcessorWithOutputSleep, workspace=ws,
                  input_file_grp="OCR-D-IMG",
                  output_file_grp="OCR-D-OUT",
                  parameter={"sleep": 0},
                  mets_server_url=mets_server_url)
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
    config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
    run_processor(DummyProcessorWithOutputSleep, workspace=ws,
                  input_file_grp="OCR-D-IMG",
                  output_file_grp="OCR-D-OUT",
                  parameter={"sleep": 0},
                  mets_server_url=mets_server_url)
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
    config.OCRD_EXISTING_OUTPUT = 'ABORT'
    with pytest.raises(Exception) as exc:
        run_processor(DummyProcessorWithOutputSleep, workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT",
                      parameter={"sleep": 0},
                      mets_server_url=mets_server_url)
    assert "already exists" in str(exc.value)
    run_processor(DummyProcessorWithOutputDocfile, workspace=ws,
                  input_file_grp="OCR-D-GT-PAGE",
                  output_file_grp="OCR-D-OUT2",
                  parameter={"file_id": "FULLDOWNLOAD"})
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT2")) == 3
    docfile = next(ws.mets.find_files(fileGrp="OCR-D-OUT2", mimetype="text/plain"), None)
    assert docfile is not None
    assert docfile.pageId is None
    config.reset_defaults()

def test_run_output_metsserver_timeout(start_mets_server):
    mets_server_url, ws = start_mets_server
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 0
    # do not raise for number of failures:
    config.OCRD_MAX_MISSING_OUTPUTS = -1
    config.OCRD_MISSING_OUTPUT = 'ABORT'
    config.OCRD_PROCESSING_PAGE_TIMEOUT = 3
    run_processor(DummyProcessorWithOutputSleep, workspace=ws,
                  input_file_grp="OCR-D-IMG",
                  output_file_grp="OCR-D-OUT",
                  parameter={"sleep": 1})
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
    config.OCRD_EXISTING_OUTPUT = 'OVERWRITE'
    config.OCRD_PROCESSING_PAGE_TIMEOUT = 1
    with pytest.raises(TimeoutError) as exc:
        run_processor(DummyProcessorWithOutputSleep, workspace=ws,
                      input_file_grp="OCR-D-IMG",
                      output_file_grp="OCR-D-OUT",
                      parameter={"sleep": 3})

# 2s (+ 2s tolerance) instead of 3*3s (+ 2s tolerance)
# fixme: pytest-timeout does not shut down / finalize the fixture properly
#        (regardless of method or func_only), so the next test in the suite
#        does not execute ("previous item was not torn down properly")
#        so we must instead wait for completion and assert on the time spent...
#@pytest.mark.timeout(timeout=4, func_only=True, method="signal")
def test_run_output_parallel(start_mets_server):
    import time
    mets_server_url, ws = start_mets_server
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 0
    # do not raise for single-page timeout
    config.OCRD_PROCESSING_PAGE_TIMEOUT = -1
    # do not raise for number of failures:
    config.OCRD_MAX_MISSING_OUTPUTS = -1
    config.OCRD_MAX_PARALLEL_PAGES = 3
    start_time = time.time()
    run_processor(DummyProcessorWithOutputSleep, workspace=ws,
                  input_file_grp="OCR-D-IMG",
                  output_file_grp="OCR-D-OUT",
                  parameter={"sleep": 2},
                  mets_server_url=mets_server_url)
    run_time = time.time() - start_time
    assert run_time < 3.5, f"run_processor took {run_time}s"
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
    config.reset_defaults()

def test_run_output_parallel_caching(start_mets_server):
    import time
    mets_server_url, ws = start_mets_server
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == 0
    # do not raise for single-page timeout
    config.OCRD_PROCESSING_PAGE_TIMEOUT = -1
    # do not raise for number of failures:
    config.OCRD_MAX_MISSING_OUTPUTS = -1
    config.OCRD_MAX_PARALLEL_PAGES = 3
    kwargs = dict(workspace=ws,
                  input_file_grp="OCR-D-IMG",
                  output_file_grp="OCR-D-OUT",
                  parameter={"sleep": 2},
                  mets_server_url=mets_server_url,
                  instance_caching=True)
    start_time = time.time()
    proc1 = run_processor(DummyProcessorWithOutputSleep, **kwargs)
    run_time = time.time() - start_time
    assert run_time < 3.5, f"run_processor took {run_time}s"
    assert len(ws.mets.find_all_files(fileGrp="OCR-D-OUT")) == len(ws.mets.find_all_files(fileGrp="OCR-D-IMG"))
    start_time = time.time()
    proc2 = run_processor(DummyProcessorWithOutputSleep, **kwargs)
    assert proc1 is proc2, "instance_caching must yield identical processor objects for equal parameters"
    run_time = time.time() - start_time
    # should be faster with default config.OCRD_EXISTING_OUTPUT==SKIP
    assert run_time < 1.5, f"run_processor took {run_time}s"
    config.reset_defaults()

if __name__ == "__main__":
    main(__file__)
