import json
import os
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

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

    def process(self):
        print(json.dumps(self.parameter))

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

class DummyProcessorWithOutput(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super().__init__(*args, **kwargs)

    def process(self):
        # print([str(x) for x in self.input_files]
        for input_file in self.input_files:
            file_id = make_file_id(input_file, self.output_file_grp)
            # print(input_file.ID, file_id)
            self.workspace.add_file(
                ID=file_id,
                file_grp=self.output_file_grp,
                pageId=input_file.pageId,
                mimetype=input_file.mimetype,
                local_filename=os.path.join(self.output_file_grp, file_id),
                content='CONTENT')

class IncompleteProcessor(Processor):
    pass


