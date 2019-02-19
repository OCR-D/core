from tests.base import TestCase, assets, main # pylint: disable=import-error, no-name-in-module
from tempfile import TemporaryDirectory
from os.path import join

from ocrd.resolver import Resolver
from ocrd.processor.base import Processor, run_processor

DUMMY_TOOL = {'executable': 'ocrd-test', 'steps': ['recognition/post-correction']}

class DummyProcessor(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

    def process(self):
        #  print('# nope')
        pass

class TestResolver(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))

    def test_no_resolver(self):
        with self.assertRaisesRegex(Exception, 'pass a resolver to create a workspace'):
            run_processor(DummyProcessor)

    def test_no_mets_url(self):
        with self.assertRaisesRegex(Exception, 'pass mets_url to create a workspace'):
            run_processor(DummyProcessor, resolver=self.resolver)

    def test_with_mets_url_input_files(self):
        processor = run_processor(DummyProcessor, resolver=self.resolver, mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'))
        self.assertEqual(len(processor.input_files), 35)

    def test_parameter(self):
        with TemporaryDirectory() as tempdir:
            jsonpath = join(tempdir, 'params.json')
            with open(jsonpath, 'w') as f:
                f.write('{}')
            processor = run_processor(
                DummyProcessor,
                parameter=jsonpath,
                resolver=self.resolver,
                mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml')
            )
            self.assertEqual(len(processor.input_files), 35)

    def test_parameter_url(self):
        with TemporaryDirectory() as tempdir:
            jsonpath = join(tempdir, 'params.json')
            with open(jsonpath, 'w') as f:
                f.write('{}')
            processor = run_processor(
                DummyProcessor,
                parameter='file://%s' % jsonpath,
                resolver=self.resolver,
                mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml')
            )
            self.assertEqual(len(processor.input_files), 35)

    def test_verify(self):
        proc = DummyProcessor(self.workspace)
        self.assertEqual(proc.verify(), True)

    def test_json(self):
        DummyProcessor(self.workspace, dump_json=True)

    def test_params(self):
        proc = Processor(workspace=self.workspace)
        self.assertEqual(proc.parameter, {})

    def test_run_agent(self):
        no_agents_before = len(self.workspace.mets.agents)
        run_processor(DummyProcessor, ocrd_tool=DUMMY_TOOL, workspace=self.workspace)
        self.assertEqual(len(self.workspace.mets.agents), no_agents_before + 1, 'one more agent')
        #  print(self.workspace.mets.agents[no_agents_before])

if __name__ == "__main__":
    main()
