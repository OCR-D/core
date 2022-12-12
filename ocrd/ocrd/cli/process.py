"""
OCR-D CLI: running task sequences (workflow processing)

.. click:: ocrd.cli.process:process_cli
    :prog: ocrd process
    :nested: full

"""
import click

from ocrd_utils import getLogger, initLogging
from ocrd.task_sequence import run_tasks

from ..decorators import ocrd_loglevel

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------
@click.command('process')
@ocrd_loglevel
@click.option('-m', '--mets', help="METS to process", default="mets.xml")
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.option('--overwrite', is_flag=True, default=False, help="Remove output pages/images if they already exist")
@click.argument('tasks', nargs=-1, required=True)
def process_cli(log_level, mets, page_id, tasks, overwrite):
    """
    Process a series of tasks
    """
    initLogging()
    log = getLogger('ocrd.cli.process')
    run_tasks(mets, log_level, page_id, tasks, overwrite)
    log.info("Finished")
