from os.path import abspath

import click

from ..resolver import Resolver
from ..workspace import Workspace
from ..workspace_bagger import WorkspaceBagger

@click.group("zip")
def zip_cli():
    """
    Bag/Spill/Validate OCRD-ZIP bags
    """

# ----------------------------------------------------------------------
# ocrd zip bag
# ----------------------------------------------------------------------

@zip_cli.command('bag')
@click.option('-d', '--directory',
              default='.',
              type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
              help='Workspace folder location.',
              show_default=True)
@click.option('-M', '--mets-basename',
              default="mets.xml",
              help='The basename of the METS file.',
              show_default=True)
@click.option('-i', '--identifier', '--id', help="Ocrd-Identifier", required=True)
@click.option('-D', '--manifestation-depth', help="Ocrd-Manifestation-Depth", type=click.Choice(['full', 'partial']), default='partial')
@click.option('-m', '--mets', help="location of mets.xml in the bag's data dir", default="mets.xml")
@click.option('-b', '--base-version-checksum', help="Ocrd-Base-Version-Checksum")
@click.option('-j', '--jobs', help="Number of parallel processes", type=int, default=1)
@click.argument('dest', type=click.Path(dir_okay=False, writable=True, readable=False, resolve_path=True), required=False)
def bag(directory, mets_basename, dest, identifier, manifestation_depth, mets, base_version_checksum, jobs):
    """
    Bag workspace as OCRD-ZIP at DEST
    """
    resolver = Resolver()
    workspace = Workspace(resolver, directory=directory, mets_basename=mets_basename)
    workspace_bagger = WorkspaceBagger(resolver)
    workspace_bagger.bag(
        workspace,
        dest=dest,
        ocrd_identifier=identifier,
        ocrd_manifestation_depth=manifestation_depth,
        ocrd_mets=mets,
        ocrd_base_version_checksum=base_version_checksum,
        no_processes=jobs
    )
