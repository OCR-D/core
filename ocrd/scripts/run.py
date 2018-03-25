import click

from ocrd.resolver import Resolver
from ocrd.processor.characterize.exif import ExifProcessor

@click.group()
@click.option('-w', '--working-dir', default='/tmp', help='Path to store intermediate and result files (default: "/tmp")', type=click.Path(exists=True))
@click.option('-m', '--mets-xml', help="METS file to run", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, working_dir, mets_xml):
    """
    Perform OCR for a given METS file.
    """
    resolver = Resolver(cache_enabled=False)
    workspace = resolver.create_workspace('file://' + mets_xml)
    ctx.obj = workspace
    #  setattr(ctx, 'workspace', workspace)
    #  ctx.obj = {}
    #  ctx.obj.workspace = workspace
    #  setattr(ctx.obj, 'workspace', workspace)
    #  setattr(ctx.obj, 'mets_xml', mets_xml)

@cli.command('characterize/exif')
@click.pass_context
def characterize_exif(ctx):
    """
    Characterize images with exiftool
    """
    workspace = ctx.obj
    ExifProcessor(workspace).process()
    workspace.save_mets()

    #  #  print subcommand

    #  # read METS
    #  initializer = init.Initializer()
    #  initializer.load(mets_xml)

    #  # set the working dir
    #  initializer.set_working_dir(working_dir)

    #  # initialize
    #  initializer.initialize()

    #  # image characterization
    #  characterizer = characterize.Characterizer()
    #  characterizer.set_handle(initializer.get_handle())
    #  characterizer.characterize()

    #  # page segmentation
    #  page_segmenter = segment.PageSegmenter()
    #  page_segmenter.set_handle(initializer.get_handle())
    #  page_segmenter.segment()

    #  # region segmentation
    #  region_segmenter = segment.RegionSegmenter()
    #  region_segmenter.set_handle(initializer.get_handle())
    #  region_segmenter.segment()

    #  # output
    #  for ID in initializer.get_handle().page_trees:
    #      print(md.parseString(ET.tostring(initializer.get_handle().page_trees[ID].getroot(), encoding='utf8', method='xml')).toprettyxml(indent="\t"))
    #      pass
