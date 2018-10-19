import os
import hashlib

from flask import Flask, Response, request, send_from_directory
#  from werkzeug.utils import secure_filename
from ocrd.constants import DEFAULT_UPLOAD_FOLDER, DEFAULT_REPOSITORY_URL

def create(upload_folder=DEFAULT_UPLOAD_FOLDER, base_url=DEFAULT_REPOSITORY_URL):

    if not os.path.isdir(upload_folder):
        os.makedirs(upload_folder)

    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def _post_file():
        """
        Post a file. Name can be overridden with 'Slug'.
        """
        if 'file' not in request.files:
            return 'No file part', 400
        mets_file = request.files['file']
        file_id = request.headers.get('Slug')
        if file_id is None:
            file_id = hashlib.md5(mets_file.read()).hexdigest()
            mets_file.seek(0)
        local_filename = os.path.join(upload_folder, file_id)
        mets_file.save(local_filename)
        resp = Response()
        resp.headers.set('Location', base_url + file_id)
        resp.status_code = 201
        return resp

    @app.route('/<file_id>', methods=['GET'])
    def _get_file(file_id):
        """
        Get an uploaded file
        """
        local_filename = os.path.join(upload_folder, file_id)
        if not os.path.exists(local_filename):
            return 'File not found', 404
        return send_from_directory(upload_folder, file_id, as_attachment=False, mimetype="text/xml")

    return app

if __name__ == '__main__':
    create().run(port=5052)
