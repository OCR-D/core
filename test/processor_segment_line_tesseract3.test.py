#  from pprint import pprint

from assets import METS_HEROLD_SMALL
import base as unittest
from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter
from ocrd.processor.segment_line.tesseract3 import Tesseract3LineSegmenter

class TestProcessorSegmentLineTesseract3(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD_SMALL)
        Tesseract3RegionSegmenter(workspace, inputGrp="INPUT", outputGrp="OCR-D-SEG-BLOCK").process()
        workspace.save_mets()
        Tesseract3LineSegmenter(workspace, inputGrp="OCR-D-SEG-BLOCK", outputGrp="OCR-D-SEG-LINE").process()
        workspace.save_mets()

if __name__ == '__main__':
    unittest.main()
