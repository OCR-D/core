import click
from ocrd_utils.logging import setOverrideLogLevel

__all__ = ['loglevel_option', 'ocrd_loglevel']

def _set_root_logger_version(ctx, param, value):    # pylint: disable=unused-argument
    setOverrideLogLevel(value)
    return value

loglevel_option = click.option('-l', '--log-level', help="Log level",
                               type=click.Choice([
                                   'OFF', 'ERROR', 'WARN',
                                   'INFO', 'DEBUG', 'TRACE'
                               ]),
                               default=None, callback=_set_root_logger_version)

def ocrd_loglevel(f):
    """
    Add an option '--log-level' to set the log level.
    """
    loglevel_option(f)
    return f
