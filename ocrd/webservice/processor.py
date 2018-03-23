from flask import Flask
from flask import request

from ocrd.processor.base import run_processor
from ocrd.processor.characterize.exif import ExifProcessor
from ocrd.processor.segment_line.tesseract3 import Tesseract3LineSegmenter
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter
from ocrd.resolver import Resolver

resolver = Resolver(cache_enabled=True)

def create():
    app = Flask(__name__)

    @app.route('/processor/characterize/exif', methods=['PUT'])
    def _characterize_exif():
        run_processor(ExifProcessor, request.args['mets_url'], resolver)
        return 'DONE', 200

    @app.route('/processor/segment_line/tesseract3', methods=['PUT'])
    def _segment_line_tesseract3():
        run_processor(Tesseract3LineSegmenter, request.args['mets_url'], resolver)
        return 'DONE', 200

    @app.route('/processor/segment_region/tesseract3', methods=['PUT'])
    def _segment_region_tesseract3():
        run_processor(Tesseract3RegionSegmenter, request.args['mets_url'], resolver)
        return 'DONE', 200

    return app
