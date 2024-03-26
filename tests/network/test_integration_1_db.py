from datetime import datetime
from hashlib import md5
from pathlib import Path
from pytest import raises
from tests.base import assets
from src.ocrd_network import JobState
from src.ocrd_network.models import DBProcessorJob, DBWorkflowScript
from src.ocrd_network.database import (
    sync_db_create_processing_job,
    sync_db_get_processing_job,
    sync_db_update_processing_job,
    sync_db_create_workspace,
    sync_db_get_workspace,
    sync_db_update_workspace,
    sync_db_create_workflow_script,
    sync_db_get_workflow_script,
    sync_db_find_first_workflow_script_by_content
)


def test_db_processing_job_create(mongo_client):
    job_id = f"test_job_id_{datetime.now()}"
    path_to_mets = "/ocrd/dummy/path"
    processor_name = "ocrd-dummy"
    job_state = JobState.cached
    input_file_group = "DEFAULT"
    output_file_group = "OCR-D-DUMMY"
    db_created_processing_job = sync_db_create_processing_job(
        db_processing_job=DBProcessorJob(
            job_id=job_id,
            processor_name=processor_name,
            state=job_state,
            path_to_mets=path_to_mets,
            input_file_grps=[input_file_group],
            output_file_grps=[output_file_group]
        )
    )
    assert db_created_processing_job
    db_found_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_found_processing_job
    assert db_found_processing_job.job_id == job_id
    assert db_found_processing_job.processor_name == processor_name
    assert db_found_processing_job.state == job_state
    assert db_found_processing_job.path_to_mets == path_to_mets
    assert db_found_processing_job.input_file_grps == [input_file_group]
    assert db_found_processing_job.output_file_grps == [output_file_group]

    with raises(ValueError):
        sync_db_get_processing_job(job_id="non-existing-id")


def test_db_processing_job_update(mongo_client):
    job_id = f"test_job_id_{datetime.now()}"
    path_to_mets = "/ocrd/dummy/path"
    processor_name = "ocrd-dummy"
    input_file_group = "DEFAULT"
    output_file_group = "OCR-D-DUMMY"
    db_created_processing_job = sync_db_create_processing_job(
        db_processing_job=DBProcessorJob(
            job_id=job_id,
            processor_name=processor_name,
            state=JobState.cached,
            path_to_mets=path_to_mets,
            input_file_grps=[input_file_group],
            output_file_grps=[output_file_group]
        )
    )
    assert db_created_processing_job
    db_found_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_found_processing_job
    db_updated_processing_job = sync_db_update_processing_job(job_id=job_id, state=JobState.running)
    assert db_found_processing_job != db_updated_processing_job
    db_found_updated_processing_job = sync_db_get_processing_job(job_id=job_id)
    assert db_found_updated_processing_job
    assert db_found_updated_processing_job == db_updated_processing_job
    assert db_found_updated_processing_job.state == JobState.running

    with raises(ValueError):
        sync_db_update_processing_job(job_id="non-existing", state=JobState.running)
        sync_db_update_processing_job(job_id=job_id, non_existing_field="dummy_value")
        sync_db_update_processing_job(job_id=job_id, processor_name="non-updatable-field")


def test_db_workspace_create(mongo_client):
    mets_path = assets.path_to("kant_aufklaerung_1784/data/mets.xml")
    db_created_workspace = sync_db_create_workspace(mets_path=mets_path)
    assert db_created_workspace
    assert db_created_workspace.workspace_mets_path == mets_path
    db_found_workspace = sync_db_get_workspace(workspace_mets_path=mets_path)
    assert db_found_workspace
    assert db_found_workspace == db_created_workspace

    with raises(ValueError):
        sync_db_get_workspace(workspace_id="non-existing-id")
        sync_db_get_workspace(workspace_mets_path="non-existing-mets")

    with raises(FileNotFoundError):
        sync_db_create_workspace(mets_path="non-existing-mets")


def test_db_workspace_update(mongo_client):
    mets_path = assets.path_to("kant_aufklaerung_1784-binarized/data/mets.xml")
    dummy_mets_server_url = "/tmp/dummy.sock"

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


# TODO: There is no db wrapper implemented due to direct access in the processing server...
#   TODO2: Should be refactored with proper asset access
def create_db_model_workflow_script(
    workflow_id: str,
    script_path: Path = Path(Path(__file__).parent, "dummy-workflow.txt")
) -> DBWorkflowScript:
    workflow_id = workflow_id
    with open(script_path, "rb") as fp:
        content = (fp.read()).decode("utf-8")
    content_hash = md5(content.encode("utf-8")).hexdigest()
    return DBWorkflowScript(workflow_id=workflow_id, content=content, content_hash=content_hash)


def test_db_workflow_script_create(mongo_client):
    workflow_id = f"test_workflow_{datetime.now()}"
    db_model_workflow_script = create_db_model_workflow_script(workflow_id=workflow_id)
    db_created_workflow_script = sync_db_create_workflow_script(db_workflow_script=db_model_workflow_script)
    assert db_created_workflow_script
    db_found_workflow_script = sync_db_get_workflow_script(workflow_id=workflow_id)
    assert db_found_workflow_script
    assert db_found_workflow_script == db_created_workflow_script

    with raises(ValueError):
        sync_db_get_workflow_script(workflow_id="non-existing-id")


def test_db_find_workflow_script_by_content(mongo_client):
    workflow_id = f"test_workflow_{datetime.now()}"
    db_model_wf_script = create_db_model_workflow_script(workflow_id=workflow_id)
    db_created_workflow_script = sync_db_create_workflow_script(db_workflow_script=db_model_wf_script)
    assert db_created_workflow_script
    db_found_workflow_script = sync_db_find_first_workflow_script_by_content(workflow_id=db_model_wf_script.workflow_id)
    assert db_found_workflow_script
    assert db_found_workflow_script == db_created_workflow_script


# TODO: hard to implement without some refactoring in the ocrd_network
#  and providing proper db wrappers
def test_db_workflow_job_create():
    pass


# TODO: hard to implement without some refactoring in the ocrd_network
#  and providing proper db wrappers
def test_db_workflow_job_update():
    pass
