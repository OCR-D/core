# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,line-too-long

from tests.base import TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from ocrd import Resolver, Workspace
from ocrd.processor.base import run_processor
from ocrd.cli.dummy_processor import DummyProcessor

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
            self.assertEqual(len(output_files), 3)
            self.assertEqual(len(workspace.mets.find_files(ID='//COPY_OF.*')), 3)

if __name__ == "__main__":
    main()
