import codecs

import click

from ocrd import OcrdToolValidator

# ----------------------------------------------------------------------
# ocrd validate-ocrd-tool
# ----------------------------------------------------------------------

@click.command('validate-ocrd-tool', help='Validate an ocrd-tool.json')
@click.argument('json_file', "ocrd-tool.json to validate")
def validate_ocrd_tool_cli(json_file):
    with codecs.open(json_file, encoding='utf-8') as f:
        report = OcrdToolValidator.validate_json(f.read())
    print(report.to_xml())
    if not report.is_valid:
        return 128
