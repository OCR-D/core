#  from pprint import pprint

import base as unittest
from base import PWD
from ocrd.resolver import Resolver
from ocrd.processor.characterize.exif import ExifProcessor

METS_URL = 'file://' + PWD + '/assets/herold/mets.xml'

class TestProcessorExif(unittest.TestCase):

    def test_basic(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_URL)
        workspace.download_all_inputs()
        processor = ExifProcessor(workspace)
        processor.verify()
        processor.process()
        #  workspace.upload_all_outputs()
        #  print(workspace)
        #  mets = OcrdMets(filename=METS_URL)
        #  print(mets.files_in_group('INPUT')[0])

if __name__ == '__main__':
    unittest.main()
