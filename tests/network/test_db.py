from tests.base import assets
from ocrd_network.models import StateEnum
from ocrd_network.database import (
    sync_db_create_workspace,
    sync_db_get_workspace,
    sync_db_update_workspace
)


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


def test_db_create_workspace(mongo_workspaces):
    mets_path = assets.path_to('kant_aufklaerung_1784/data/mets.xml')
    db_created_workspace = sync_db_create_workspace(mets_path=mets_path)
    assert db_created_workspace
    assert db_created_workspace.workspace_mets_path == mets_path
    db_found_workspace = sync_db_get_workspace(workspace_mets_path=mets_path)
    assert db_found_workspace
    assert db_found_workspace.workspace_mets_path == mets_path


def test_db_update_workspace(mongo_workspaces):
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
