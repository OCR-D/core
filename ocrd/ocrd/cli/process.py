"""
CLI for task_sequence
"""
import click

from ocrd_utils import getLogger
from ocrd.task_sequence import run_tasks

from ..decorators import ocrd_loglevel


# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------
@click.command('process')
@ocrd_loglevel
@click.option('-m', '--mets', help="METS to process", required=True)
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.argument('tasks', nargs=-1, required=True)
def process_cli(log_level, mets, page_id, tasks):
    """
    Process a series of tasks
    """
    log = getLogger('ocrd.cli.process')

    run_tasks(mets, log_level, page_id, tasks)
    log.info("Finished")
