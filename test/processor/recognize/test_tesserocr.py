import os
import shutil

from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesserocr import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesserocr import Tesseract3LineSegmenter
from ocrd.processor.recognize.tesserocr import Tesseract3Recognizer

from test.assets import METS_HEROLD_SMALL
from test.base import TestCase, skip, main

WORKSPACE_DIR = '/tmp/pyocrd-test-recognizer'

class TestTesseract3Recognizer(TestCase):

    def setUp(self):
        if os.path.exists(WORKSPACE_DIR):
            shutil.rmtree(WORKSPACE_DIR)
        os.makedirs(WORKSPACE_DIR)

    skip("Takes too long")
    def runTest(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD_SMALL, directory=WORKSPACE_DIR)
        Tesseract3RegionSegmenter(workspace, inputGrp="INPUT", outputGrp="OCR-D-SEG-BLOCK").process()
        workspace.save_mets()
        Tesseract3LineSegmenter(workspace, inputGrp="OCR-D-SEG-BLOCK", outputGrp="OCR-D-SEG-LINE").process()
        workspace.save_mets()
        #  TODO takes too long
        Tesseract3Recognizer(workspace, inputGrp="OCR-D-SEG-LINE", outputGrp="OCR-D-OCR-TESS").process()
        workspace.save_mets()

if __name__ == '__main__':
    main()
