import os
import json
from tempfile import mkdtemp, TemporaryDirectory
from shutil import rmtree

from pathlib import Path

from tests.base import TestCase, main, assets

from ocrd.resolver import Resolver
from ocrd.task_sequence import ProcessorTask, validate_tasks

SAMPLE_NAME = 'ocrd-sample-processor'
SAMPLE_OCRD_TOOL_JSON = '''{
    "executable": "ocrd-sample-processor",
    "description": "Do stuff and things",
    "categories": ["Image foobaring"],
    "steps": ["preprocessing/optimization/foobarization"],
    "input_file_grp": ["OCR-D-IMG"],
    "output_file_grp": ["OCR-D-IMG-BIN"],
    "parameters": {
        "param1": {
            "type": "boolean",
            "default": false,
            "description": "param1 description"
        }
    }
}'''
SAMPLE_NAME_WITHOUT_OUTPUT_FILE_GRP = 'ocrd-sample-processor-without-file-grp'
SAMPLE_OCRD_TOOL_JSON_WITHOUT_OUTPUT_FILE_GRP = json.loads(SAMPLE_OCRD_TOOL_JSON)
del SAMPLE_OCRD_TOOL_JSON_WITHOUT_OUTPUT_FILE_GRP['output_file_grp']
SAMPLE_OCRD_TOOL_JSON_WITHOUT_OUTPUT_FILE_GRP = json.dumps(SAMPLE_OCRD_TOOL_JSON_WITHOUT_OUTPUT_FILE_GRP)

SAMPLE_NAME_REQUIRED_PARAM = 'ocrd-sample-processor-required-param'
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM = json.loads(SAMPLE_OCRD_TOOL_JSON)
del SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM['parameters']['param1']['default']
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM['parameters']['param1']['required'] = True
SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM = json.dumps(SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM)

class TestTaskSequence(TestCase):

    def tearDown(self):
        rmtree(self.tempdir)

    def setUp(self):
        self.tempdir = mkdtemp(prefix='ocrd-task-sequence-')

        p = Path(self.tempdir, SAMPLE_NAME)
        p.write_text("""\
#!/usr/bin/env python
print('''%s''')
        """ % SAMPLE_OCRD_TOOL_JSON)
        p.chmod(0o777)

        p = Path(self.tempdir, SAMPLE_NAME_WITHOUT_OUTPUT_FILE_GRP)
        p.write_text("""\
#!/usr/bin/env python
print('''%s''')
        """ % SAMPLE_OCRD_TOOL_JSON_WITHOUT_OUTPUT_FILE_GRP)
        p.chmod(0o777)

        p = Path(self.tempdir, SAMPLE_NAME_REQUIRED_PARAM)
        p.write_text("""\
#!/usr/bin/env python
print('''%s''')
        """ % SAMPLE_OCRD_TOOL_JSON_REQUIRED_PARAM)
        p.chmod(0o777)

        os.environ['PATH'] = os.pathsep.join([self.tempdir, os.environ['PATH']])
        #  from distutils.spawn import find_executable as which # pylint: disable=import-error,no-name-in-module
        #  self.assertTrue(which('ocrd-sample-processor'))

    def test_parse_no_in(self):
        task = ProcessorTask.parse('sample-processor')
        with self.assertRaisesRegex(Exception, 'must have input file group'):
            task.validate()

    def test_parse_no_out(self):
        task = ProcessorTask.parse('sample-processor -I IN')
        with self.assertRaisesRegex(Exception, 'Processor requires output_file_grp but none was provided.'):
            task.validate()
        # this should validate
        task2 = ProcessorTask.parse('sample-processor-without-file-grp -I IN')
        self.assertTrue(task2.validate())

    def test_parse_unknown(self):
        with self.assertRaisesRegex(Exception, 'Failed parsing task description'):
            ProcessorTask.parse('sample-processor -x wrong wrong wrong')

    def test_parse_ok(self):
        task_str = 'sample-processor -I IN -O OUT -p /path/to/param.json'
        task = ProcessorTask.parse(task_str)
        self.assertEqual(task.executable, 'ocrd-sample-processor')
        self.assertEqual(task.input_file_grps, ['IN'])
        self.assertEqual(task.output_file_grps, ['OUT'])
        self.assertEqual(task.parameter_path, '/path/to/param.json')
        self.assertEqual(str(task), task_str)

    def test_parse_parameter_none(self):
        task_str = 'sample-processor -I IN -O OUT1,OUT2'
        task = ProcessorTask.parse(task_str)
        self.assertEqual(task.parameter_path, None)
        self.assertEqual(str(task), task_str)

    def test_fail_validate_param(self):
        task = ProcessorTask.parse('sample-processor -I IN -O OUT -p /path/to/param.json')
        with self.assertRaisesRegex(Exception, 'Error parsing'):
            task.validate()

    def test_fail_validate_executable(self):
        task = ProcessorTask.parse('no-such-processor -I IN')
        with self.assertRaisesRegex(Exception, 'Executable not found in '):
            task.validate()

    def test_required_param(self):
        task = ProcessorTask.parse('sample-processor-required-param -I IN -O OUT')
        with self.assertRaisesRegex(Exception, "'param1' is a required property"):
            task.validate()


    def test_validate_sequence(self):
        resolver = Resolver()
        with TemporaryDirectory() as tempdir:
            workspace = resolver.workspace_from_url(assets.path_to('kant_aufklaerung_1784/data/mets.xml'), dst_dir=tempdir)
            params_path = Path(tempdir, 'params.json')
            params_path.write_text('{"param1": true}')
            with self.assertRaisesRegex(Exception, 'Input file group not contained in METS or produced by previous steps: FOO'):
                validate_tasks([ProcessorTask.parse(x) for x in [
                    'sample-processor-required-param -I IN -O OUT -p %s' % params_path,
                    'sample-processor-required-param -I FOO -O OUT -p %s' % params_path
                ]], workspace)

if __name__ == '__main__':
    main()
