from __future__ import absolute_import

import click

from ocrd import init

@click.command()
@click.option('-w', '--working-dir', default='/tmp', help='Path to store intermediate and result files', type=click.Path(exists=True))
@click.argument('METS_XML', type=click.File('rb'))
def cli(working_dir, mets_xml):
    """
    Perform OCR for a given METS file.
    """

    # read METS
    initializer = init.Initializer()
    initializer.load(mets_xml)

    # set the working dir
    initializer.set_working_dir(working_dir)

    # initialize
    initializer.initialize()
