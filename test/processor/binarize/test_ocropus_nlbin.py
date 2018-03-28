from test.base import TestCase, main
from test.assets import METS_HEROLD
from ocrd.resolver import Resolver
from ocrd.processor.ocropus_nlbin import OcropusNlbinBinarizer

class OcropusNlbinBinarizer(TestCase):

    def runTest(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD)
        # TODO
        #  workspace.download_all_inputs()
        processor = ExifProcessor(workspace)
        processor.verify()
        processor.process()
        #  workspace.upload_all_outputs()
        #  print(workspace)
        #  mets = OcrdMets(filename=METS_URL)
        #  print(mets.files_in_group('INPUT')[0])

if __name__ == '__main__':
    main()
