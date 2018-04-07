import click

from ocrd.resolver import Resolver
from ocrd.validator import WorkspaceValidator

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
def validate_cli(mets_url):
    resolver = Resolver(cache_enabled=True)
    report = WorkspaceValidator.validate_url(resolver, mets_url)
    print(report.to_xml())
    if not report.is_valid:
        return 128

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------

@cli.group('process', chain=True)
@click.option('-m', '--mets-xml', help="METS file to run", type=click.Path(exists=True))
@click.pass_context
def process_cli(ctx, mets_xml):
    """
    Execute OCR-D processors for a METS file directly.
    """
    resolver = Resolver(cache_enabled=True)
    ctx.obj = {}
    if mets_xml:
        ctx.obj['mets_url'] = 'file://' + mets_xml
        ctx.obj['workspace'] = resolver.workspace_from_url(ctx.obj['mets_url'])

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
