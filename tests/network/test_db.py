from ocrd_network.models import StateEnum


def test_db_write_processing_job(mongo_processor_jobs):
    job_id = 'test_id_1234'
    inserted_job = mongo_processor_jobs.insert_one(
        document={
            "job_id": job_id,
            "processor_name": 'ocrd-dummy',
            "state": StateEnum.cached,
            "path_to_mets": '/ocrd/dummy/path',
            "input_file_grps": ['DEFAULT'],
            "output_file_grps": ['OCR-D-DUMMY']
        }
    )
    assert inserted_job
    found_job = mongo_processor_jobs.find_one(filter={"job_id": job_id})
    assert found_job


def test_db_read_processing_job(mongo_processor_jobs):
    job_id = 'test_id_1234'
    found_job = mongo_processor_jobs.find_one(filter={"job_id": job_id})
    assert found_job
    assert found_job['job_id'] == job_id
    assert found_job['processor_name'] == 'ocrd-dummy'
    assert found_job['state'] == StateEnum.cached
    assert found_job['path_to_mets'] == '/ocrd/dummy/path'
    assert found_job['input_file_grps'] == ['DEFAULT']
    assert found_job['output_file_grps'] == ['OCR-D-DUMMY']


def test_db_update_processing_job(mongo_processor_jobs):
    job_id = 'test_id_1234'
    mongo_processor_jobs.update_one(
        filter={"job_id": job_id},
        update={"$set": {"state": StateEnum.running}}
    )
    found_job = mongo_processor_jobs.find_one(filter={"job_id": job_id})
    assert found_job
    assert found_job['job_id'] == job_id
    assert found_job['processor_name'] == 'ocrd-dummy'
    assert found_job['state'] == StateEnum.running
    assert found_job['path_to_mets'] == '/ocrd/dummy/path'
    assert found_job['input_file_grps'] == ['DEFAULT']
    assert found_job['output_file_grps'] == ['OCR-D-DUMMY']
