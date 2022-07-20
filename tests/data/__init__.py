import json
from ocrd import Processor

DUMMY_TOOL = {
    'executable': 'ocrd-test',
    'description': 'dolor sit',
    'steps': ['recognition/post-correction'],
    'categories': ['Image preprocessing'],
    'input_file_grp': ['DUMMY_INPUT'],
    'output_file_grp': ['DUMMY_OUTPUT'],
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
    def process(self):
        pass

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


class IncompleteProcessor(Processor):
    pass
