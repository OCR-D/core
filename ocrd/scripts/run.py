import click

from ocrd.processor import run_processor
from ocrd.processor.characterize.exif import ExifProcessor
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesseract3 import Tesseract3LineSegmenter
from ocrd.resolver import Resolver

@click.group()
@click.option('-m', '--mets-xml', help="METS file to run", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, mets_xml):
    """
    Execute OCR-D modules for a METS file.
    """
    resolver = Resolver(cache_enabled=True)
    ctx.obj = {}
    ctx.obj['mets_url'] = 'file://' + mets_xml
    ctx.obj['workspace'] = resolver.create_workspace(ctx.obj['mets_url'])

@cli.command('characterize/exif')
@click.pass_context
def _characterize_exif(ctx):
    """
    Characterize images with exiftool
    """
    run_processor(ExifProcessor, workspace=ctx.obj['workspace'])

@cli.command('segment-region/tesseract3')
@click.pass_context
def _segment_region_tesseract3(ctx):
    """
    Segment page into regions
    """
    run_processor(Tesseract3RegionSegmenter, workspace=ctx.obj['workspace'])

@cli.command('segment-line/tesseract3')
@click.pass_context
def _segment_line_tesseract3(ctx):
    """
    Segment page/regions into lines
    """
    run_processor(Tesseract3LineSegmenter, workspace=ctx.obj['workspace'])
