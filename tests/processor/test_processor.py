import json

from tempfile import TemporaryDirectory
from os.path import join
from tests.base import TestCase, assets, main # pylint: disable=import-error, no-name-in-module

from ocrd.resolver import Resolver
from ocrd.processor.base import Processor, run_processor, run_cli

DUMMY_TOOL = {
    'executable': 'ocrd-test',
    'steps': ['recognition/post-correction'],
    'parameters': {
        'baz': {
            'type': 'string',
            'default': 'bla'
        }
    }
}

class DummyProcessor(Processor):

    def process(self):
        pass

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

class IncompleteProcessor(Processor):
    pass

class TestResolver(TestCase):

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
        self.assertEqual(len(processor.input_files), 35)

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
            self.assertEqual(len(processor.input_files), 35)

    def test_verify(self):
        proc = DummyProcessor(self.workspace)
        self.assertEqual(proc.verify(), True)

    def test_json(self):
        DummyProcessor(self.workspace, dump_json=True)

    def test_params_missing_required(self):
        class DummyProcessorWithRequiredParameters(Processor):
            def process(self): pass
            def __init__(self, *args, **kwargs):
                kwargs['version'] = '0.0.1'
                kwargs['ocrd_tool'] = {
                    'executable': 'ocrd-test',
                    'steps': ['recognition/post-correction'],
                    'parameters': {
                        'i-am-required': {'required': True}
                    }
                }
                super(DummyProcessorWithRequiredParameters, self).__init__(*args, **kwargs)
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

if __name__ == "__main__":
    main()
