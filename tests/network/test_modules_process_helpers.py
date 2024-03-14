from pathlib import Path
from src.ocrd.processor.builtin.dummy_processor import DummyProcessor
from src.ocrd_network.constants import NetworkLoggingDirs
from src.ocrd_network.logging_utils import get_root_logging_dir
from src.ocrd_network.process_helpers import invoke_processor
from src.ocrd_network.utils import generate_id
from tests.base import assets


def test_invoke_processor_bash():
    pass
    bash_lib_cp_processor = "tests/data/bashlib_cp_processor.sh"
    assert Path(bash_lib_cp_processor).exists(), f"Bash lib test processor not found in: {bash_lib_cp_processor}"

    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    assert Path(path_to_mets).exists()
    log_dir_root = get_root_logging_dir(module_name=NetworkLoggingDirs.PROCESSING_JOBS)
    job_id = generate_id()
    path_to_log_file = Path(log_dir_root, job_id)
    input_file_grp = "OCR-D-IMG"
    output_file_grp = f"OCR-D-BASH-TEST-{job_id}"
    invoke_processor(
        processor_class=None,  # required only for pythonic processors
        executable=bash_lib_cp_processor,
        abs_path_to_mets=path_to_mets,
        input_file_grps=[input_file_grp],
        output_file_grps=[output_file_grp],
        page_id="PHYS_0017,PHYS_0020",
        parameters={},
        log_filename=path_to_log_file,
        log_level="DEBUG"
    )
    assert Path(assets.path_to(f"{workspace_root}/{output_file_grp}")).exists()
    assert Path(path_to_log_file).exists()


def test_invoke_processor_pythonic():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    assert Path(path_to_mets).exists()
    log_dir_root = get_root_logging_dir(module_name=NetworkLoggingDirs.PROCESSING_JOBS)
    job_id = generate_id()
    path_to_log_file = Path(log_dir_root, job_id)
    input_file_grp = "OCR-D-IMG"
    output_file_grp = f"OCR-D-DUMMY-TEST-{job_id}"
    invoke_processor(
        processor_class=DummyProcessor,
        executable="",  # not required for pythonic processors
        abs_path_to_mets=path_to_mets,
        input_file_grps=[input_file_grp],
        output_file_grps=[output_file_grp],
        page_id="PHYS_0017,PHYS_0020",
        parameters={},
        log_filename=path_to_log_file,
        log_level="DEBUG"
    )
    assert Path(assets.path_to(f"{workspace_root}/{output_file_grp}")).exists()
    assert Path(path_to_log_file).exists()
