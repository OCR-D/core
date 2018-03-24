#  from pprint import pprint

import base as unittest
from assets import METS_HEROLD_SMALL, METS_HEROLD
from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter

class TestProcessorSegmentRegionTesseract3(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD_SMALL)
        Tesseract3RegionSegmenter(workspace).process()
        workspace.save_mets()

if __name__ == '__main__':
    unittest.main()
