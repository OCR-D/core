import codecs
import json

import click
import yaml

from ocrd import run_cli, OcrdSwagger, Resolver, WorkspaceValidator, OcrdToolValidator, Workspace
from ocrd.decorators import ocrd_cli_options

from ocrd.webservice.processor import create as create_processor_ws
from ocrd.webservice.repository import create as create_repository_ws

@click.group()
def cli():
    """
    CLI to OCR-D
    """
# ----------------------------------------------------------------------
# ocrd validate-ocrd-tool
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
# ocrd workspace
# ----------------------------------------------------------------------

@cli.group("workspace", help="Working with workspace")
def workspace_cli():
    pass

# ----------------------------------------------------------------------
# ocrd workspace validate
# ----------------------------------------------------------------------

@workspace_cli.command('validate', help='Validate a workspace')
@click.option('-m', '--mets-url', help="METS URL to validate", required=True)
def validate_workspace(mets_url):
    resolver = Resolver(cache_enabled=True)
    report = WorkspaceValidator.validate_url(resolver, mets_url)
    print(report.to_xml())
    if not report.is_valid:
        return 128

@workspace_cli.command('create-from-url', help="Create a workspace from a METS URL and return the directory")
@click.option('-m', '--mets-url', help="METS URL to create workspace for", required=True)
@click.option('-a', '--download-all', is_flag=True, default=False, help="Whether to download all files into the workspace")
def workspace_create(mets_url, download_all):
    resolver = Resolver(cache_enabled=True)
    workspace = resolver.workspace_from_url(mets_url)
    if download_all:
        for fileGrp in workspace.mets.file_groups:
            for f in workspace.mets.find_files(fileGrp=fileGrp):
                workspace.download_file(f, subdir=fileGrp, basename=f.ID)
    workspace.save_mets()
    print(workspace.directory)

@workspace_cli.command('add-file', help="Add a file to METS in a workspace")
@click.option('-w', '--working-dir', help="Directory of the workspace", required=True)
@click.option('-G', '--filegrp', help="fileGrp USE", required=True)
@click.option('-i', '--fileid', help="ID for the file")
@click.option('-g', '--groupid', help="GROUPID")
@click.argument('local_filename')
def workspace_add_file(working_dir, filegrp, local_filename, fileid, groupid):
    resolver = Resolver(cache_enabled=True)
    workspace = Workspace(resolver, working_dir)
    workspace.mets.add_file(filegrp, local_filename=local_filename)
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd generate-swagger
# ----------------------------------------------------------------------

@cli.command('generate-swagger', help="Generate Swagger schema from ocrd-tool.json files")
@click.option('-S', '--swagger-template', help="Swagger template to add operations to. Use builtin if not specified.")
@click.option('-T', '--ocrd-tool', multiple=True, help="ocrd-tool.json file to generate from. Repeatable")
@click.option('-f', '--format', help="Format to generate, JSON or YAML", type=click.Choice(['JSON', 'YAML']), default='JSON')
def generate_swagger(swagger_template, ocrd_tool, **kwargs):
    swagger = OcrdSwagger.from_ocrd_tools(swagger_template, *ocrd_tool)
    if kwargs['format'] == 'YAML':
        print(yaml.dump(swagger))
    else:
        print(json.dumps(swagger, indent=2))

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------

@cli.command('process')
@ocrd_cli_options
@click.option('-T', '--ocrd-tool', multiple=True)
@click.argument('steps', nargs=-1)
def process_cli(mets_url, **kwargs):
    """
    Execute OCR-D processors for a METS file directly.
    """
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
