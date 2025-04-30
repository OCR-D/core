# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,line-too-long

from io import BytesIO
import os

from PIL import Image

from tests.base import TestCase, assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from ocrd import Resolver, Workspace
from ocrd_utils import MIMETYPE_PAGE, pushd_popd
from ocrd_modelfactory import page_from_file
from ocrd.processor.base import run_processor
from ocrd.processor.builtin.dummy_processor import DummyProcessor

class TestDummyProcessor(TestCase):

    def test_copies_ok(self):
        with copy_of_directory(assets.url_of('SBB0000F29300010000/data')) as wsdir:
            workspace = Workspace(Resolver(), wsdir)
            os.chdir(workspace.directory)
            input_files = workspace.mets.find_all_files(fileGrp='OCR-D-IMG')
            self.assertEqual(len(input_files), 3)
            output_files = workspace.mets.find_all_files(fileGrp='OUTPUT')
            self.assertEqual(len(output_files), 0)
            run_processor(
                DummyProcessor,
                input_file_grp='OCR-D-IMG',
                output_file_grp='OUTPUT',
                parameter={'copy_files': True},
                workspace=workspace
            )
            output_files = workspace.mets.find_all_files(fileGrp='OUTPUT')
            output_files.sort(key=lambda x: x.url)
            assert output_files[0].local_filename == 'OUTPUT/OUTPUT_PHYS_0001.tif'
            assert output_files[1].local_filename == 'OUTPUT/OUTPUT_PHYS_0001_PAGE.xml'
            self.assertEqual(page_from_file(output_files[1]).pcGtsId, output_files[1].ID)
            assert page_from_file(output_files[1]).get_Page().imageFilename == str(output_files[0].local_filename)
            self.assertEqual(len(output_files), 6)
            self.assertEqual(len(workspace.mets.find_all_files(ID='//OUTPUT.*')), 6)
            self.assertEqual(len(workspace.mets.find_all_files(ID='//OUTPUT.*_PAGE')), 3)
            self.assertEqual(len(workspace.mets.find_all_files(fileGrp='OUTPUT', mimetype=MIMETYPE_PAGE)), 3)
            run_processor(
                DummyProcessor,
                input_file_grp='OUTPUT',
                output_file_grp='OUTPUT2',
                parameter={'copy_files': True},
                workspace=workspace
            )
            output2_files = workspace.mets.find_all_files(fileGrp='OUTPUT2')
            output2_files.sort(key=lambda x: x.url)
            self.assertEqual(len(output2_files), 3)

def test_copy_file_false(tmpdir):
    workspace = Resolver().workspace_from_nothing(directory=tmpdir)
    os.chdir(workspace.directory)
    for i in range(10):
        pil_image = Image.new('RGB', (100, 100))
        bhandle = BytesIO()
        pil_image.save(bhandle, format='PNG')
        workspace.add_file(
            'IMG',
            file_id=f'IMG_{i}',
            mimetype='image/png',
            page_id=f'PHYS_{i}',
            local_filename=f'IMG/IMG_{i}.png',
            content=bhandle.getvalue(),
        )
    assert len(workspace.mets.find_all_files(fileGrp='IMG')) == 10
    run_processor(
        DummyProcessor,
        workspace=workspace,
        input_file_grp='IMG',
        output_file_grp='OUTPUT',
        parameter={'copy_files': False},
    )
    assert len(workspace.mets.find_all_files()) == 20, 'We expect 10 PAGE files for the 10 image files'
    page_img0 = next(workspace.mets.find_files(pageId='PHYS_0', fileGrp='OUTPUT'))
    pcgts = page_from_file(workspace.download_file(page_img0))
    assert pcgts.get_Page().imageWidth == 100, 'image is 100 pix wide'
    assert pcgts.get_Page().imageHeight == 100, 'image is 100 pix long'
    assert pcgts.get_Page().imageFilename == 'IMG/IMG_0.png', 'imageFilename references the original img path'

if __name__ == "__main__":
    main(__file__)
