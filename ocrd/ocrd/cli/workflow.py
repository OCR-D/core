"""
CLI for task_sequence
"""
import click
import flask

from ocrd_utils import getLogger, initLogging
from ocrd.task_sequence import run_tasks, parse_tasks

from ..decorators import ocrd_loglevel
from .process import process_cli

@click.group("workflow")
def workflow_cli():
    """
    Process a series of tasks
    """
    initLogging()

# ----------------------------------------------------------------------
# ocrd workflow process
# ----------------------------------------------------------------------
@workflow_cli.command('process')
@ocrd_loglevel
@click.option('-m', '--mets', help="METS to process", default="mets.xml")
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.option('--overwrite', is_flag=True, default=False, help="Remove output pages/images if they already exist")
@click.argument('tasks', nargs=-1, required=True)
def process_cli_alias(log_level, mets, page_id, tasks, overwrite):
    """
    Run processor CLIs in a series of tasks

    (alias for ``ocrd process``)
    """
    process_cli(log_level, mets, page_id, tasks, overwrite)

# ----------------------------------------------------------------------
# ocrd workflow server
# ----------------------------------------------------------------------
@workflow_cli.command('server')
@ocrd_loglevel
@click.option('-h', '--host', help="host name/IP to listen at", default='127.0.0.1')
@click.option('-p', '--port', help="TCP port to listen at", default=5000, type=click.IntRange(min=1024))
@click.argument('tasks', nargs=-1, required=True)
def server_cli(log_level, host, port, tasks):
    """
    Start server for a series of tasks to run processor CLIs or APIs on workspaces

    Parse the given tasks and try to instantiate all Pythonic
    processors among them with the given parameters.
    Open a web server that listens on the given host and port
    for GET requests named ``process`` with the following
    (URL-encoded) arguments:

        mets (string): Path name (relative to the server's CWD,
                       or absolute) of the workspace to process

        page_id (string): Comma-separated list of page IDs to process

        overwrite (bool): Remove output pages/images if they already exist

    The server will handle each request by running the tasks
    on the given workspace. Pythonic processors will be run via API
    (on those same instances).  Non-Pythonic processors (or those
    not directly accessible in the current venv) will be run via CLI
    normally, instantiating each time.
    Also, between each contiguous chain of Pythonic tasks in the overall
    series, no METS de/serialization will be performed.

    Stop the server by sending SIGINT (e.g. via ctrl+c
    on the terminal), or sending a GET request named ``shutdown``.
    """
    log = getLogger('ocrd.workflow.server')
    log.debug("Parsing and instantiating %d tasks", len(tasks))
    tasks = parse_tasks(tasks)
    app = flask.Flask(__name__)
    @app.route('/process')
    def process(): # pylint: disable=unused-variable
        if flask.request.args.get("mets"):
            mets = flask.request.args["mets"]
        else:
            return 'Error: No METS'
        if flask.request.args.get('page_id'):
            page_id = flask.request.args["page_id"]
        else:
            page_id = ''
        if flask.request.args.get('overwrite'):
            overwrite = flask.request.args["overwrite"] in ["True", "true", "1"]
        else:
            overwrite = False
        try:
            run_tasks(mets, log_level, page_id, tasks, overwrite)
        except Exception as e:
            log.exception("Request '%s' failed", str(flask.request.args))
            return 'Failed: %s' % str(e)
        return 'Finished'
    @app.route('/shutdown')
    def shutdown(): # pylint: disable=unused-variable
        fun = flask.request.environ.get('werkzeug.server.shutdown')
        if fun is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        fun()
    log.debug("Running server on http://%s:%d", host, port)
    app.run(host=host, port=port)
