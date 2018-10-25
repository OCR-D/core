from json import dumps, loads
import codecs
import sys

import click

from ocrd import OcrdToolValidator
from ocrd.constants import VERSION as OCRD_VERSION
from ocrd.validator import ParameterValidator

class OcrdToolCtx(object):

    def __init__(self, filename):
        self.filename = filename
        with codecs.open(filename, encoding='utf-8') as f:
            self.content = f.read()
            self.json = loads(self.content)

pass_ocrd_tool = click.make_pass_decorator(OcrdToolCtx)

# ----------------------------------------------------------------------
# ocrd ocrd-tool
# ----------------------------------------------------------------------

@click.group('ocrd-tool', help='Work with ocrd-tool.json JSON_FILE')
@click.argument('json_file')
@click.pass_context
def ocrd_tool_cli(ctx, json_file):
    ctx.obj = OcrdToolCtx(json_file)

# ----------------------------------------------------------------------
# ocrd ocrd-tool version
# ----------------------------------------------------------------------

@ocrd_tool_cli.command('version', help='Version of ocrd-tool.json')
@pass_ocrd_tool
def ocrd_tool_version(ctx):
    print('Version "%s", ocrd/core "%s"' % (ctx.json['version'], OCRD_VERSION))

# ----------------------------------------------------------------------
# ocrd ocrd-tool validate
# ----------------------------------------------------------------------

@ocrd_tool_cli.command('validate', help='Validate an ocrd-tool.json')
@pass_ocrd_tool
def ocrd_tool_validate(ctx):
    report = OcrdToolValidator.validate_json(ctx.json)
    print(report.to_xml())
    if not report.is_valid:
        return 128

# ----------------------------------------------------------------------
# ocrd ocrd-tool list-tools
# ----------------------------------------------------------------------

@ocrd_tool_cli.command('list-tools', help="List tools")
@pass_ocrd_tool
def ocrd_tool_list(ctx):
    for tool in ctx.json['tools']:
        print(tool)

# ----------------------------------------------------------------------
# ocrd ocrd-tool tool
# ----------------------------------------------------------------------

@ocrd_tool_cli.group('tool', help='Work with a single tool TOOL_NAME')
@click.argument('tool_name')
@pass_ocrd_tool
def ocrd_tool_tool(ctx, tool_name):
    if tool_name not in ctx.json['tools']:
        raise Exception("No such tool: %s" % tool_name)
    ctx.tool_name = tool_name

# ----------------------------------------------------------------------
# ocrd ocrd-tool tool description
# ----------------------------------------------------------------------

@ocrd_tool_tool.command('description', help="Describe tool")
@pass_ocrd_tool
def ocrd_tool_tool_description(ctx):
    print(ctx.json['tools'][ctx.tool_name]['description'])

# ----------------------------------------------------------------------
# ocrd ocrd-tool tool categories
# ----------------------------------------------------------------------

@ocrd_tool_tool.command('categories', help="Categories of tool")
@pass_ocrd_tool
def ocrd_tool_tool_categories(ctx):
    print('\n'.join(ctx.json['tools'][ctx.tool_name]['categories']))

# ----------------------------------------------------------------------
# ocrd ocrd-tool tool steps
# ----------------------------------------------------------------------

@ocrd_tool_tool.command('steps', help="Steps of tool")
@pass_ocrd_tool
def ocrd_tool_tool_steps(ctx):
    print('\n'.join(ctx.json['tools'][ctx.tool_name]['steps']))

# ----------------------------------------------------------------------
# ocrd ocrd-tool tool dump
# ----------------------------------------------------------------------

@ocrd_tool_tool.command('dump', help="Dump JSON of tool")
@pass_ocrd_tool
def ocrd_tool_tool_dump(ctx):
    print(dumps(ctx.json['tools'][ctx.tool_name], indent=True))

# ----------------------------------------------------------------------
# ocrd ocrd-tool tool parse-params
# ----------------------------------------------------------------------

@ocrd_tool_tool.command('parse-params')
@click.option('-p', '--parameters', help='Parameter JSON file', type=click.Path())
@click.option('-j', '--json', help='Output JSON instead of shell variables', is_flag=True, default=False)
@pass_ocrd_tool
def ocrd_tool_tool_parse_params(ctx, parameters, json):
    """
    Parse parameters with fallback to defaults and output as shell-eval'able assignments to params var.
    """
    if parameters is None or parameters == "":
        parameters = {}
    else:
        with open(parameters, 'r') as f:
            parameters = loads(f.read())
    parameterValidator = ParameterValidator(ctx.json['tools'][ctx.tool_name])
    report = parameterValidator.validate(parameters)
    if not report.is_valid:
        print(report.to_xml())
        sys.exit(1)
    if json:
        print(dumps(parameters))
    else:
        for k in parameters:
            print('params["%s"]="%s"' % (k, parameters[k]))
