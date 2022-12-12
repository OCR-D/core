"""
OCR-D CLI: OCRD-ZIP (BagIt) management

.. click:: ocrd.cli.zip:zip_cli
    :prog: ocrd zip
    :nested: full
"""
import sys

import click

from ocrd_utils import initLogging
from ocrd_validators import OcrdZipValidator

from ..resolver import Resolver
from ..workspace import Workspace
from ..workspace_bagger import WorkspaceBagger

@click.group("zip")
def zip_cli():
    """
    Bag/Spill/Validate OCRD-ZIP bags
    """
    initLogging()

# ----------------------------------------------------------------------
# ocrd zip bag
# ----------------------------------------------------------------------

@zip_cli.command('bag')
@click.argument('dest', type=click.Path(dir_okay=True, writable=True, readable=False, resolve_path=True), required=False)
@click.option('-d', '--directory',
              default='.',
              type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
              help='Workspace folder location.',
              show_default=True)
@click.option('-M', '--mets-basename',
              default="mets.xml",
              help='Basename of the METS file.',
              show_default=True)
@click.option('-i', '--identifier', '--id', help="Ocrd-Identifier", required=True)
@click.option('-m', '--mets', help="location of mets.xml in the bag's data dir", default="mets.xml")
@click.option('-b', '--base-version-checksum', help="Ocrd-Base-Version-Checksum")
@click.option('-t', '--tag-file', help="Add a non-payload file to bag", type=click.Path(file_okay=True, dir_okay=False, readable=True, resolve_path=True), multiple=True)
@click.option('-Z', '--skip-zip', help="Create a directory but do not ZIP it", is_flag=True, default=False)
@click.option('-j', '--processes', help="Number of parallel processes", type=int, default=1)
def bag(directory, mets_basename, dest, identifier, mets, base_version_checksum, tag_file, skip_zip, processes):
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
        ocrd_mets=mets,
        ocrd_base_version_checksum=base_version_checksum,
        processes=processes,
        tag_files=tag_file,
        skip_zip=skip_zip
    )

# ----------------------------------------------------------------------
# ocrd zip spill
# ----------------------------------------------------------------------

@zip_cli.command('spill')
@click.option('-d', '--dest',
              default='.',
              type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
              help='Workspace folder location.',
              show_default=True)
@click.argument('src', type=click.Path(dir_okay=False, readable=True, resolve_path=True), required=True)
def spill(dest, src):
    """
    Spill/unpack OCRD-ZIP bag at SRC to DEST

    SRC must exist an be an OCRD-ZIP
    DEST must not exist and be a directory
    """
    resolver = Resolver()
    workspace_bagger = WorkspaceBagger(resolver)
    workspace = workspace_bagger.spill(src, dest)
    print(workspace)

# ----------------------------------------------------------------------
# ocrd zip validate
# ----------------------------------------------------------------------

@zip_cli.command('validate')
@click.argument('src', type=click.Path(dir_okay=True, readable=True, resolve_path=True), required=True)
@click.option('-Z', '--skip-unzip', help="Treat SRC as a directory not a ZIP", is_flag=True, default=False)
@click.option('-B', '--skip-bag', help="Whether to skip all checks of manifests and files", is_flag=True, default=False)
@click.option('-C', '--skip-checksums', help="Whether to omit checksum checks but still check basic BagIt conformance", is_flag=True, default=False)
@click.option('-D', '--skip-delete', help="Whether to skip deleting the unpacked OCRD-ZIP dir after valdiation", is_flag=True, default=False)
@click.option('-j', '--processes', help="Number of parallel processes", type=int, default=1)
def validate(src, **kwargs):
    """
    Validate OCRD-ZIP

    SRC must exist an be an OCRD-ZIP, either a ZIP file or a directory.
    """
    resolver = Resolver()
    validator = OcrdZipValidator(resolver, src)
    report = validator.validate(**kwargs)
    print(report)
    if not report.is_valid:
        sys.exit(1)

# ----------------------------------------------------------------------
# ocrd zip update
# ----------------------------------------------------------------------

@zip_cli.command('update')
@click.argument('src', type=click.Path(dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dest', type=click.Path(dir_okay=True, readable=True, writable=True, resolve_path=True), required=False)
@click.option('-o', '--overwrite', help="overwrite bag in SRC", is_flag=True)
def update(src, dest=None, overwrite=False):
    """
    Recreate files containing checksums (manifest-sha512.txt, tagmanifest-sha512.txt and
    'Payload-Oxum' contained in bag-info.txt) of an OCRD-ZIP.

    Open the bag (zip file or directory) ``src``, create or update its manifests/checksums and
    output to (zip file or directory) ``dest``. It is also possible to output to ``src`` / overwrite
    ``src`` in place when ``--overwrite``-flag is given.
    """
    WorkspaceBagger(Resolver()).recreate_checksums(src, dest=dest, overwrite=overwrite)
