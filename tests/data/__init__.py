import json
import os
from pytest import warns
from ocrd import Processor
from ocrd_utils import make_file_id

DUMMY_TOOL = {
    'executable': 'ocrd-test',
    'description': 'dolor sit',
    'steps': ['recognition/post-correction'],
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
        kwargs['download_files'] = False
        super().__init__(*args, **kwargs)

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
        kwargs['download_files'] = False
        super().__init__(*args, **kwargs)

    def process(self): pass

class DummyProcessorWithOutput(Processor):
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
        kwargs['download_files'] = False
        super().__init__(*args, **kwargs)

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
                content='CONTENT')

class IncompleteProcessor(Processor):
    @property
    def ocrd_tool(self):
        return {}


