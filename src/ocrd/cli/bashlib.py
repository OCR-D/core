"""
OCR-D CLI: bash library

.. click:: ocrd.cli.bashlib:bashlib_cli
    :prog: ocrd bashlib
    :nested: full

"""

# WARNING: bashlib processors have been deprecated as of v3 of the OCR-D/core API
#          and will be removed in v3.7.0. We retain the `ocrd bashlib` CLI only
#          to not break the `ocrd bashlib filename` command, which is used in CD
#          scripts to get the `share` directory of the core installation. 

import click
from ocrd.constants import BASHLIB_FILENAME

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

