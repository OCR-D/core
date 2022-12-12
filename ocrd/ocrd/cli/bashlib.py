"""
OCR-D CLI: bash library

.. click:: ocrd.cli.bashlib:bashlib_cli
    :prog: ocrd bashlib
    :nested: full

"""
from __future__ import print_function
import sys
from os.path import isfile
import click

from ocrd.constants import BASHLIB_FILENAME
import ocrd.constants
import ocrd_utils.constants
import ocrd_models.constants
import ocrd_validators.constants
from ocrd.decorators import (
    parameter_option,
    parameter_override_option,
    ocrd_loglevel
)
from ocrd_utils import (
    is_local_filename,
    get_local_filename,
    initLogging,
    make_file_id
)
from ocrd.resolver import Resolver
from ocrd.processor import Processor

# ----------------------------------------------------------------------
# ocrd bashlib
# ----------------------------------------------------------------------

@click.group('bashlib')
def bashlib_cli():
    """
    Work with bash library
    """

# ----------------------------------------------------------------------
# ocrd bashlib filename
# ----------------------------------------------------------------------

@bashlib_cli.command('filename')
def bashlib_filename():
    """
    Dump the bash library filename for sourcing by shell scripts

    For functions exported by bashlib, see `<../../README.md>`_
    """
    print(BASHLIB_FILENAME)

@bashlib_cli.command('constants')
@click.argument('name')
def bashlib_constants(name):
    """
    Query constants from ocrd_utils and ocrd_models
    """
    all_constants = {}
    for src in [ocrd.constants, ocrd_utils.constants, ocrd_models.constants, ocrd_validators.constants]:
        for k in src.__all__:
            all_constants[k] = src.__dict__[k]
    if name in ['*', 'KEYS', '__all__']:
        print(sorted(all_constants.keys()))
        sys.exit(0)
    if name not in all_constants:
        print("ERROR: name '%s' is not a known constant" % name, file=sys.stderr)
        sys.exit(1)
    val = all_constants[name]
    if isinstance(val, dict):
        # make this bash-friendly (show initialization for associative array)
        for key in val:
            print("[%s]=%s" % (key, val[key]), end=' ')
    else:
        print(val)

@bashlib_cli.command('input-files')
@click.option('-m', '--mets', help="METS to process", default="mets.xml")
@click.option('-w', '--working-dir', help="Working Directory")
@click.option('-I', '--input-file-grp', help='File group(s) used as input.', default='INPUT')
@click.option('-O', '--output-file-grp', help='File group(s) used as output.', default='OUTPUT')
# repeat some other processor options for convenience (will be ignored here)
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.option('--overwrite', is_flag=True, default=False, help="Remove output pages/images if they already exist")
@parameter_option
@parameter_override_option
@ocrd_loglevel
def bashlib_input_files(**kwargs):
    """
    List input files for processing

    Instantiate a processor and workspace from the given processing options.
    Then loop through the input files of the input fileGrp, and for each one,
    print its `url`, `ID`, `mimetype` and `pageId`, as well as its recommended
    `outputFileId` (from ``make_file_id``).

    (The printing format is one associative array initializer per line.)
    """
    initLogging()
    mets = kwargs.pop('mets')
    working_dir = kwargs.pop('working_dir')
    if is_local_filename(mets) and not isfile(get_local_filename(mets)):
        msg = "File does not exist: %s" % mets
        raise Exception(msg)
    resolver = Resolver()
    workspace = resolver.workspace_from_url(mets, working_dir)
    processor = Processor(workspace,
                          ocrd_tool=None,
                          page_id=kwargs['page_id'],
                          input_file_grp=kwargs['input_file_grp'],
                          output_file_grp=kwargs['output_file_grp'])
    for input_file in processor.input_files:
        for field in ['url', 'ID', 'mimetype', 'pageId']:
            # make this bash-friendly (show initialization for associative array)
            print("[%s]='%s'" % (field, getattr(input_file, field)), end=' ')
        print("[outputFileId]='%s'" % make_file_id(input_file, kwargs['output_file_grp']))
