import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pymongo import ReturnDocument

from ocrd_network.database import (
    db_claim_result_callback,
    db_claim_result_counter_decrement,
    db_complete_result_callback,
    db_create_processing_job,
    db_create_workflow_job,
    db_create_workflow_script,
    db_create_workspace,
    db_find_first_workflow_script_by_content,
    db_get_processing_job,
    db_get_processing_jobs,
    db_get_workflow_job,
    db_get_workflow_script,
    db_get_workspace,
    db_release_result_callback_claim,
    db_update_processing_job,
    db_update_workspace,
    initiate_database,
    sync_db_create_processing_job,
    sync_db_create_workflow_job,
    sync_db_create_workflow_script,
    sync_db_create_workspace,
    sync_db_find_first_workflow_script_by_content,
    sync_db_get_processing_job,
    sync_db_get_processing_jobs,
    sync_db_get_workflow_job,
    sync_db_get_workflow_script,
    sync_db_get_workspace,
    sync_db_update_processing_job,
    sync_db_update_workspace,
    sync_initiate_database,
    verify_database_uri,
    verify_mongodb_available,
)


# Database initialization

@patch("ocrd_network.database.init_beanie", new_callable=AsyncMock)
@patch("ocrd_network.database.AsyncMongoClient")
def test_initiate_database(mock_client, mock_init_beanie):
    asyncio.run(initiate_database("mongodb://localhost:27017/ocrd"))
    mock_client.assert_called_once_with("mongodb://localhost:27017/ocrd")
    mock_init_beanie.assert_awaited_once()
    assert mock_init_beanie.await_args.kwargs["database"] == mock_client.return_value.get_default_database.return_value
    assert len(mock_init_beanie.await_args.kwargs["document_models"]) == 4


@patch("ocrd_network.database.init_beanie", new_callable=AsyncMock)
@patch("ocrd_network.database.AsyncMongoClient")
def test_initiate_database_custom_name(mock_client, mock_init_beanie):
    asyncio.run(initiate_database("mongodb://localhost:27017", "custom"))
    mock_client.return_value.get_default_database.assert_called_once_with(default="custom")


# Workspace creation

def test_db_create_workspace_file_not_found(tmp_path):
    mets_path = str(tmp_path / "missing.xml")
    with pytest.raises(FileNotFoundError, match="does not exist"):
        asyncio.run(db_create_workspace(mets_path))


@patch("ocrd_network.database.db_get_workspace", new_callable=AsyncMock)
def test_db_create_workspace_already_exists(mock_get_workspace, tmp_path):
    mets_path = tmp_path / "mets.xml"
    mets_path.touch()
    expected = object()
    mock_get_workspace.return_value = expected
    result = asyncio.run(db_create_workspace(str(mets_path)))
    assert result is expected
    mock_get_workspace.assert_awaited_once_with(workspace_mets_path=str(mets_path))


@patch("ocrd_network.database.DBWorkspace")
@patch("ocrd_network.database.db_get_workspace", new_callable=AsyncMock)
def test_db_create_workspace_new(mock_get_workspace, mock_workspace, tmp_path):
    mets_path = tmp_path / "mets.xml"
    mets_path.touch()
    mock_get_workspace.side_effect = ValueError("Not found")
    mock_workspace.return_value.save = AsyncMock()
    result = asyncio.run(db_create_workspace(str(mets_path)))
    mock_workspace.assert_called_once_with(
        workspace_id=mock_workspace.call_args.kwargs["workspace_id"],
        workspace_path=Path(tmp_path),
        workspace_mets_path=str(mets_path),
        ocrd_identifier="",
        bagit_profile_identifier="",
    )
    assert result is mock_workspace.return_value
    mock_workspace.return_value.save.assert_awaited_once()


# Workspace lookup

def test_db_get_workspace_requires_search_key():
    with pytest.raises(ValueError, match="Either"):
        asyncio.run(db_get_workspace())


@pytest.mark.parametrize("search_kwargs, error_match", [
    ({"workspace_id": "missing-id"}, "Workspace with id"),
    ({"workspace_mets_path": "/tmp/missing/mets.xml"}, "Workspace with path"),
])
@patch("ocrd_network.database.DBWorkspace")
def test_db_get_workspace_not_found(mock_workspace, search_kwargs, error_match):
    mock_workspace.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match=error_match):
        asyncio.run(db_get_workspace(**search_kwargs))
    mock_workspace.find_one.assert_awaited_once()


@pytest.mark.parametrize("search_kwargs", [
    {"workspace_id": "workspace-1"},
    {"workspace_mets_path": "/tmp/workspace/mets.xml"},
])
@patch("ocrd_network.database.DBWorkspace")
def test_db_get_workspace_found(mock_workspace, search_kwargs):
    expected = object()
    mock_workspace.find_one = AsyncMock(return_value=expected)
    result = asyncio.run(db_get_workspace(**search_kwargs))
    assert result is expected
    mock_workspace.find_one.assert_awaited_once()


@patch("ocrd_network.database.DBWorkspace")
def test_db_get_workspace_both_search_keys(mock_workspace):
    workspace_by_id = object()
    workspace_by_path = object()
    mock_workspace.find_one = AsyncMock(
        side_effect=[workspace_by_id, workspace_by_path]
    )
    result = asyncio.run(db_get_workspace(
        workspace_id="workspace-1",
        workspace_mets_path="/tmp/workspace/mets.xml",
    ))
    assert result is workspace_by_path
    assert mock_workspace.find_one.await_count == 2


# Workspace updates

def test_db_update_workspace_requires_search_key():
    with pytest.raises(ValueError, match="Either"):
        asyncio.run(db_update_workspace(ocrd_identifier="test"))


@pytest.mark.parametrize("search_kwargs, error_match", [
    ({"workspace_id": "missing-id"}, "Workspace with id"),
    ({"workspace_mets_path": "/tmp/missing/mets.xml"}, "Workspace with path"),
])
@patch("ocrd_network.database.DBWorkspace")
def test_db_update_workspace_not_found(mock_workspace, search_kwargs, error_match):
    mock_workspace.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match=error_match):
        asyncio.run(db_update_workspace(**search_kwargs, ocrd_identifier="test"))


@pytest.mark.parametrize("field", [
    "ocrd_identifier",
    "bagit_profile_identifier",
    "ocrd_base_version_checksum",
    "ocrd_mets",
    "bag_info_adds",
    "deleted",
    "mets_server_url",
])
@patch("ocrd_network.database.DBWorkspace")
def test_db_update_workspace_allowed_fields(mock_workspace, field):
    workspace = SimpleNamespace(
        workspace_id="workspace-1",
        workspace_mets_path="/tmp/workspace/mets.xml",
        ocrd_identifier="",
        bagit_profile_identifier="",
        ocrd_base_version_checksum="",
        ocrd_mets=None,
        bag_info_adds=None,
        deleted=False,
        mets_server_url=None,
        save=AsyncMock(),
    )
    mock_workspace.find_one = AsyncMock(return_value=workspace)
    value = "updated-value"
    search_kwargs = (
        {"workspace_mets_path": "/tmp/workspace/mets.xml"}
        if field == "workspace_id"
        else {"workspace_id": "workspace-1"}
    )
    result = asyncio.run(db_update_workspace(**search_kwargs, **{field: value}))
    assert result is workspace
    assert getattr(workspace, field) == value
    workspace.save.assert_awaited_once()


@patch("ocrd_network.database.DBWorkspace")
def test_db_update_workspace_unknown_field(mock_workspace):
    workspace = SimpleNamespace(workspace_id="workspace-1", save=AsyncMock())
    mock_workspace.find_one = AsyncMock(return_value=workspace)
    with pytest.raises(ValueError, match="is not available"):
        asyncio.run(db_update_workspace(
            workspace_id="workspace-1",
            unknown_field="value",
        ))
    workspace.save.assert_not_awaited()


@patch("ocrd_network.database.DBWorkspace")
def test_db_update_workspace_non_updatable_field(mock_workspace):
    workspace = SimpleNamespace(id="workspace-1", save=AsyncMock())
    mock_workspace.find_one = AsyncMock(return_value=workspace)
    with pytest.raises(ValueError, match="is not updatable"):
        asyncio.run(db_update_workspace(
            workspace_id="workspace-1",
            id="new-id",
        ))
    workspace.save.assert_not_awaited()


# Processing-job creation and lookup

def test_db_create_processing_job():
    job = Mock()
    job.insert = AsyncMock(return_value=job)
    result = asyncio.run(db_create_processing_job(job))
    assert result is job
    job.insert.assert_awaited_once()


@patch("ocrd_network.database.DBProcessorJob")
def test_db_get_processing_job_found(mock_job):
    expected = object()
    mock_job.find_one = AsyncMock(return_value=expected)
    result = asyncio.run(db_get_processing_job("job-1"))
    assert result is expected
    mock_job.find_one.assert_awaited_once()


@patch("ocrd_network.database.DBProcessorJob")
def test_db_get_processing_job_not_found(mock_job):
    mock_job.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match="Processing job with id"):
        asyncio.run(db_get_processing_job("missing-job"))


# Processing-job updates

@patch("ocrd_network.database.DBProcessorJob")
def test_db_update_processing_job_not_found(mock_job):
    mock_job.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match="Processing job with id"):
        asyncio.run(db_update_processing_job("missing-job", state="done"))


@pytest.mark.parametrize("field", [
    "state",
    "start_time",
    "end_time",
    "path_to_mets",
    "exec_time",
    "log_file_path",
])
@patch("ocrd_network.database.DBProcessorJob")
def test_db_update_processing_job_allowed_fields(mock_job, field):
    job = SimpleNamespace(
        job_id="job-1",
        state="created",
        start_time=None,
        end_time=None,
        path_to_mets=None,
        exec_time=None,
        log_file_path=None,
        save=AsyncMock(),
    )
    mock_job.find_one = AsyncMock(return_value=job)
    value = "updated-value"
    result = asyncio.run(db_update_processing_job(
        "job-1",
        **{field: value},
    ))
    assert result is job
    assert getattr(job, field) == value
    job.save.assert_awaited_once()


@patch("ocrd_network.database.DBProcessorJob")
def test_db_update_processing_job_unknown_field(mock_job):
    job = SimpleNamespace(job_id="job-1", save=AsyncMock())
    mock_job.find_one = AsyncMock(return_value=job)
    with pytest.raises(ValueError, match="is not available"):
        asyncio.run(db_update_processing_job("job-1", unknown_field="value"))
    job.save.assert_not_awaited()


@patch("ocrd_network.database.DBProcessorJob")
def test_db_update_processing_job_non_updatable_field(mock_job):
    job = SimpleNamespace(job_id="job-1", id="old-id", save=AsyncMock())
    mock_job.find_one = AsyncMock(return_value=job)
    with pytest.raises(ValueError, match="is not updatable"):
        asyncio.run(db_update_processing_job("job-1", id="new-id"))
    job.save.assert_not_awaited()


# Atomic result-callback operations

@pytest.mark.parametrize("result, expected", [
    ({"job_id": "job-1"}, True),
    (None, False),
])
@patch("ocrd_network.database.DBProcessorJob")
def test_db_claim_result_callback(mock_job, result, expected):
    collection = Mock()
    collection.find_one_and_update = AsyncMock(return_value=result)
    mock_job.get_pymongo_collection.return_value = collection
    actual = asyncio.run(db_claim_result_callback("job-1"))
    assert actual is expected
    collection.find_one_and_update.assert_awaited_once_with(
        {
            "job_id": "job-1",
            "result_callback_processed": {"$ne": True},
            "result_callback_in_progress": {"$ne": True},
        },
        {"$set": {"result_callback_in_progress": True}},
        return_document=ReturnDocument.BEFORE,
    )


@pytest.mark.parametrize("result, expected", [
    ({"job_id": "job-1"}, True),
    (None, False),
])
@patch("ocrd_network.database.DBProcessorJob")
def test_db_claim_result_counter_decrement(mock_job, result, expected):
    collection = Mock()
    collection.find_one_and_update = AsyncMock(return_value=result)
    mock_job.get_pymongo_collection.return_value = collection
    actual = asyncio.run(db_claim_result_counter_decrement("job-1"))
    assert actual is expected
    collection.find_one_and_update.assert_awaited_once_with(
        {
            "job_id": "job-1",
            "result_callback_counter_decremented": {"$ne": True},
        },
        {"$set": {"result_callback_counter_decremented": True}},
        return_document=ReturnDocument.BEFORE,
    )


@patch("ocrd_network.database.DBProcessorJob")
def test_db_release_result_callback_claim(mock_job):
    collection = Mock()
    collection.update_one = AsyncMock()
    mock_job.get_pymongo_collection.return_value = collection
    asyncio.run(db_release_result_callback_claim("job-1"))
    collection.update_one.assert_awaited_once_with(
        {
            "job_id": "job-1",
            "result_callback_processed": {"$ne": True},
        },
        {"$set": {"result_callback_in_progress": False}},
    )


@pytest.mark.parametrize("modified_count, expected", [
    (1, True),
    (0, False),
    (2, False),
])
@patch("ocrd_network.database.DBProcessorJob")
def test_db_complete_result_callback(mock_job, modified_count, expected):
    collection = Mock()
    collection.update_one = AsyncMock(
        return_value=Mock(modified_count=modified_count)
    )
    mock_job.get_pymongo_collection.return_value = collection
    actual = asyncio.run(db_complete_result_callback("job-1"))
    assert actual is expected
    collection.update_one.assert_awaited_once_with(
        {
            "job_id": "job-1",
            "result_callback_in_progress": True,
            "result_callback_processed": {"$ne": True},
        },
        {
            "$set": {
                "result_callback_processed": True,
                "result_callback_in_progress": False,
            }
        },
    )


# Workflow-job creation and lookup

def test_db_create_workflow_job():
    job = Mock()
    job.insert = AsyncMock(return_value=job)
    result = asyncio.run(db_create_workflow_job(job))
    assert result is job
    job.insert.assert_awaited_once()


@patch("ocrd_network.database.DBWorkflowJob")
def test_db_get_workflow_job_found(mock_job):
    expected = object()
    mock_job.find_one = AsyncMock(return_value=expected)
    result = asyncio.run(db_get_workflow_job("workflow-1"))
    assert result is expected
    mock_job.find_one.assert_awaited_once()


@patch("ocrd_network.database.DBWorkflowJob")
def test_db_get_workflow_job_not_found(mock_job):
    mock_job.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match="Workflow job with id"):
        asyncio.run(db_get_workflow_job("missing-workflow"))


# Processing-job list lookup

@patch("ocrd_network.database.DBProcessorJob")
@patch("ocrd_network.database.In")
def test_db_get_processing_jobs(mock_in, mock_job):
    expected = [object(), object()]
    query = Mock()
    query.to_list = AsyncMock(return_value=expected)
    mock_job.find.return_value = query
    result = asyncio.run(db_get_processing_jobs(["job-1", "job-2"]))
    assert result == expected
    mock_in.assert_called_once()
    mock_job.find.assert_called_once_with(mock_in.return_value)
    query.to_list.assert_awaited_once()


# Workflow-script creation and lookup

def test_db_create_workflow_script():
    workflow = Mock()
    workflow.insert = AsyncMock(return_value=workflow)
    result = asyncio.run(db_create_workflow_script(workflow))
    assert result is workflow
    workflow.insert.assert_awaited_once()


@patch("ocrd_network.database.DBWorkflowScript")
def test_db_get_workflow_script_found(mock_script):
    expected = object()
    mock_script.find_one = AsyncMock(return_value=expected)
    result = asyncio.run(db_get_workflow_script("workflow-1"))
    assert result is expected
    mock_script.find_one.assert_awaited_once()


@patch("ocrd_network.database.DBWorkflowScript")
def test_db_get_workflow_script_not_found(mock_script):
    mock_script.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match="Workflow-script with id"):
        asyncio.run(db_get_workflow_script("missing-workflow"))


@patch("ocrd_network.database.DBWorkflowScript")
def test_db_find_first_workflow_script_by_content_found(mock_script):
    expected = object()
    mock_script.find_one = AsyncMock(return_value=expected)
    result = asyncio.run(db_find_first_workflow_script_by_content("content-hash"))
    assert result is expected
    mock_script.find_one.assert_awaited_once()


@patch("ocrd_network.database.DBWorkflowScript")
def test_db_find_first_workflow_script_by_content_not_found(mock_script):
    mock_script.find_one = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match="content_hash"):
        asyncio.run(db_find_first_workflow_script_by_content("missing-hash"))


# MongoDB URI validation

def test_verify_database_uri_accepts_valid_uri():
    uri = "mongodb://localhost:27017/ocrd"
    assert verify_database_uri(uri) == uri


def test_verify_database_uri_rejects_invalid_uri():
    with pytest.raises(ValueError, match="wrong format"):
        verify_database_uri("not-a-mongodb-uri")


# MongoDB connection verification

@patch("ocrd_network.database.MongoClient")
def test_verify_mongodb_available(mock_client):
    verify_mongodb_available("mongodb://localhost:27017/ocrd")
    mock_client.assert_called_once_with(
        "mongodb://localhost:27017/ocrd",
        serverSelectionTimeoutMS=60000.0,
    )
    mock_client.return_value.admin.command.assert_called_once_with("ismaster")


@pytest.mark.parametrize("failure_stage", ["client", "command"])
@patch("ocrd_network.database.MongoClient")
def test_verify_mongodb_available_failure_redacts_credentials(mock_client, failure_stage):
    if failure_stage == "client":
        mock_client.side_effect = RuntimeError("Connection failed")
    else:
        mock_client.return_value.admin.command.side_effect = RuntimeError("Connection failed")
    with pytest.raises(RuntimeError) as exc_info:
        verify_mongodb_available("mongodb://user:secret@localhost:27017/ocrd")
    assert "secret" not in str(exc_info.value)
    assert "****" in str(exc_info.value)


# Synchronous wrappers
SYNC_WRAPPERS = [
    (sync_initiate_database, "initiate_database", ("mongodb://localhost:27017/ocrd",), {}),
    (sync_db_create_workspace, "db_create_workspace", ("/tmp/mets.xml",), {}),
    (sync_db_get_workspace, "db_get_workspace", (), {"workspace_id": "workspace-1"}),
    (sync_db_update_workspace, "db_update_workspace", (), {"workspace_id": "workspace-1", "ocrd_identifier": "test"}),
    (sync_db_create_processing_job, "db_create_processing_job", (object(),), {}),
    (sync_db_get_processing_job, "db_get_processing_job", ("job-1",), {}),
    (sync_db_update_processing_job, "db_update_processing_job", ("job-1",), {"state": "done"}),
    (sync_db_create_workflow_job, "db_create_workflow_job", (object(),), {}),
    (sync_db_get_workflow_job, "db_get_workflow_job", ("workflow-1",), {}),
    (sync_db_get_processing_jobs, "db_get_processing_jobs", (["job-1"],), {}),
    (sync_db_create_workflow_script, "db_create_workflow_script", (object(),), {}),
    (sync_db_get_workflow_script, "db_get_workflow_script", ("workflow-1",), {}),
    (sync_db_find_first_workflow_script_by_content, "db_find_first_workflow_script_by_content", ("content-hash",), {}),
]


@pytest.mark.parametrize("sync_function, async_function_name, args, kwargs", SYNC_WRAPPERS)
def test_sync_database_wrappers(sync_function, async_function_name, args, kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with patch(
            f"ocrd_network.database.{async_function_name}",
            new_callable=AsyncMock,
        ) as mock_async:
            result = sync_function(*args, **kwargs)
        assert result is (None if async_function_name == "initiate_database" else mock_async.return_value)
        mock_async.assert_awaited_once()
    finally:
        asyncio.set_event_loop(None)
        loop.close()


def test_sync_initiate_database():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with patch(
            "ocrd_network.database.initiate_database",
            new_callable=AsyncMock,
        ) as mock_init:
            result = sync_initiate_database("mongodb://localhost:27017/ocrd")
        assert result is None
        mock_init.assert_awaited_once_with("mongodb://localhost:27017/ocrd", "ocrd")
    finally:
        asyncio.set_event_loop(None)
        loop.close()
