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
from ocrd_utils.constants import DEFAULT_METS_BASENAME
import ocrd_models.constants
import ocrd_validators.constants
from ocrd.decorators import (
    parameter_option,
    parameter_override_option,
    ocrd_loglevel,
    ocrd_cli_wrap_processor
)
from ocrd_utils import (
    is_local_filename,
    get_local_filename,
    initLogging,
    getLogger,
    make_file_id,
    config
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
@click.option('-m', '--mets', help="METS to process", default=DEFAULT_METS_BASENAME)
@click.option('-w', '--working-dir', help="Working Directory")
@click.option('-I', '--input-file-grp', help='File group(s) used as input.', default=None)
@click.option('-O', '--output-file-grp', help='File group(s) used as output.', default=None)
# repeat some other processor options for convenience (will be ignored here)
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.option('--overwrite', is_flag=True, default=False, help="Remove output pages/images if they already exist\n"
              "(with '--page-id', remove only those).\n"
              "Short-hand for OCRD_EXISTING_OUTPUT=OVERWRITE")
@click.option('--debug', is_flag=True, default=False, help="Abort on any errors with full stack trace.\n"
              "Short-hand for OCRD_MISSING_OUTPUT=ABORT")
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
    class BashlibProcessor(Processor):
        @property
        def ocrd_tool(self):
            return {'executable': '', 'steps': ['']}
        @property
        def version(self):
            return '1.0'
        # go half way of the normal run_processor / process_workspace call tree
        # by just delegating to process_workspace, overriding process_page_file
        # to ensure all input files exist locally (without persisting them in the METS)
        # and print what needs to be acted on in bash-friendly way
        def process_page_file(self, *input_files):
            for field in ['url', 'local_filename', 'ID', 'mimetype', 'pageId']:
                # make this bash-friendly (show initialization for associative array)
                if len(input_files) > 1:
                    # single quotes allow us to preserve the list value inside the alist
                    value = ' '.join(str(getattr(res, field)) for res in input_files)
                else:
                    value = str(getattr(input_files[0], field))
                print(f"[{field}]='{value}'", end=' ')
            output_file_id = make_file_id(input_files[0], kwargs['output_file_grp'])
            print(f"[outputFileId]='{output_file_id}'")
    ocrd_cli_wrap_processor(BashlibProcessor, **kwargs)
