import click

from ocrd.resolver import Resolver
from ocrd.processor.characterize.exif import ExifProcessor
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesseract3 import Tesseract3LineSegmenter

@click.group()
@click.option('-m', '--mets-xml', help="METS file to run", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, mets_xml):
    """
    Execute OCR-D modules for a METS file.
    """
    resolver = Resolver(cache_enabled=True)
    ctx.obj = resolver.create_workspace('file://' + mets_xml)

@cli.command('characterize/exif')
@click.pass_context
def characterize_exif(ctx):
    """
    Characterize images with exiftool
    """
    ExifProcessor(ctx.obj).process()
    ctx.obj.persist()

@cli.command('segment-region/tesseract3')
@click.pass_context
def segment_region_tesseract3(ctx):
    """
    Segment page into regions
    """
    Tesseract3RegionSegmenter(ctx.obj).process()
    ctx.obj.persist()

@cli.command('segment-line/tesseract3')
@click.pass_context
def segment_line_tesseract3(ctx):
    """
    Segment page/regions into lines
    """
    Tesseract3LineSegmenter(ctx.obj).process()
    ctx.obj.persist()
