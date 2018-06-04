import click

from ocrd.constants import BASHLIB_FILENAME

# ----------------------------------------------------------------------
# ocrd bashlib
# ----------------------------------------------------------------------

@click.command('bashlib')
def bashlib_cli():
    """
    Dump the bash library for sourcing by shell scripts
    """
    print(BASHLIB_FILENAME)
