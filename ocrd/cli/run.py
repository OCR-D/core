import click

from ocrd.processor.base import run_processor
from ocrd.processor.characterize.exif import ExifProcessor
from ocrd.processor.segment_region.tesserocr import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesserocr import Tesseract3LineSegmenter
from ocrd.processor.recognize.tesserocr import Tesseract3Recognizer
from ocrd.resolver import Resolver

from ocrd.webservice.processor import create as create_processor_ws
from ocrd.webservice.repository import create as create_repository_ws

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

@process_cli.command('segment-region/tesserocr')
@click.pass_context
def _segment_region_tesserocr(ctx):
    """
    Segment page into regions
    """
    run_processor(Tesseract3RegionSegmenter, workspace=ctx.obj['workspace'])

@process_cli.command('segment-line/tesserocr')
@click.pass_context
def _segment_line_tesserocr(ctx):
    """
    Segment page/regions into lines
    """
    run_processor(Tesseract3LineSegmenter, workspace=ctx.obj['workspace'])

@process_cli.command('recognize/tesserocr')
@click.pass_context
def _recognize_tesserocr(ctx):
    """
    Recognize lines
    """
    run_processor(Tesseract3Recognizer, workspace=ctx.obj['workspace'])

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
