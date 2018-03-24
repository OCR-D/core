#  from pprint import pprint

import base as unittest
from base import PWD
from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesseract3 import Tesseract3LineSegmenter

METS_URL = 'file://' + PWD + '/assets/herold/mets.xml'

class TestProcessorSegmentLineTesseract3(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_URL)
        workspace.download_files_in_group('INPUT')
        Tesseract3RegionSegmenter(workspace, inputGrp="INPUT", outputGrp="OCR-D-SEG-BLOCK").process()
        workspace.save_mets()
        Tesseract3LineSegmenter(workspace, inputGrp="OCR-D-SEG-BLOCK", outputGrp="OCR-D-SEG-LINE").process()

if __name__ == '__main__':
    unittest.main()
