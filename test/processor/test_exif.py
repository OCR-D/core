from ocrd.resolver import Resolver
from ocrd.processor.characterize.exif import ExifProcessor

from test.base import TestCase, main, assets

METS_HEROLD = assets.url_of('SBB0000F29300010000/mets.xml')

class TestProcessorExif(TestCase):

    def runTest(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD)
        #  workspace.download_all_inputs()
        processor = ExifProcessor(workspace)
        processor.verify()
        processor.process()
        #  workspace.upload_all_outputs()
        #  print(workspace)
        #  mets = OcrdMets(filename=METS_URL)
        #  print(mets.find_files(fileGrp='INPUT')[0])

if __name__ == '__main__':
    main()
