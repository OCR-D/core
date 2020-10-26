import json

from tempfile import TemporaryDirectory
from os.path import join
from tests.base import CapturingTestCase as TestCase, assets, main # pylint: disable=import-error, no-name-in-module
from tests.data import DummyProcessor, DummyProcessorWithRequiredParameters, IncompleteProcessor, DUMMY_TOOL

from ocrd_utils import MIMETYPE_PAGE, pushd_popd, initLogging
from ocrd.resolver import Resolver
from ocrd.processor.base import Processor, run_processor, run_cli

class TestProcessor(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))

    def test_incomplete_processor(self):
        proc = IncompleteProcessor(None)
        with self.assertRaisesRegex(Exception, 'Must be implemented'):
            proc.process()

    def test_no_resolver(self):
        with self.assertRaisesRegex(Exception, 'pass a resolver to create a workspace'):
            run_processor(DummyProcessor)

    def test_no_mets_url(self):
        with self.assertRaisesRegex(Exception, 'pass mets_url to create a workspace'):
            run_processor(DummyProcessor, resolver=self.resolver)

    def test_with_mets_url_input_files(self):
        processor = run_processor(DummyProcessor, resolver=self.resolver, mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'))
        self.assertEqual(len(processor.input_files), 20)
        self.assertTrue(all([f.mimetype == MIMETYPE_PAGE for f in processor.input_files]))

    def test_parameter(self):
        with TemporaryDirectory() as tempdir:
            jsonpath = join(tempdir, 'params.json')
            with open(jsonpath, 'w') as f:
                f.write('{"baz": "quux"}')
            with open(jsonpath, 'r') as f:
                processor = run_processor(
                    DummyProcessor,
                    parameter=json.load(f),
                    resolver=self.resolver,
                    mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml')
                )
            self.assertEqual(len(processor.input_files), 20)

    def test_verify(self):
        proc = DummyProcessor(self.workspace)
        self.assertEqual(proc.verify(), True)

    def test_json(self):
        DummyProcessor(self.workspace, dump_json=True)

    def test_params_missing_required(self):
        with self.assertRaisesRegex(Exception, 'is a required property'):
            DummyProcessorWithRequiredParameters(workspace=self.workspace)

    def test_params(self):
        proc = Processor(workspace=self.workspace)
        self.assertEqual(proc.parameter, {})

    def test_run_agent(self):
        no_agents_before = len(self.workspace.mets.agents)
        run_processor(DummyProcessor, ocrd_tool=DUMMY_TOOL, workspace=self.workspace)
        self.assertEqual(len(self.workspace.mets.agents), no_agents_before + 1, 'one more agent')
        #  print(self.workspace.mets.agents[no_agents_before])

    def test_run_cli(self):
        with TemporaryDirectory() as tempdir:
            run_processor(DummyProcessor, ocrd_tool=DUMMY_TOOL, workspace=self.workspace)
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
        class ZipTestProcessor(Processor): pass
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar1', pageId='phys_0001')
            ws.add_file('GRP2', mimetype='application/alto+xml', ID='foobar2', pageId='phys_0001')
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar3', pageId='phys_0002')
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, ID='foobar4', pageId='phys_0002')
            proc = ZipTestProcessor(workspace=ws, input_file_grp='GRP1,GRP2')
            tuples = [(one.ID, two.ID) for one, two in proc.zip_input_files(mimetype=r'//application/(vnd.prima.page|alto)\+xml')]
            assert ('foobar1', 'foobar2') in tuples
            assert ('foobar3', 'foobar4') in tuples

    def test_zip_input_files_require_first(self):
        initLogging()
        class ZipTestProcessor(Processor): pass
        self.capture_out_err()
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.add_file('GRP1', mimetype=MIMETYPE_PAGE, ID='foobar1', pageId=None)
            ws.add_file('GRP2', mimetype=MIMETYPE_PAGE, ID='foobar2', pageId='phys_0001')
            proc = ZipTestProcessor(workspace=ws, input_file_grp='GRP1,GRP2')
            assert [(one, two.ID) for one, two in proc.zip_input_files(require_first=False)] == [(None, 'foobar2')]
        r = self.capture_out_err()
        assert 'ERROR ocrd.processor.base - found no page phys_0001 in file group GRP1' in r.err


if __name__ == "__main__":
    main(__file__)
