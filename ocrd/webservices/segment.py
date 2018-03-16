from __future__ import absolute_import

import os

import xml.dom.minidom as md

from lxml import etree as ET

from flask import Flask
from flask import request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(["xml"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_page_segmentation_ws(initializer,page_segmenter):
    ws = Flask(__name__)
    ws.config['UPLOAD_FOLDER'] = initializer.working_dir

    @ws.route('/result/<filename>')
    def result(filename):
        return send_from_directory(ws.config['UPLOAD_FOLDER'],
                               filename, as_attachment=False, mimetype="text/xml")

    @ws.route('/ps/', methods=['GET', 'POST'])
    def index():
        """
        Main method of the webservice
        """
        if request.method == 'POST':

            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            mets_file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if mets_file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if mets_file and allowed_file(mets_file.filename):
                filename = secure_filename(mets_file.filename)
                mets_file.save(os.path.join(ws.config['UPLOAD_FOLDER'], filename))

                # real functionality
                initializer.load(os.path.join(ws.config['UPLOAD_FOLDER'], filename))
                initializer.initialize()
                page_segmenter.set_handle(initializer.get_handle())
                page_segmenter.segment()

                return redirect(url_for('result',
                                    filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''
            
    return ws

