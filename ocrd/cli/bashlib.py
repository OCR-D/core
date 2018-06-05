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
    """
    print(BASHLIB_FILENAME)
