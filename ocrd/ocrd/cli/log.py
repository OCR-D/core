"""
Logging CLI
"""
import click
from ocrd_utils import initLogging, getLogger, getLevelName
import logging

class LogCtx():

    def __init__(self, name):
        self.name = name

    def log(self, lvl, *args, **kwargs):
        logger = getLogger(self.name)
        logger.log(getLevelName(lvl), *args, **kwargs)

pass_log = click.make_pass_decorator(LogCtx)

@click.group("log")
@click.option('-n', '--name', envvar='OCRD_TOOL_NAME', default='', metavar='LOGGER_NAME', help='Name of the logger', show_default=True)
@click.pass_context
def log_cli(ctx, name, *args, **kwargs):
    """
    Logging
    """
    initLogging()
    ctx.obj = LogCtx(name)

def _bind_log_command(lvl):
    @click.argument('msgs', nargs=-1)
    @pass_log
    def _log_wrapper(ctx, msgs):
        if not msgs:
            ctx.log(lvl.upper(), '')
        else:
            msg = list(msgs) if '%s' in msgs[0] else ' '.join([x.replace('%', '%%') for x in msgs])
            ctx.log(lvl.upper(), msg)
    return _log_wrapper

for _lvl in ['trace', 'debug', 'info', 'warning', 'error', 'critical']:
    log_cli.command(_lvl, help="Log a %s message" % _lvl.upper())(_bind_log_command(_lvl))
