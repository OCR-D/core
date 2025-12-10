# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,line-too-long

from tests.base import assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from ocrd import Resolver, Workspace
from ocrd_utils import MIMETYPE_PAGE, pushd_popd, initLogging, disableLogging
from ocrd_modelfactory import page_from_file
from ocrd.processor.base import run_processor
from ocrd.processor.builtin.filter_processor import FilterProcessor

from tests.test_mets_server import fixture_start_mets_server
from tests.processor.test_processor import workspace_kant


def test_filter_none(workspace_kant, caplog):
    caplog.set_level(10)
    workspace = workspace_kant
    input_files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-PAGE')
    input_pcgts0 = page_from_file(input_files[0])
    proc = run_processor(FilterProcessor,
                         workspace=workspace,
                         input_file_grp="OCR-D-GT-PAGE",
                         output_file_grp="OCR-D-OUT",
                         parameter={'select': '//pc:Glyph', 'plot': False})
    assert len(caplog.records) > 1
    assert any(rec.message.startswith("Executing processor 'ocrd-filter' took")
               for rec in caplog.records
               if rec.name == 'ocrd.process.profile')
    assert sum(1 for rec in caplog.records
               if rec.name == 'ocrd.processor.FilterProcessor' and
               "no matches" in rec.message) == 2
    output_files = workspace.mets.find_all_files(fileGrp='OCR-D-OUT')
    assert len(input_files) == len(output_files)
    output_files.sort(key=lambda x: x.url)
    assert output_files[0].local_filename == 'OCR-D-OUT/OCR-D-OUT_PHYS_0017.xml'
    output_pcgts0 = page_from_file(output_files[0])
    assert output_pcgts0.pcGtsId == output_files[0].ID
    assert len(output_pcgts0.Page.get_AllTextLines()) == len(input_pcgts0.Page.get_AllTextLines())
    
def test_filter_largefonts(workspace_kant, caplog):
    caplog.set_level(10)
    workspace = workspace_kant
    input_files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-PAGE')
    input_pcgts0 = page_from_file(input_files[0])
    proc = run_processor(FilterProcessor,
                         workspace=workspace,
                         input_file_grp="OCR-D-GT-PAGE",
                         output_file_grp="OCR-D-OUT",
                         parameter={'select': '//pc:TextRegion[pc:pixelarea(.) div string-length(pc:textequiv(.)) > 1000]',
                                    'plot': True})
    assert len(caplog.records) > 1
    assert any(rec.message.startswith("Executing processor 'ocrd-filter' took")
               for rec in caplog.records
               if rec.name == 'ocrd.process.profile')
    assert sum(1 for rec in caplog.records
               if rec.name == 'ocrd.processor.FilterProcessor' and
               "matched" in rec.message) == 5 # 4 in p17, 1 on p20
    output_files = workspace.mets.find_all_files(fileGrp='OCR-D-OUT')
    assert len(input_files) == len(output_files) - 5
    output_files.sort(key=lambda x: x.url)
    assert output_files[0].local_filename == 'OCR-D-OUT/OCR-D-OUT_PHYS_0017_r_1_1.IMG.png'
    assert output_files[4].local_filename == 'OCR-D-OUT/OCR-D-OUT_PHYS_0017.xml'
    output_pcgts4 = page_from_file(output_files[4])
    assert output_pcgts4.pcGtsId == output_files[4].ID
    assert len(output_pcgts4.Page.get_AllTextLines()) == len(input_pcgts0.Page.get_AllTextLines()) - 5
    
if __name__ == "__main__":
    main(__file__)
