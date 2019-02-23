#  import os
#  from tempfile import TemporaryDirectory

from tests.base import TestCase, main

from ocrd.task_sequence import ProcessorTask

class TestTaskSequence(TestCase):

    def test_parse_no_in(self):
        task = ProcessorTask.parse('sample-processor1')
        with self.assertRaisesRegex(Exception, 'must have input file group'):
            task.validate()

    def test_parse_no_out(self):
        task = ProcessorTask.parse('sample-processor1 -I IN')
        with self.assertRaisesRegex(Exception, 'must have output file group'):
            task.validate()

    def test_parse_unknown(self):
        with self.assertRaisesRegex(Exception, 'Failed parsing task description'):
            ProcessorTask.parse('sample-processor1 -x wrong wrong wrong')

    def test_parse_ok(self):
        task_str = 'sample-processor1 -I IN -O OUT -p /path/to/param.json'
        task = ProcessorTask.parse(task_str)
        self.assertEqual(task.executable, 'ocrd-sample-processor1')
        self.assertEqual(task.input_file_grps, ['IN'])
        self.assertEqual(task.output_file_grps, ['OUT'])
        self.assertEqual(task.parameter_path, '/path/to/param.json')
        self.assertEqual(str(task), task_str)

    def test_parse_parameter_none(self):
        task_str = 'sample-processor1 -I IN -O OUT1,OUT2'
        task = ProcessorTask.parse(task_str)
        self.assertEqual(task.parameter_path, None)
        self.assertEqual(str(task), task_str)

    def test_fail_validate_param(self):
        task = ProcessorTask.parse('sample-processor1 -I IN -O OUT -p /path/to/param.json')
        with self.assertRaisesRegex(Exception, 'Parameter file not readable'):
            task.validate()

    def test_fail_validate_executable(self):
        task = ProcessorTask.parse('sample-processor1 -I IN -O OUT -p /tmp')
        with self.assertRaisesRegex(Exception, 'Executable not found in '):
            task.validate()


if __name__ == '__main__':
    main()
