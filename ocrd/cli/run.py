import click

from ocrd.processor import run_processor
from ocrd.processor.characterize.exif import ExifProcessor
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesseract3 import Tesseract3LineSegmenter
from ocrd.resolver import Resolver

from ocrd.webservice.processor import create as create_processor_ws

@click.group()
def cli():
    """
    CLI to OCR-D
    """
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
        ctx.obj['workspace'] = resolver.create_workspace(ctx.obj['mets_url'])

@process_cli.command('characterize/exif')
@click.pass_context
def _characterize_exif(ctx):
    """
    Characterize images with exiftool
    """
    run_processor(ExifProcessor, workspace=ctx.obj['workspace'])

@process_cli.command('segment-region/tesseract3')
@click.pass_context
def _segment_region_tesseract3(ctx):
    """
    Segment page into regions
    """
    run_processor(Tesseract3RegionSegmenter, workspace=ctx.obj['workspace'])

@process_cli.command('segment-line/tesseract3')
@click.pass_context
def _segment_line_tesseract3(ctx):
    """
    Segment page/regions into lines
    """
    run_processor(Tesseract3LineSegmenter, workspace=ctx.obj['workspace'])

# ----------------------------------------------------------------------
# ocrd server
# ----------------------------------------------------------------------

@cli.group('server')
def server_cli():
    """
    Start OCR-D web services
    """

@server_cli.command()
@click.option('-p', '--port', help="Port to run processor webservice on", default=5010)
def processor(port):
    """
    Start a server exposing the processors as webservices
    """
    create_processor_ws().run(port=port)
