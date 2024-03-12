from pytest import fixture
from src.ocrd_network.models import DBProcessorJob


@fixture(scope="session", name="processing_job_1")
def fixture_processing_job_1() -> DBProcessorJob:
    workspace_key = "/path/to/mets.xml"
    processing_job = DBProcessorJob(
        job_id="job_id_1",
        processor_name="processor_name_1",
        path_to_mets=workspace_key,
        input_file_grps=["DEFAULT"],
        output_file_grps=["OCR-D-BIN"],
        page_id="PHYS_0001..PHYS_0003",
        depends_on=[]
    )
    yield processing_job


@fixture(scope="session", name="processing_job_2")
def fixture_processing_job_2() -> DBProcessorJob:
    workspace_key = "/path/to/mets.xml"
    processing_job = DBProcessorJob(
        job_id="job_id_2",
        processor_name="processor_name_2",
        path_to_mets=workspace_key,
        input_file_grps=["OCR-D-BIN"],
        output_file_grps=["OCR-D-CROP"],
        page_id="PHYS_0001..PHYS_0003",
        depends_on=["job_id_1"]
    )
    yield processing_job


@fixture(scope="session", name="processing_job_3")
def fixture_processing_job_3() -> DBProcessorJob:
    workspace_key = "/path/to/mets.xml"
    processing_job = DBProcessorJob(
        job_id="job_id_3",
        processor_name="processor_name_3",
        path_to_mets=workspace_key,
        input_file_grps=["OCR-D-CROP"],
        output_file_grps=["OCR-D-BIN2"],
        page_id="PHYS_0001..PHYS_0003",
        depends_on=["job_id_2"]
    )
    yield processing_job


@fixture(scope="session", name="processing_job_4")
def fixture_processing_job_4() -> DBProcessorJob:
    workspace_key = "/path/to/mets.xml"
    processing_job = DBProcessorJob(
        job_id="job_id_4",
        processor_name="processor_name_4",
        path_to_mets=workspace_key,
        input_file_grps=["OCR-D-BIN2"],
        output_file_grps=["OCR-D-BIN-DENOISE"],
        page_id="PHYS_0001..PHYS_0003",
        depends_on=["job_id_2"]
    )
    yield processing_job
