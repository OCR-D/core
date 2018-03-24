#  from pprint import pprint

import base as unittest
from base import PWD
from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter

METS_URL = 'file://' + PWD + '/assets/herold/mets.xml'

class TestProcessorSegmentRegionTesseract3(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_URL)
        workspace.download_all_inputs()
        processor = Tesseract3RegionSegmenter(workspace)
        processor.verify()
        processor.process()

if __name__ == '__main__':
    unittest.main()
