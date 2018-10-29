from test.base import TestCase, assets, main # pylint: disable=import-error,no-name-in-module
from ocrd.resolver import Resolver
from ocrd_models.validator import WorkspaceValidator

class TestWorkspaceValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()

    def runTest(self):
        report = WorkspaceValidator.validate_url(self.resolver, assets.url_of('SBB0000F29300010000/mets_one_file.xml'))
        print(report.to_xml())

if __name__ == '__main__':
    main()
