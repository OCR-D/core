# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,line-too-long

from tests.base import TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from ocrd import Resolver, Workspace
from ocrd_utils import MIMETYPE_PAGE
from ocrd_modelfactory import page_from_file
from ocrd.processor.base import run_processor
from ocrd.processor.builtin.dummy_processor import DummyProcessor

class TestDummyProcessor(TestCase):

    def test_copies_ok(self):
        with copy_of_directory(assets.url_of('SBB0000F29300010000/data')) as wsdir:
            workspace = Workspace(Resolver(), wsdir)
            input_files = workspace.mets.find_files(fileGrp='OCR-D-IMG')
            self.assertEqual(len(input_files), 3)
            output_files = workspace.mets.find_files(fileGrp='OUTPUT')
            self.assertEqual(len(output_files), 0)
            run_processor(
                DummyProcessor,
                input_file_grp='OCR-D-IMG',
                output_file_grp='OUTPUT',
                workspace=workspace
            )
            output_files = workspace.mets.find_files(fileGrp='OUTPUT')
            output_files.sort(key=lambda x: x.url)
            print([str(s) for s in output_files])
            self.assertEqual(output_files[0].url, 'OUTPUT/OUTPUT_0001.tif')
            self.assertEqual(output_files[1].url, 'OUTPUT/OUTPUT_0001.xml')
            self.assertEqual(page_from_file(output_files[1]).pcGtsId, output_files[1].ID)
            self.assertEqual(page_from_file(output_files[1]).get_Page().imageFilename, output_files[0].url)
            self.assertEqual(len(output_files), 6)
            self.assertEqual(len(workspace.mets.find_files(ID='//OUTPUT.*')), 6)
            self.assertEqual(len(workspace.mets.find_files(ID='//OUTPUT.*_PAGE')), 3)
            self.assertEqual(len(workspace.mets.find_files(fileGrp='OUTPUT', mimetype=MIMETYPE_PAGE)), 3)

if __name__ == "__main__":
    main(__file__)
