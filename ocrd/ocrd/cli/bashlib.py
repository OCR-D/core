from __future__ import print_function
import sys
import click

from ocrd.constants import BASHLIB_FILENAME
import ocrd_utils.constants
import ocrd_models.constants

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
    if name in ['*', 'KEYS', '__all__']:
        for symbol in ocrd_utils.constants.__all__:
            print(symbol)
        for symbol in ocrd_models.constants.__all__:
            print(symbol)
    elif (name in ocrd_utils.constants.__all__ or
          name in ocrd_models.constants.__all__):
        if name in ocrd_utils.constants.__all__:
            constant = ocrd_utils.constants.__dict__[name]
        else:
            constant = ocrd_models.constants.__dict__[name]
        if isinstance(constant, dict):
            # make this bash-friendly (show initialization for associative array)
            for key in constant:
                print("[%s]=%s" % (key, constant[key]), end=' ')
        else:
            print(constant)
    else:
        print("ERROR: name '%s' is not a known constant" % name, file=sys.stderr)
        sys.exit(1)
