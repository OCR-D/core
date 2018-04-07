from ocrd.resolver import Resolver
from ocrd.processor.segment_region.tesserocr import Tesseract3RegionSegmenter

from test.base import TestCase, main, assets
METS_HEROLD_SMALL = assets.url_of('SBB0000F29300010000/mets_one_file.xml')

class TestProcessorSegmentRegionTesseract3(TestCase):

    def runTest(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.workspace_from_url(METS_HEROLD_SMALL)
        Tesseract3RegionSegmenter(workspace).process()
        workspace.save_mets()

if __name__ == '__main__':
    main()
