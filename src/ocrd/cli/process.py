"""
OCR-D CLI: running task sequences (workflow processing)

.. click:: ocrd.cli.process:process_cli
    :prog: ocrd process
    :nested: full

"""
import click

from ocrd_utils import getLogger, initLogging, DEFAULT_METS_BASENAME
from ocrd.task_sequence import run_tasks

from ..decorators import ocrd_loglevel

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------
@click.command('process')
@ocrd_loglevel
@click.option('-m', '--mets', help="METS to process", default=DEFAULT_METS_BASENAME)
@click.option('-U', '--mets-server-url', help="TCP host URI or UDS path of METS server")
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.option('--overwrite', is_flag=True, default=False, help="Remove output pages/images if they already exist")
@click.argument('tasks', nargs=-1, required=True)
def process_cli(log_level, mets, mets_server_url, page_id, tasks, overwrite):
    """
    Process a series of tasks
    """
    initLogging()
    log = getLogger('ocrd.cli.process')
    run_tasks(mets, log_level, page_id, tasks, overwrite=overwrite, mets_server_url=mets_server_url)
    log.info("Finished")
