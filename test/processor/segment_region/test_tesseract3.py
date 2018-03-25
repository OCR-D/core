#  from pprint import pprint

from test.base import TestCase, main
from test.assets import METS_HEROLD_SMALL
from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesseract3 import Tesseract3RegionSegmenter

class TestProcessorSegmentRegionTesseract3(TestCase):

    def runTest(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD_SMALL)
        Tesseract3RegionSegmenter(workspace).process()
        workspace.save_mets()

if __name__ == '__main__':
    main()
