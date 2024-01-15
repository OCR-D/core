from ocrd_network.models import DBProcessorJob, StateEnum
from ocrd_network.database import sync_db_get_processing_job


def test_db_write_processing_job(mongo_processor_jobs):
    job_id = 'test_id_1234'
    db_processing_job = DBProcessorJob(
        job_id=job_id,
        processor_name='ocrd-dummy',
        state=StateEnum.cached,
        path_to_mets='/ocrd/dummy/path',
        input_file_grps=['DEFAULT'],
        output_file_grps=['OCR-D-DUMMY']
    )
    inserted_job = db_processing_job.insert()
    assert inserted_job
    found_job = mongo_processor_jobs.find_one({"job_id": job_id})
    assert found_job


def test_db_read_processing_job():
    job_id = 'test_id_1234'
    db_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_processing_job.job_id == job_id
    assert db_processing_job.processor_name == 'ocrd-dummy'
    assert db_processing_job.state == StateEnum.cached
    assert db_processing_job.path_to_mets == '/ocrd/dummy/path'
    assert db_processing_job.input_file_grps == ['DEFAULT']
    assert db_processing_job.output_file_grps == ['OCR-D-DUMMY']


def test_db_update_processing_job():
    pass
