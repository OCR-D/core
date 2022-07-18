"""
CLI for task_sequence
"""
import sys
import os
import json
import subprocess
import click
import requests

from ocrd_utils import getLogger, initLogging

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
@click.option('-t', '--timeout', help="maximum processing time (in sec per page) before reloading worker (0 to disable)", default=0)
@click.option('-j', '--processes', help="number of parallel workers to spawn", default=1)
@click.option('-h', '--host', help="host name/IP to listen at", default='127.0.0.1')
@click.option('-p', '--port', help="TCP port to listen at", default=5000, type=click.IntRange(min=1024))
@click.argument('tasks', nargs=-1, required=True)
def server_cli(log_level, timeout, processes, host, port, tasks):
    """
    Start server for a series of tasks to run processor CLIs or APIs on workspaces

    Parse the given tasks and try to instantiate all Pythonic
    processors among them with the given parameters.
    Open a web server that listens on the given ``host`` and ``port``
    and queues requests into ``processes`` worker processes
    for GET requests named ``/process`` with the following
    (URL-encoded) arguments:

        mets (string): Path name (relative to the server's CWD,
                       or absolute) of the workspace to process

        page_id (string): Comma-separated list of page IDs to process

        log_level (int): Override all logger levels during processing

        overwrite (bool): Remove output pages/images if they already exist

    The server will handle each request by running the tasks
    on the given workspace. Pythonic processors will be run via API
    (on those same instances).  Non-Pythonic processors (or those
    not directly accessible in the current venv) will be run via CLI
    normally, instantiating each time.
    Also, between each contiguous chain of Pythonic tasks in the overall
    series, no METS de/serialization will be performed.

    If processing does not finish before ``timeout`` seconds per page,
    then the request will fail and the respective worker be reloaded.

    To see the server's workflow configuration, send a GET request named
    ``/list-tasks``.

    Stop the server by sending SIGINT (e.g. via ctrl+c
    on the terminal), or sending a GET request named ``/shutdown``.
    """
    log = getLogger('ocrd.workflow.server')
    log.debug("Running server with %d workers on http://%s:%d", processes, host, port)
    result = subprocess.run(["uwsgi", "--http-socket", "%s:%d" % (host, port),
                             "--wsgi-file", os.path.join(os.path.dirname(__file__), 'server.py'),
                             "--callable", "app", "--need-app",
                             # "--disable-logging", # OCR-D logging is enough
                             # "--http-keepalive", "true",
                             # "--add-header", "Connection: Keep-Alive",
                             "--processes", "%d" % processes,
                             "--master", "--single-interpreter",
                             # "--daemonize2", # return from workflow CLI
                             "--lazy-apps", # fork before loading app
                             "--no-orphans", # kill workers if master dies
                             "--die-on-term", # do not reload on SIGTERM
                             "--reload-on-exception", # reload failed workers
                             "--enable-threads", # for multithreading in Numpy, TF, ...
                             "--cache2", "name=workspace_lock,items=100",
                             # wrap in JSON to retain list/quotes (not possible with pyargv):
                             "--set", "tasks=%s" % json.dumps(tasks),
                             # server log level:
                             "--set", "loglevel=%s" % (log_level or ''),
                             # worker timeout per page:
                             "--set", "timeout_per_page=%d" % timeout,
                             "--buffer-size", "102400"])
    return result.returncode

# ----------------------------------------------------------------------
# ocrd workflow client
# ----------------------------------------------------------------------
@workflow_cli.group('client')
@click.option('-h', '--host', help="host name/IP to request from", default='127.0.0.1')
@click.option('-p', '--port', help="TCP port to request from", default=5000, type=click.IntRange(min=1024))
@click.pass_context
def client_cli(ctx, host, port):
    """
    Have the workflow server run commands
    """
    url = 'http://' + host + ':' + str(port) + '/'
    ctx.ensure_object(dict)
    ctx.obj['URL'] = url
    ctx.obj['log'] = getLogger('ocrd.workflow.client')

@client_cli.command('process')
@ocrd_loglevel
@click.option('-m', '--mets', help="METS to process", default="mets.xml")
@click.option('-g', '--page-id', help="ID(s) of the pages to process")
@click.option('--overwrite', is_flag=True, default=False, help="Remove output pages/images if they already exist")
@click.pass_context
def client_process_cli(ctx, log_level, mets, page_id, overwrite):
    """
    Have the workflow server process another workspace
    """
    url = ctx.obj['URL'] + 'process'
    params = {'mets': mets,
              'page_id': page_id,
              'log_level': log_level,
              'overwrite': str(overwrite)
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print(response.text)
        if response.text == 'Finished':
            sys.exit(0)
        else:
            sys.exit(1)
    except requests.exceptions.HTTPError as err:
        ctx.obj['log'].error("Server error: %s", err.response.text)
    except requests.exceptions.ConnectionError as err:
        ctx.obj['log'].error("Connection error: %s", err)
    except requests.exceptions.Timeout as err:
        ctx.obj['log'].error("Timeout error: %s", err)
    except requests.exceptions.RequestException as err:
        ctx.obj['log'].error("Unknown error: %s", err)
    sys.exit(2)

@client_cli.command('list-tasks')
@click.pass_context
def client_list_tasks_cli(ctx):
    """
    Have the workflow server print the configured task sequence
    """
    url = ctx.obj['URL'] + 'list-tasks'
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(response.text)
        sys.exit(0)
    except requests.exceptions.HTTPError as err:
        ctx.obj['log'].error("Server error: %s", err.response.text)
    except requests.exceptions.ConnectionError as err:
        ctx.obj['log'].error("Connection error: %s", err)
    except requests.exceptions.Timeout as err:
        ctx.obj['log'].error("Timeout error: %s", err)
    except requests.exceptions.RequestException as err:
        ctx.obj['log'].error("Unknown error: %s", err)
    sys.exit(2)

@client_cli.command('shutdown')
@click.pass_context
def client_shutdown_cli(ctx):
    """
    Have the workflow server shutdown gracefully
    """
    url = ctx.obj['URL'] + 'shutdown'
    try:
        response = requests.get(url)
        print(response.text)
        sys.exit(0)
    except requests.exceptions.HTTPError as err:
        ctx.obj['log'].error("Server error: %s", err.response.text)
    except requests.exceptions.ConnectionError as err:
        ctx.obj['log'].error("Connection error: %s", err)
    except requests.exceptions.Timeout as err:
        ctx.obj['log'].error("Timeout error: %s", err)
    except requests.exceptions.RequestException as err:
        ctx.obj['log'].error("Unknown error: %s", err)
    sys.exit(2)

