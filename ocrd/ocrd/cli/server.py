"""
Flask application for uwsgi workflow server

(This is not meant to be imported directly, but loaded from uwsgi.)
"""
import base64
import os
import signal
import json
import flask
import uwsgi # added to module path by uwsgi runner

from io import BytesIO
from ocrd_modelfactory import page_from_file
from ocrd_utils import getLogger, initLogging, pushd_popd
from ocrd.task_sequence import run_tasks, parse_tasks
from ocrd.resolver import Resolver
from PIL import Image
from tempfile import TemporaryDirectory


# unwrap user-defined workflow:
tasks = json.loads(uwsgi.opt["tasks"])
loglevel = uwsgi.opt["loglevel"].decode()
timeout_per_page = int(uwsgi.opt["timeout_per_page"])
workers = uwsgi.numproc
where = "GPU" # priority/general worker (i.e. contract worker / wage labourer)
if "CUDA_WORKERS" in os.environ:
    gpu_workers = int(os.environ["CUDA_WORKERS"])
    assert gpu_workers <= workers, \
        "CUDA_WORKERS[%d] <= workers[%d] violated" % (gpu_workers, workers)
else:
    gpu_workers = workers

initLogging()
res = Resolver()
app = flask.Flask(__name__)
log = getLogger('ocrd.workflow.server')
if loglevel:
    log.setLevel(loglevel)

def setup_where():
    global where
    log.debug("Setup for worker %d", uwsgi.worker_id())
    if uwsgi.worker_id() > gpu_workers:
        # avoid GPU
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        where = 'CPU'

def setup():
    global tasks
    setup_where()
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
    # prevent multiple concurrent requests to the same workspace/METS
    if not lock(mets):
        return 'Error: Locked METS', 423
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
        _process(mets, page_id, log_level, overwrite)
    except Exception as e:
        log.exception("Request '%s' failed", str(flask.request.args))
        unlock(mets)
        return 'Failed: %s' % str(e), 500
    unlock(mets)
    return 'Finished'

def _process(mets, page_id='', log_level=None, overwrite=False):
    if page_id:
        npages = len(page_id.split(','))
    else:
        workspace = res.workspace_from_url(mets)
        npages = len(workspace.mets.physical_pages)
    timeout = timeout_per_page * npages
    log.info("Processing %d tasks on %d pages (timeout=%ds)", len(tasks), npages, timeout)
    # allow no more than timeout_per_page before restarting worker:
    uwsgi.set_user_harakiri(timeout) # go, go, go!
    # run the workflow
    run_tasks(mets, log_level, page_id, tasks, overwrite)
    uwsgi.set_user_harakiri(0) # take a breath!

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

def lock(mets):
    uwsgi.lock()
    try:
        log.debug("locking '%s'", mets)
        if uwsgi.cache_exists(mets):
            granted = False
        else:
            uwsgi.cache_set(mets, b'running')
            granted = True
    finally:
        uwsgi.unlock()
    return granted

def unlock(mets):
    uwsgi.lock()
    try:
        log.debug("unlocking '%s'", mets)
        uwsgi.cache_del(mets)
    finally:
        uwsgi.unlock()

@app.route('/process_images', methods=["POST"])
def process_images():  # pylint: disable=undefined-name
    log.debug(f"Processing request: {flask.request}")
    if flask.request.is_json:
        req = flask.request.get_json()

        pages = {}
        if "pages" in req:
            for k, v in req["pages"].items():
                pages[k] = v
        elif "PAGES" in req:
            for k, v in pages["PAGES"].items():
                pages[k] = v
        else:
            return 'Missing "pages" param.', 400

        try:
            work_dir = TemporaryDirectory()
            ws = res.workspace_from_nothing(directory=work_dir.name)

            for k, v in pages.items():
                img = Image.open(BytesIO(base64.b64decode(v)))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                ws.save_image_file(img, k, "OCR-D-IMG", page_id=k, mimetype='image/png')
            ws.save_mets()
            ws.reload_mets()
        except Exception as e:
            work_dir.cleanup()
            return f"An error occured while decoding image(s) and creating mets.xml. {e}", 400

        try:
            _process(ws.mets_target)
            ws.reload_mets()
            for k in pages.keys():
                pages[k] = {"img": None, "page": None}

                page_file = next(ws.mets.find_files(
                    pageId=k,
                    fileGrp=tasks[-1].output_file_grps[0],
                ))
                with pushd_popd(ws.directory):
                    if page_file and os.path.exists(page_file.local_filename):
                        with open(page_file.local_filename, "r", encoding="utf8") as f:
                            pages[k]["page"] = f.read()
                    img_path = page_from_file(
                        page_file
                    ).get_Page().get_AlternativeImage()[-1].get_filename()
                    if img_path and os.path.exists(img_path):
                        img = Image.open(img_path)
                        img_file = BytesIO()
                        img.save(img_file, format="PNG")
                        pages[k]["img"] = base64.b64encode(img_file.getvalue()).decode("utf8")
        except Exception as e:
            return f"Failed: {e}", 500
        finally:
            work_dir.cleanup()

        return flask.json.jsonify(pages)
    else:
        return "Request was not JSON.", 400

setup()
