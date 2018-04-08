import codecs
import json

import click

from ocrd.resolver import Resolver
from ocrd.processor.base import run_cli
from ocrd.validator import WorkspaceValidator, OcrdToolValidator
from ocrd.decorators import ocrd_cli_options

from ocrd.webservice.processor import create as create_processor_ws
from ocrd.webservice.repository import create as create_repository_ws

@click.group()
def cli():
    """
    CLI to OCR-D
    """
# ----------------------------------------------------------------------
# ocrd validate-workspace
# ----------------------------------------------------------------------

@cli.command('validate-workspace', help='Validate a workspace')
@click.option('-m', '--mets-url', help="METS URL to validate")
def validate_workspace(mets_url):
    resolver = Resolver(cache_enabled=True)
    report = WorkspaceValidator.validate_url(resolver, mets_url)
    print(report.to_xml())
    if not report.is_valid:
        return 128

# ----------------------------------------------------------------------
# ocrd validate-workspace
# ----------------------------------------------------------------------

@cli.command('validate-ocrd-tool', help='Validate an ocrd-tool.json')
@click.argument('json_file', "ocrd-tool.json to validate")
def validate_ocrd_tool(json_file):
    with codecs.open(json_file, encoding='utf-8') as f:
        report = OcrdToolValidator.validate_json(f.read())
    print(report.to_xml())
    if not report.is_valid:
        return 128

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------

@cli.command('process')
@ocrd_cli_options
@click.option('-T', '--ocrd-tool', multiple=True)
@click.argument('steps', nargs=-1)
def process_cli(mets_url, *args, **kwargs):
    """
    Execute OCR-D processors for a METS file directly.
    """
    if mets_url.find('://') == -1:
        mets_url = 'file://' + mets_url
    resolver = Resolver(cache_enabled=True)
    workspace = resolver.workspace_from_url(mets_url)

    cmds = []
    for ocrd_tool_file in kwargs['ocrd_tool']:
        with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
            obj = json.loads(f.read())
            for tool in obj['tools']:
                cmds.append(tool['binary'])

    for cmd in kwargs['steps']:
        if cmd not in cmds:
            raise Exception("Tool not registered: '%s'" % cmd)

    for cmd in kwargs['steps']:
        run_cli(cmd, mets_url, resolver, workspace)

    workspace.reload_mets()

    #  print('\n'.join(k + '=' + str(kwargs[k]) for k in kwargs))
    print(workspace)

# ----------------------------------------------------------------------
# ocrd server
# ----------------------------------------------------------------------

@cli.group('server')
def server_cli():
    """
    Start OCR-D web services
    """

@server_cli.command('process')
@click.option('-p', '--port', help="Port to run processor webservice on", default=5010)
def _start_processor(port):
    """
    Start a server exposing the processors as webservices
    """
    create_processor_ws().run(port=port)

@server_cli.command('repository')
@click.option('-p', '--port', help="Port to run repository webservice on", default=5000)
def _start_repository(port):
    """
    Start a minimal repository.
    """
    create_repository_ws().run(port=port)
