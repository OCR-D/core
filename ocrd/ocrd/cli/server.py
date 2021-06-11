"""
Flask application for uwsgi workflow server

(This is not meant to be imported directly, but loaded from uwsgi.)
"""
import os
import signal
import json
import flask
import uwsgi # added to module path by uwsgi runner

from ocrd_utils import getLogger, initLogging
from ocrd.task_sequence import run_tasks, parse_tasks
from ocrd.resolver import Resolver

initLogging()
# unwrap user-defined workflow:
tasks = json.loads(uwsgi.opt["tasks"])
loglevel = uwsgi.opt["loglevel"].decode()
timeout_per_page = int(uwsgi.opt["timeout_per_page"])
res = Resolver()
app = flask.Flask(__name__)
log = getLogger('ocrd.workflow.server')
if loglevel:
    log.setLevel(loglevel)

def setup():
    global tasks
    if "CUDA_WORKERS" in os.environ and uwsgi.worker_id() > int(os.environ["CUDA_WORKERS"]):
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        where = "CPU"
    else:
        where = "GPU"
    log.info("Parsing and instantiating %d tasks (on %s)", len(tasks), where)
    tasks = parse_tasks(tasks) # raises exception if invalid (causing worker to exit)
    for task in tasks:
        task.instantiate() # returns False if impossible (causing CLI fallback below)

@app.route('/process')
def process(): # pylint: disable=unused-variable
    log.debug("Processing request: %s", str(flask.request))
    if flask.request.args.get("mets"):
        mets = flask.request.args["mets"]
    else:
        return 'Error: No METS', 400
    if flask.request.args.get('page_id'):
        page_id = flask.request.args["page_id"]
    else:
        page_id = ''
    if flask.request.args.get('log_level'):
        log_level = flask.request.args["log_level"]
    else:
        log_level = None
    if flask.request.args.get('overwrite'):
        overwrite = flask.request.args["overwrite"] in ["True", "true", "1"]
    else:
        overwrite = False
    try:
        if page_id:
            npages = len(page_id.split(','))
        else:
            workspace = res.workspace_from_url(mets)
            npages = len(workspace.mets.physical_pages)
        timeout = timeout_per_page * npages
        log.info("Processing %d tasks on %d pages (timeout=%ds)", len(tasks), npages, timeout)
        # FIXME: prevent multiple concurrent requests to the same workspace/METS
        # (use internal routing rules to prevent that, perhaps send 503 or just push to backlog)
        # allow no more than timeout_per_page before restarting worker:
        uwsgi.set_user_harakiri(timeout) # go, go, go!
        # run the workflow
        run_tasks(mets, log_level, page_id, tasks, overwrite)
        uwsgi.set_user_harakiri(0) # take a breath!
    except Exception as e:
        log.exception("Request '%s' failed", str(flask.request.args))
        return 'Failed: %s' % str(e), 500
    return 'Finished'

@app.route('/list-tasks')
def list_tasks(): # pylint: disable=unused-variable
    seq = ''
    for task in tasks:
        seq += '\n' + str(task)
    return seq
@app.route('/shutdown')
def shutdown(): # pylint: disable=unused-variable
    log.debug("Shutting down")
    # does not work ("error managing signal 2 on worker 1"):
    # uwsgi.signal(signal.SIGINT)
    os.kill(uwsgi.masterpid(), signal.SIGINT)
    return 'Stopped'

setup()
