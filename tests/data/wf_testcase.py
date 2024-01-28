import json
import os
from os.path import join
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from tests.base import CapturingTestCase as BaseTestCase

SAMPLE_NAME = 'ocrd-sample-processor'
SAMPLE_OCRD_TOOL_JSON = '''{
    "executable": "ocrd-sample-processor",
    "description": "Do stuff and things",
    "categories": ["Image foobaring"],
    "steps": ["preprocessing/optimization/foobarization"],
    "input_file_grp": ["OCR-D-IMG"],
    "output_file_grp": ["OCR-D-IMG-BIN", "SECOND_OUT"],
    "parameters": {
        "param1": {
            "type": "boolean",
            "default": false,
            "description": "param1 description"
        }
    }
}'''

SAMPLE_NAME_REQUIRED_PARAM = 'sample-processor-required-param'
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM = json.loads(SAMPLE_OCRD_TOOL_JSON)
del SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM['parameters']['param1']['default']
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM['executable'] = 'ocrd-' + SAMPLE_NAME_REQUIRED_PARAM
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM['parameters']['param1']['required'] = True
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM['input_file_grp'] += ['SECOND_IN']
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM = json.dumps(SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM)

PARAM_JSON = '{"foo": 42}'

class TestCase(BaseTestCase):

    def tearDown(self):
        rmtree(self.tempdir)

    def setUp(self):
        super().setUp()
        self.tempdir = mkdtemp(prefix='ocrd-task-sequence-')
        self.param_fname = join(self.tempdir, 'params.json')
        with open(self.param_fname, 'w') as f:
            f.write(PARAM_JSON)

        p = Path(self.tempdir, SAMPLE_NAME)
        p.write_text("""\
#!/usr/bin/env python
print('''%s''')
        """ % SAMPLE_OCRD_TOOL_JSON)
        p.chmod(0o777)

        p = Path(self.tempdir, 'ocrd-' + SAMPLE_NAME_REQUIRED_PARAM)
        p.write_text("""\
#!/usr/bin/env python
print('''%s''')
        """ % SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM)
        p.chmod(0o777)

        os.environ['PATH'] = os.pathsep.join([self.tempdir, os.environ['PATH']])
        #  from distutils.spawn import find_executable as which # pylint: disable=import-error,no-name-in-module
        #  self.assertTrue(which('ocrd-sample-processor'))


