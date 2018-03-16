from __future__ import absolute_import

import click

from ocrd import init, segment, webservices

@click.command()
@click.option('-w', '--working-dir', default='/tmp', help='Path to store intermediate and result files (default: "/tmp")', type=click.Path(exists=True))
def cli(working_dir):
    """
    Starts a web service.
    """

    # create initializer (needed for standalone running)
    initializer = init.Initializer()
    initializer.set_working_dir(working_dir)

    # page segmentation
    page_segmenter = segment.PageSegmenter()

    #
    # load app and run
    #
    ws = webservices.create_page_segmentation_ws(initializer,page_segmenter)
    ws.run()
