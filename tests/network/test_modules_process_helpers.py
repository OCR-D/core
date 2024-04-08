from contextlib import contextmanager
from os import environ
from pathlib import Path

from ocrd.processor.builtin.dummy_processor import DummyProcessor
from ocrd_network.constants import NetworkLoggingDirs
from ocrd_network.logging_utils import get_root_logging_dir
from ocrd_network.process_helpers import invoke_processor
from ocrd_network.utils import generate_id

from tests.base import assets

@contextmanager
def temp_env_var(k, v):
    v_before = environ.get(k, None)
    environ[k] = v
    yield
    if v_before is not None:
        environ[k] = v_before
    else:
        del environ[k]


def test_invoke_processor_bash():
    scriptdir = Path(__file__).parent.parent / 'data'
    with temp_env_var('PATH', f'{scriptdir}:{environ["PATH"]}'):
        workspace_root = "kant_aufklaerung_1784/data"
        path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
        assert Path(path_to_mets).exists()
        log_dir_root = get_root_logging_dir(module_name=NetworkLoggingDirs.PROCESSING_JOBS)
        job_id = generate_id()
        path_to_log_file = Path(log_dir_root, job_id)
        input_file_grp = "OCR-D-IMG"
        output_file_grp = f"OCR-D-BASH-TEST-{job_id}"
        try:
            invoke_processor(
                processor_class=None,  # required only for pythonic processors
                executable='ocrd-cp',
                abs_path_to_mets=path_to_mets,
                input_file_grps=[input_file_grp],
                output_file_grps=[output_file_grp],
                page_id="PHYS_0017,PHYS_0020",
                parameters={},
                log_filename=path_to_log_file,
                log_level="DEBUG"
            )
        except:
            with open(path_to_log_file, 'r', encoding='utf-8') as f:
                print(f.read())
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
