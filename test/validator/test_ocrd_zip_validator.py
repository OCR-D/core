from test.base import TestCase, main, assets # pylint: disable=import-error,no-name-in-module
from ocrd_models.validator import OcrdZipValidator
from ocrd.workspace import Workspace
from ocrd.workspace_bagger import WorkspaceBagger
from ocrd.resolver import Resolver

class TestOcrdZipValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.bagger = WorkspaceBagger(self.resolver)

    def test_validation(self):
        workspace = Workspace(self.resolver, directory=assets.path_to('SBB0000F29300010000/data'))
        ocrdzip = self.bagger.bag(workspace, 'SBB0000F29300010000', ocrd_manifestation_depth='partial')
        validator = OcrdZipValidator(self.resolver, ocrdzip)
        report = validator.validate()
        self.assertEqual(report.is_valid, True)
        print(report)

    def test_validation_unzipped(self):
        validator = OcrdZipValidator(self.resolver, assets.path_to('kant_aufklaerung_1784'))
        report = validator.validate(skip_unzip=True)
        self.assertEqual(report.is_valid, True)
        print(report)

if __name__ == '__main__':
    main()
