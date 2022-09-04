"""
OCR-D CLI: ocrd-tool.json management

.. click:: ocrd.cli.ocrd_tool:ocrd_tool_cli
    :prog: ocrd ocrd-tool
    :nested: full

"""
from json import dumps
import codecs
import sys
import os
import click

from ocrd.decorators import parameter_option, parameter_override_option
from ocrd.processor import Processor
from ocrd_utils import (
    set_json_key_value_overrides,
    VERSION as OCRD_VERSION,
    parse_json_string_with_comments as loads
)
from ocrd_validators import ParameterValidator, OcrdToolValidator

class OcrdToolCtx():

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
    report = OcrdToolValidator.validate(ctx.json)
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

@ocrd_tool_tool.command('list-resources', help="List tool's file resources")
@pass_ocrd_tool
def ocrd_tool_tool_list_resources(ctx):
    class BashProcessor(Processor):
        @property
        def moduledir(self):
            return os.path.dirname(ctx.filename)
    BashProcessor(None, ocrd_tool=ctx.json['tools'][ctx.tool_name],
                  list_resources=True)

@ocrd_tool_tool.command('show-resource', help="Dump a tool's file resource")
@click.argument('res_name')
@pass_ocrd_tool
def ocrd_tool_tool_show_resource(ctx, res_name):
    class BashProcessor(Processor):
        @property
        def moduledir(self):
            return os.path.dirname(ctx.filename)
    BashProcessor(None, ocrd_tool=ctx.json['tools'][ctx.tool_name],
                  show_resource=res_name)

@ocrd_tool_tool.command('help', help="Generate help for processors")
@pass_ocrd_tool
def ocrd_tool_tool_params_help(ctx):
    Processor(None, ocrd_tool=ctx.json['tools'][ctx.tool_name],
              show_help=True)

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
@parameter_option
@parameter_override_option
@click.option('-j', '--json', help='Output JSON instead of shell variables', is_flag=True, default=False)
@pass_ocrd_tool
def ocrd_tool_tool_parse_params(ctx, parameter, parameter_override, json):
    """
    Parse parameters with fallback to defaults and output as shell-eval'able assignments to params var.
    """
    set_json_key_value_overrides(parameter, *parameter_override)
    parameterValidator = ParameterValidator(ctx.json['tools'][ctx.tool_name])
    report = parameterValidator.validate(parameter)
    if not report.is_valid:
        print(report.to_xml())
        sys.exit(1)
    if json:
        print(dumps(parameter))
    else:
        for k in parameter:
            print('params["%s"]="%s"' % (k, parameter[k]))
