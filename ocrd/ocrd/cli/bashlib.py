from __future__ import print_function
import sys
import click

from ocrd.constants import BASHLIB_FILENAME
import ocrd.constants
import ocrd_utils.constants
import ocrd_models.constants
import ocrd_validators.constants

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
