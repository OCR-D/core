from flask import Flask
from flask import request

from ocrd.processor.base import run_processor
#  from ocrd.processor.segment_line.tesserocr import Tesseract3LineSegmenter
#  from ocrd.processor.segment_region.tesserocr import Tesseract3RegionSegmenter
from ocrd.resolver import Resolver

resolver = Resolver()

def create():
    app = Flask(__name__)

    #  @app.route('/processor/segment_line/tesserocr', methods=['PUT'])
    #  def _segment_line_tesserocr():
    #      run_processor(Tesseract3LineSegmenter, request.args['mets_url'], resolver)
    #      return 'DONE', 200

    #  @app.route('/processor/segment_region/tesserocr', methods=['PUT'])
    #  def _segment_region_tesserocr():
    #      run_processor(Tesseract3RegionSegmenter, request.args['mets_url'], resolver)
    #      return 'DONE', 200

    return app
