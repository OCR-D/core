"""
Flask application and gunicorn processing server for Processor
"""
import os
import signal
import multiprocessing as mp
import atexit
import json
import flask
import gunicorn.app.base

from ocrd_validators import WorkspaceValidator
from ocrd_utils import getLogger
from ocrd.task_sequence import ProcessorTask
from .processor import run_api
from . import Resolver

class ProcessingServer(gunicorn.app.base.BaseApplication):

    def __init__(self, processorClass, processorArgs, options=None):
        # happens in pre-fork context
        self.options = options or {'bind': '127.0.0.1:5000', 'workers': 1}
        # TODOs:
        # - add 'CUDA_VISIBLE_DEVICES' to 'raw_env' to options (server level instead of worker level)
        # - customize 'errorlog' (over stdout) in options
        # - customize 'accesslog' (over None) in options
        self.options['accesslog'] = '-'
        self.options['access_log_format'] = '%(t)s "%(r)s" %(s)s %(b)s "%(T)s"'
        # - customize 'logger_class' in options
        # - customize 'logconfig' or 'logconfig_dict' in options
        # - customize 'access_log_format' in options
        self.options['timeout'] = 0 # disable (timeout managed by workers on request level)
        self.options['preload_app'] = False # instantiate workers independently
        self.options['pre_fork'] = pre_fork # see below
        self.options['post_fork'] = post_fork # see below
        self.options['pre_request'] = pre_request # see below
        self.options['post_request'] = post_request # see below
        self.options['worker_abort'] = worker_abort # see below
        self.processor_cls = processorClass
        self.processor_opt = processorArgs
        self.master_pid = os.getpid()
        manager = mp.Manager()
        self.master_lock = manager.Lock()
        self.master_cache = manager.dict()
        # (Manager creates an additional mp.Process on __enter__,
        #  and registers an atexit handler joining that in __exit__,
        #  but our forked workers inherit this. To prevent attempting
        #  to join a non-child, we need to remove that in post_fork.)
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        # happens in (forked) worker context (because preload_app=False)
        # instantiate
        self.obj = self.processor_cls(None, **self.processor_opt)
        self.exe = self.obj.ocrd_tool['executable']
        self.res = Resolver()
        self.log = getLogger('ocrd.processor.server')
        self.app = flask.Flask(self.exe)
        # add routes
        self.app.add_url_rule('/process', None, self.process)
        self.app.add_url_rule('/list-tasks', None, self.list_tasks)
        self.app.add_url_rule('/shutdown', None, self.shutdown)
        return self.app

    def process(self):
        self.log.debug("Processing request: %s", str(flask.request))
        if flask.request.args.get("mets"):
            mets = flask.request.args["mets"]
        else:
            return 'Error: No METS', 400
        # prevent multiple concurrent requests to the same workspace/METS
        if not self.lock(mets):
            return 'Error: Locked METS', 423
        if flask.request.args.get('page_id'):
            page_id = flask.request.args["page_id"]
        else:
            page_id = ''
        # if flask.request.args.get('log_level'):
        #     log_level = flask.request.args["log_level"]
        # else:
        #     log_level = None
        if flask.request.args.get('overwrite'):
            overwrite = flask.request.args["overwrite"] in ["True", "true", "1"]
        else:
            overwrite = False
        try:
            workspace = self.res.workspace_from_url(mets)
            workspace.overwrite_mode = overwrite
            report = WorkspaceValidator.check_file_grp(
                workspace,
                self.obj.input_file_grp,
                '' if overwrite else self.obj.output_file_grp,
                page_id)
            if not report.is_valid:
                raise Exception("Invalid input/output file grps:\n\t%s" % '\n\t'.join(report.errors))
            if page_id:
                npages = len(page_id.split(','))
            else:
                npages = len(workspace.mets.physical_pages)
            # allow no more than page_timeout before restarting worker:
            timeout = getattr(self.obj, 'page_timeout', 0)
            timeout *= npages
            self.log.info("Processing %s on %d pages of '%s' (timeout=%ds)", self.exe, npages, mets, timeout)
            with Timeout(timeout, "processing %s on %s cancelled after %d seconds on %d pages" % (
                    self.exe, mets, timeout, npages)):
                # run the workflow
                error = run_api(self.obj, workspace, page_id)
                if error:
                    raise error
                workspace.save_mets()
        except Exception as e:
            self.log.exception("Request '%s' failed", str(flask.request.args))
            self.unlock(mets)
            return 'Failed: %s' % str(e), 500
        self.unlock(mets)
        return 'Finished'

    def list_tasks(self):
        task = ProcessorTask(self.exe, [self.obj.input_file_grp], [self.obj.output_file_grp], self.obj.parameter)
        return str(task) + '\n'

    def shutdown(self):
        self.log.debug("Shutting down")
        os.kill(self.master_pid, signal.SIGTERM)
        return 'Stopped'

    def lock(self, resource):
        with self.master_lock:
            if resource in self.master_cache:
                return False
            self.master_cache[resource] = True
        return True
    def unlock(self, resource):
        with self.master_lock:
            del self.master_cache[resource]

class Timeout:
    def __init__(self, seconds, message):
        self.seconds = seconds
        self.message = message
    def _handler(self, signum, stack):
        raise TimeoutError(self.message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.seconds)
    def __exit__(self, *args):
        signal.alarm(0)
    
def pre_fork(server, worker):
    # happens when worker (but not app/processor) was instantiated (but not forked yet)
    worker.num_workers = server.num_workers # nominal value
    worker.worker_id = len(server.WORKERS) + 1 # actual value

def post_fork(server, worker):
    # happens when worker (but not app/processor) was was instantiated (and forked)
    # remove atexit handler for multiprocessing.Manager process
    atexit.unregister(mp.util._exit_function)
    # differentiate GPU workers from CPU workers via envvar
    if "CUDA_WORKERS" in os.environ:
        cuda_workers = int(os.environ["CUDA_WORKERS"])
        assert cuda_workers <= worker.num_workers, \
            "CUDA_WORKERS[%d] <= workers[%d] violated" % (cuda_workers, worker.num_workers)
    else:
        cuda_workers = worker.num_workers
    if worker.worker_id > cuda_workers:
        worker.log.debug("Setup for worker %d (non-CUDA)", worker.worker_id)
        os.environ["CUDA_VISIBLE_DEVICES"] = "" # avoid GPU
    else:
        worker.log.debug("Setup for worker %d (normal)", worker.worker_id)

def pre_request(worker, req):
    worker.log.debug("%s %s at worker %d" % (req.method, req.path, worker.worker_id))

def post_request(worker, req, env, res):
    worker.log.debug("%s %s at worker %d: %s" % (req.method, req.path, worker.worker_id, res))

def worker_abort(worker):
    worker.log.debug("aborting worker %s", worker)
    # FIXME: skip/fallback remaining pages, save_mets, signalling ...
    # worker.app.obj.clean_up()
