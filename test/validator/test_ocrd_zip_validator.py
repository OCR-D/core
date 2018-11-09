from test.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module
from ocrd.validator import OcrdZipValidator
from ocrd.workspace import Workspace
from ocrd.workspace_bagger import WorkspaceBagger
from ocrd.resolver import Resolver

class TestOcrdZipValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.bagger = WorkspaceBagger(self.resolver)

    def test_validation(self):
        workspace = Workspace(self.resolver, directory=assets.path_to('SBB0000F29300010000'))
        ocrdzip = self.bagger.bag(workspace, 'SBB0000F29300010000', ocrd_manifestation_depth='partial')
        validator = OcrdZipValidator(self.resolver, ocrdzip)
        report = validator.validate()
        print(report)

if __name__ == '__main__':
    main()
