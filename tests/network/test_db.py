from pytest import raises
from tests.base import assets
from ocrd_network.models import StateEnum
from ocrd_network.database import (
    sync_db_get_processing_job,
    sync_db_update_processing_job,
    sync_db_create_workspace,
    sync_db_get_workspace,
    sync_db_update_workspace
)


def test_db_processing_job_create(mongo_processor_jobs):
    job_id = 'test_id_1234'
    # TODO: There is no db wrapper to create processing job
    #  Hence, for now, use a low level method to insert a job
    db_created_processing_job = mongo_processor_jobs.insert_one(
        document={
            "job_id": job_id,
            "processor_name": 'ocrd-dummy',
            "state": StateEnum.cached,
            "path_to_mets": '/ocrd/dummy/path',
            "input_file_grps": ['DEFAULT'],
            "output_file_grps": ['OCR-D-DUMMY']
        }
    )
    assert db_created_processing_job
    db_found_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_found_processing_job
    assert db_found_processing_job.job_id == job_id
    assert db_found_processing_job.processor_name == 'ocrd-dummy'
    assert db_found_processing_job.state == StateEnum.cached
    assert db_found_processing_job.path_to_mets == '/ocrd/dummy/path'
    assert db_found_processing_job.input_file_grps == ['DEFAULT']
    assert db_found_processing_job.output_file_grps == ['OCR-D-DUMMY']

    with raises(ValueError) as value_error:
        sync_db_get_processing_job(job_id='non-existing-id')


def test_db_processing_job_update(mongo_processor_jobs):
    job_id = 'test_id_12345'
    # TODO: There is no db wrapper to create processing job
    #  Hence, for now, use a low level method to insert a job
    db_created_processing_job = mongo_processor_jobs.insert_one(
        document={
            "job_id": job_id,
            "processor_name": 'ocrd-dummy',
            "state": StateEnum.cached,
            "path_to_mets": '/ocrd/dummy/path',
            "input_file_grps": ['DEFAULT'],
            "output_file_grps": ['OCR-D-DUMMY']
        }
    )
    assert db_created_processing_job
    db_found_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_found_processing_job
    db_updated_processing_job = sync_db_update_processing_job(job_id=job_id, state=StateEnum.running)
    assert db_found_processing_job != db_updated_processing_job
    db_found_updated_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_found_updated_processing_job
    assert db_found_updated_processing_job == db_updated_processing_job
    assert db_found_updated_processing_job.state == StateEnum.running

    with raises(ValueError) as value_error:
        sync_db_update_processing_job(job_id='non-existing', state=StateEnum.running)
        sync_db_update_processing_job(job_id=job_id, non_existing_field='dummy_value')
        sync_db_update_processing_job(job_id=job_id, processor_name='non-updatable-field')


def test_db_workspace_create():
    mets_path = assets.path_to('kant_aufklaerung_1784/data/mets.xml')
    db_created_workspace = sync_db_create_workspace(mets_path=mets_path)
    assert db_created_workspace
    assert db_created_workspace.workspace_mets_path == mets_path
    db_found_workspace = sync_db_get_workspace(workspace_mets_path=mets_path)
    assert db_found_workspace
    assert db_found_workspace == db_created_workspace

    with raises(ValueError) as value_error:
        sync_db_get_workspace(workspace_id='non-existing-id')
        sync_db_get_workspace(workspace_mets_path='non-existing-mets')

    with raises(FileNotFoundError) as io_error:
        sync_db_create_workspace(mets_path='non-existing-mets')


def test_db_workspace_update():
    mets_path = assets.path_to('kant_aufklaerung_1784-binarized/data/mets.xml')
    dummy_mets_server_url = '/tmp/dummy.sock'

    db_created_workspace = sync_db_create_workspace(mets_path=mets_path)
    assert db_created_workspace
    db_found_workspace = sync_db_get_workspace(workspace_mets_path=mets_path)
    assert db_found_workspace
    assert db_created_workspace == db_found_workspace

    db_updated_workspace = sync_db_update_workspace(
        workspace_mets_path=mets_path,
        mets_server_url=dummy_mets_server_url
    )
    assert db_updated_workspace
    assert db_updated_workspace != db_created_workspace

    db_found_updated_workspace = sync_db_get_workspace(workspace_mets_path=mets_path)
    assert db_found_updated_workspace
    assert db_found_updated_workspace.workspace_mets_path == mets_path
    assert db_found_updated_workspace.mets_server_url == dummy_mets_server_url
    assert db_found_updated_workspace == db_updated_workspace
