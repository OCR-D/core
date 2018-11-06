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
        workspace = Workspace(self.resolver, directory=assets.url_of('SBB0000F29300010000'))
        ocrdzip = self.bagger.bag(workspace, 'SBB0000F29300010000', ocrd_manifestation_depth='partial')
        validator = OcrdZipValidator(self.resolver, ocrdzip)
        validator.validate()

    #  def test_something(self):
        #  report = OcrdZipValidator.validate_json(json.loads(skeleton))
        #  #  print(report.to_xml())
        #  self.assertEqual(report.is_valid, True)

    #  def test_file_param_ok(self):
        #  ocrd_zip = json.loads(skeleton)
        #  ocrd_zip['zips']['ocrd-xyz']['parameters'] = {"file-param": {"description": "...", "type": "string", "content-type": 'application/rdf+xml'}}
        #  report = OcrdZipValidator.validate_json(ocrd_zip)
        #  self.assertEqual(report.is_valid, True)

    #  def test_file_param_bad_content_types(self):
        #  bad_and_why = [
                #  [2, 'Number not string'],
                #  ['foo', 'No subtype'],
                #  ['foo/bar~300', 'Invalid char in subtype'],
                #  ['foo/bar 300', 'Invalid char in subtype'],
        #  ]
        #  for case in bad_and_why:
            #  ocrd_zip = json.loads(skeleton)
            #  ocrd_zip['zips']['ocrd-xyz']['parameters'] = {"file-param": {"description": "...", "type": "string", "content-type": case[0]}}
            #  report = OcrdZipValidator.validate_json(ocrd_zip)
            #  print('# %s: %s' % (case[0], case[1]))
            #  self.assertEqual(report.is_valid, False, case[1])

if __name__ == '__main__':
    main()
