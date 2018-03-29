import os
import shutil

from test.base import TestCase, main
from test.assets import METS_HEROLD_SMALL
from ocrd.resolver import Resolver
from ocrd.processor.binarize.ocropus_nlbin import OcropusNlbinBinarizer

WORKSPACE_DIR = '/tmp/pyocrd-test-ocropus-nlbin'

class OcropusNlbinBinarizerTest(TestCase):

    def setUp(self):
        if os.path.exists(WORKSPACE_DIR):
            shutil.rmtree(WORKSPACE_DIR)
        os.makedirs(WORKSPACE_DIR)

    def runTest(self):
        resolver = Resolver(cache_enabled=True)
        workspace = resolver.create_workspace(METS_HEROLD_SMALL, directory=WORKSPACE_DIR)
        processor = OcropusNlbinBinarizer(workspace)
        processor.process()
        workspace.save_mets()

if __name__ == '__main__':
    main()
