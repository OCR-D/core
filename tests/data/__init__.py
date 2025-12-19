from functools import cached_property
import json
import os
from copy import deepcopy
from time import sleep
from pytest import warns
from ocrd import Processor, OcrdPageResult
from ocrd_utils import make_file_id, config

DUMMY_TOOL = {
    'executable': 'ocrd-test',
    'description': 'dolor sit',
    'steps': ['recognition/post-correction'],
    # as we bypass Processor.metadata with OcrdToolValidator
    # we get no default expansion, so add default cardinalities here
    'input_file_grp_cardinality': 1,
    'output_file_grp_cardinality': 1,
    'parameters': {
        'baz': {
            'type': 'string',
            'default': 'bla',
            'description': 'lorem ipsum'
        }
    }
}

class DummyProcessor(Processor):
    @property
    def ocrd_tool(self):
        return DUMMY_TOOL

    @property
    def version(self):
        return '0.0.1'

    @property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def process(self):
        print(json.dumps(self.parameter))

    # override to prevent iterating over empty files
    def process_workspace(self, workspace):
        with warns(DeprecationWarning, match='should be replaced with process_page'):
            self.process()

class DummyProcessorWithRequiredParameters(Processor):
    @property
    def ocrd_tool(self):
        return {
            'executable': 'ocrd-test',
            'steps': ['recognition/post-correction'],
            'parameters': {
                'i-am-required': {'required': True}
            }
        }
    @property
    def version(self):
        return '0.0.1'

    @property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def process(self): pass

class DummyProcessorWithOutput(Processor):
    @cached_property
    def ocrd_tool(self):
        return DUMMY_TOOL

    @cached_property
    def version(self):
        return '0.0.1'

    @cached_property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def process(self):
        # print([str(x) for x in self.input_files]
        for input_file in self.input_files:
            file_id = make_file_id(input_file, self.output_file_grp)
            # print(input_file.ID, file_id)
            self.workspace.add_file(
                file_id=file_id,
                file_grp=self.output_file_grp,
                page_id=input_file.pageId,
                mimetype=input_file.mimetype,
                local_filename=os.path.join(self.output_file_grp, file_id),
                content='CONTENT',
            )

class DummyProcessorWithTwoOutputs(Processor):
    @property
    def ocrd_tool(self):
        # make deep copy
        dummy_tool = json.loads(json.dumps(DUMMY_TOOL))
        dummy_tool['output_file_grp_cardinality'] = 2
        return dummy_tool

    @property
    def version(self):
        return '0.0.1'

    @property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def process_page_pcgts(self, pcgts, page_id=None):
        left, right = pcgts, deepcopy(pcgts)
        left.Page.set_custom("left side")
        right.Page.set_custom("right side")
        return OcrdPageResult(left, right)

class DummyProcessorWithOutputDocfile(Processor):
    @property
    def ocrd_tool(self):
        # make deep copy
        dummy_tool = json.loads(json.dumps(DUMMY_TOOL))
        dummy_tool['parameters']['file_id'] = {'type': 'string'}
        return dummy_tool

    @property
    def version(self):
        return '0.0.1'

    @property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def process_page_pcgts(self, pcgts, page_id=None):
        # copycat
        return OcrdPageResult(pcgts)

    def process_workspace(self, workspace):
        super().process_workspace(workspace)
        if self.parameter['file_id']:
            workspace.add_file(
                file_id=self.parameter['file_id'],
                file_grp=self.output_file_grp,
                local_filename=os.path.join(self.output_file_grp, self.parameter['file_id'] + '.txt'),
                mimetype="text/plain",
                page_id=None,
                content="CONTENT",
            )

class DummyProcessorWithOutputSleep(Processor):
    @property
    def ocrd_tool(self):
        # make deep copy
        dummy_tool = json.loads(json.dumps(DUMMY_TOOL))
        dummy_tool['parameters']['sleep'] = {'type': 'number'}
        return dummy_tool

    @property
    def version(self):
        return '0.0.1'

    @property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def process_page_pcgts(self, pcgts, page_id=None):
        sleep(self.parameter['sleep'])
        return OcrdPageResult(pcgts)

class DummyProcessorWithOutputFailures(Processor):
    @cached_property
    def ocrd_tool(self):
        return DUMMY_TOOL

    @cached_property
    def version(self):
        return '0.0.1'

    @cached_property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    # no error handling with old process(), so override new API
    def process_page_file(self, input_file):
        n = self.workspace.mets.physical_pages.index(input_file.pageId) + 1
        if n % 2:
            raise Exception(f"intermittent failure on page {input_file.pageId}")
        output_file_id = make_file_id(input_file, self.output_file_grp)
        self.workspace.add_file(file_id=output_file_id,
                                file_grp=self.output_file_grp,
                                page_id=input_file.pageId,
                                local_filename=os.path.join(self.output_file_grp, output_file_id),
                                mimetype=input_file.mimetype,
                                content='CONTENT',
        )

class DummyProcessorWithOutputLegacy(Processor):
    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super().__init__(*args, **kwargs)
        self.download = False
        if hasattr(self, 'output_file_grp'):
            self.setup()

    def process(self):
        # print([str(x) for x in self.input_files]
        for input_file in self.input_files:
            file_id = make_file_id(input_file, self.output_file_grp)
            # print(input_file.ID, file_id)
            self.workspace.add_file(
                file_id=file_id,
                file_grp=self.output_file_grp,
                page_id=input_file.pageId,
                mimetype=input_file.mimetype,
                local_filename=os.path.join(self.output_file_grp, file_id),
                content='CONTENT',
            )

class DummyProcessorWithOutputMultiInput(Processor):
    @property
    def ocrd_tool(self):
        # make deep copy
        dummy_tool = json.loads(json.dumps(DUMMY_TOOL))
        dummy_tool['input_file_grp_cardinality'] = [2, -1]
        # delegate zip_input_files kwargs
        dummy_tool['parameters'] = {
            'require_first': {
                'type': 'boolean',
                'default': True,
            },
            'on_error': {
                'type': 'string',
                'enum': ['skip', 'first', 'last', 'abort'],
                'default': 'skip',
            },
            'mimetype': {
                'type': 'string'
            }
        }
        return dummy_tool

    @property
    def version(self):
        return '0.0.1'

    @property
    def executable(self):
        return 'ocrd-test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download = False

    def zip_input_files(self, **kwargs):
        for name, value in self.parameter.items():
            kwargs[name] = value
        self.tuples = super().zip_input_files(**kwargs)
        return self.tuples

    def process_page_pcgts(self, *input_pcgts, page_id=None):
        pcgts = next(filter(None, input_pcgts))
        return OcrdPageResult(pcgts)

class IncompleteProcessor(Processor):
    @property
    def executable(self):
        return 'ocrd-foo'

    @property
    def metadata_rawdict(self):
        return {'tools': {self.executable: {}}}


