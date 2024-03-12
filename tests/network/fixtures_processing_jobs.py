from pytest import fixture
from typing import List
from src.ocrd_network.constants import JobState
from src.ocrd_network.database import sync_db_create_processing_job
from src.ocrd_network.models import DBProcessorJob
from src.ocrd_network.utils import generate_id


@fixture(scope="package", name="processing_job_1")
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


@fixture(scope="package", name="processing_job_2")
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


@fixture(scope="package", name="processing_job_3")
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


@fixture(scope="package", name="processing_job_4")
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


@fixture(scope="function", name="processing_jobs_list")
def fixture_processing_jobs_list(
    processing_job_1: DBProcessorJob,
    processing_job_2: DBProcessorJob,
    processing_job_3: DBProcessorJob,
    processing_job_4: DBProcessorJob
) -> List[DBProcessorJob]:
    processing_jobs = []
    workspace_key = "/path/to/mets.xml"
    processing_job_1.path_to_mets = workspace_key
    processing_job_2.path_to_mets = workspace_key
    processing_job_3.path_to_mets = workspace_key
    processing_job_4.path_to_mets = workspace_key

    assert processing_job_1.state == JobState.unset
    assert processing_job_2.state == JobState.unset
    assert processing_job_3.state == JobState.unset
    assert processing_job_4.state == JobState.unset

    processing_job_1.job_id = generate_id()
    processing_job_2.job_id = generate_id()
    processing_job_3.job_id = generate_id()
    processing_job_4.job_id = generate_id()

    # Configure the processing jobs' dependency lists
    processing_job_1.depends_on = []
    processing_job_2.depends_on = [processing_job_1.job_id]
    # Both job 3 and job 4 depend on job 2
    processing_job_3.depends_on = [processing_job_2.job_id]
    processing_job_4.depends_on = [processing_job_2.job_id]

    # Insert the processing jobs into the database
    db_processing_job_1 = sync_db_create_processing_job(processing_job_1)
    db_processing_job_2 = sync_db_create_processing_job(processing_job_2)
    db_processing_job_3 = sync_db_create_processing_job(processing_job_3)
    db_processing_job_4 = sync_db_create_processing_job(processing_job_4)

    assert db_processing_job_1.state == JobState.unset
    assert db_processing_job_2.state == JobState.unset
    assert db_processing_job_3.state == JobState.unset
    assert db_processing_job_4.state == JobState.unset

    processing_jobs.append(db_processing_job_1)
    processing_jobs.append(db_processing_job_2)
    processing_jobs.append(db_processing_job_3)
    processing_jobs.append(db_processing_job_4)
    yield processing_jobs
