from flask import Flask, request
import json
import os
import tempfile
import subprocess
import shutil
from werkzeug.utils import secure_filename

from ocrd import run_executable, TMP_PREFIX

UPLOAD_FOLDER = tempfile.mkdtemp(prefix=TMP_PREFIX)

def create(executable, app=Flask(__name__)):

    if not shutil.which(executable):
        raise Exception("No such command: %s" % executable)

    ocrd_tool = json.loads(subprocess.check_output([executable, '-J']).decode('utf-8'))

    @app.route('/', methods=['GET'])
    def _get_ocrd_tool():
        return json.dumps(ocrd_tool)

    @app.route('/', methods=['POST'])
    def _run_processor():
        if 'mets' not in request.files and 'mets' not in request.form:
            return "Must pass either 'mets' form parameter or send a file 'mets' with form", 400
        elif 'mets' in request.files:
            file = request.files['mets']
            savepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(savepath)
            mets_url = 'file://' + savepath
        else:
            mets_url = request.form.mets
        run_executable(executable, mets_url=mets_url, **request.form)
        return json.dumps(mets_url), 200

    return app

