from json import loads, dumps
from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

# pylint: disable=import-error, no-name-in-module
from tests.base import TestCase, main, assets, copy_of_directory

from ocrd_utils import pushd_popd
from ocrd.resolver import Resolver

from ocrd.cli.validate import validate_cli
from tests.test_task_sequence import TestTaskSequence

OCRD_TOOL = '''
{
    "git_url": "https://github.com/ocr-d/foo",
    "version": "0.0.1",
    "tools": {
        "ocrd-xyz": {
            "executable": "ocrd-xyz",
            "description": "bars all the foos",
            "input_file_grp": ["OCR-D-FOO"],
            "output_file_grp": ["OCR-D-BAR"],
            "categories": ["Layout analysis"],
            "steps": ["layout/analysis"],
            "parameters": {
                "num-param": {
                    "type": "number",
                    "default": 1,
                    "description": "foo"
                },
                "baz": {
                    "type": "string",
                    "required": true,
                    "description": "wow such foo"
                },
                "foo": {
                    "type": "string",
                    "enum": ["foo"],
                    "required": false,
                    "description": "return of the foo"
                }
            }
        }
    }
}
'''

# inherit from TestTaskSequence for the setUp/tearDown methods
class TestCli(TestTaskSequence):

    def __init__(self, *args, **kwargs):
        super(TestTaskSequence, self).__init__(*args, **kwargs)
        self.runner = CliRunner()

    def test_validate_ocrd_tool(self):
        with TemporaryDirectory() as tempdir:
            json_path = Path(tempdir, 'ocrd-tool.json')
            json_path.write_text(OCRD_TOOL)

            # normal call
            result = self.runner.invoke(validate_cli, ['tool-json', str(json_path)])
            self.assertEqual(result.exit_code, 0)
            # relative path
            with pushd_popd(tempdir):
                result = self.runner.invoke(validate_cli, ['tool-json', 'ocrd-tool.json'])
                self.assertEqual(result.exit_code, 0)
            # default path
            with pushd_popd(tempdir):
                result = self.runner.invoke(validate_cli, ['tool-json'])
                self.assertEqual(result.exit_code, 0)

    def test_validate_parameter(self):
        with TemporaryDirectory() as tempdir:
            json_path = Path(tempdir, 'ocrd-tool.json')
            json_path.write_text(OCRD_TOOL)
            with pushd_popd(tempdir):
                result = self.runner.invoke(validate_cli, ['parameters', 'ocrd-tool.json', 'ocrd-xyz', dumps({"baz": "foo"})])
                self.assertEqual(result.exit_code, 0)

    def test_validate_page(self):
        page_path = assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS.xml')
        result = self.runner.invoke(validate_cli, ['page', page_path])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('<report valid="false">', result.stdout)

    def test_validate_tasks(self):
        # simple
        result = self.runner.invoke(validate_cli, ['tasks',
            "sample-processor-required-param -I FOO -O OUT1 -p '{\"param1\": true}'",
            "sample-processor-required-param -I FOO -O OUT2 -p '{\"param1\": true}'",
        ])
        self.assertEqual(result.exit_code, 0)

        # with workspace
        result = self.runner.invoke(validate_cli, ['tasks', '--workspace', assets.path_to('kant_aufklaerung_1784/data'),
            "sample-processor-required-param -I OCR-D-IMG -O OUT1 -p '{\"param1\": true}'",
            "sample-processor-required-param -I OCR-D-IMG -O OUT2 -p '{\"param1\": true}'",
        ])
        print(result)
        print(result.stdout)
        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    main()
