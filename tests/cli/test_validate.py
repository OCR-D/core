from json import dumps
from os import chdir
from pathlib import Path

# pylint: disable=import-error, no-name-in-module
from tests.base import main, assets, invoke_cli
from tests.data.wf_testcase import TestCase

from ocrd.resolver import Resolver
from ocrd.cli.validate import validate_cli

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
class TestCli(TestCase):

    def test_validate_tasks(self):
        # simple
        code, _, _ = self.invoke_cli(validate_cli, ['tasks',
            "sample-processor-required-param -I FOO -O OUT1 -p '{\"param1\": true}'",
            "sample-processor-required-param -I FOO -O OUT2 -p '{\"param1\": true}'",
        ])
        assert code == 0

        # with workspace
        code, out, err = self.invoke_cli(validate_cli, ['tasks', '--workspace', assets.path_to('kant_aufklaerung_1784/data'),
            "sample-processor-required-param -I OCR-D-IMG,OCR-D-GT-PAGE -O OUT1 -p '{\"param1\": true}'",
            "sample-processor-required-param -I OCR-D-IMG,OCR-D-GT-PAGE -O OUT2 -p '{\"param1\": true}'",
        ])
        print('code=%s out=%s err=%s' % (code, out, err))
        assert code == 0


def test_validate_ocrd_tool_normal_call(tmp_path, capfd):
    json_path = Path(tmp_path, 'ocrd-tool.json')
    json_path.write_text(OCRD_TOOL)

    # normal call
    code, _, _ = invoke_cli(validate_cli, ['tool-json', str(json_path)], capfd)
    assert code == 0


def test_validate_ocrd_tool_relative_path(tmp_path, capfd):
    json_path = Path(tmp_path, 'ocrd-tool.json')
    json_path.write_text(OCRD_TOOL)
    chdir(tmp_path)

    # act
    code, _, _ = invoke_cli(validate_cli, ['tool-json', 'ocrd-tool.json'], capfd)

    # assert
    assert code == 0


def test_validate_ocrd_tool_default_path(tmp_path, capfd):
    json_path = Path(tmp_path, 'ocrd-tool.json')
    json_path.write_text(OCRD_TOOL)
    chdir(tmp_path)

    # act
    code, _, _ = invoke_cli(validate_cli, ['tool-json'], capfd)

    # assert
    assert code == 0


def test_validate_parameter(tmp_path, capfd):
    json_path = Path(tmp_path, 'ocrd-tool.json')
    json_path.write_text(OCRD_TOOL)
    chdir(tmp_path)
    code, _, _ = invoke_cli(validate_cli, ['parameters', 'ocrd-tool.json', 'ocrd-xyz', dumps({"baz": "foo"})], capfd)
    assert code == 0


def test_validate_page(capfd):
    page_path = assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS.xml')
    code, out, _ = invoke_cli(validate_cli, ['page', page_path], capfd)
    assert code == 1
    assert '<report valid="false">' in out


if __name__ == '__main__':
    main(__file__)
