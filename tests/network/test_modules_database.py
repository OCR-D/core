import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pymongo import ReturnDocument

from ocrd_network.database import (
    db_claim_result_callback,
    db_claim_result_counter_decrement,
    db_complete_result_callback,
    db_release_result_callback_claim,
    sync_db_find_first_workflow_script_by_content,
    verify_database_uri,
    verify_mongodb_available,
)


@patch("ocrd_network.database.db_find_first_workflow_script_by_content")
def test_sync_db_find_first_workflow_script_by_content(mock_find):
    expected = object()
    mock_find.return_value = expected
    result = sync_db_find_first_workflow_script_by_content("test-content-hash")
    assert result is expected
    mock_find.assert_called_once_with("test-content-hash")


def test_verify_database_uri_accepts_valid_uri():
    uri = "mongodb://localhost:27017/ocrd"
    assert verify_database_uri(uri) == uri


def test_verify_database_uri_rejects_invalid_uri():
    with pytest.raises(ValueError, match="wrong format"):
        verify_database_uri("not-a-mongodb-uri")


@patch("ocrd_network.database.MongoClient")
def test_verify_mongodb_available(mock_client):
    verify_mongodb_available("mongodb://localhost:27017/ocrd")
    mock_client.assert_called_once_with("mongodb://localhost:27017/ocrd", serverSelectionTimeoutMS=60000.0)
    mock_client.return_value.admin.command.assert_called_once_with("ismaster")


@patch("ocrd_network.database.MongoClient")
def test_verify_mongodb_available_redacts_credentials(mock_client):
    mock_client.return_value.admin.command.side_effect = RuntimeError("Connection failed")
    with pytest.raises(RuntimeError) as exc_info:
        verify_mongodb_available("mongodb://user:secret@localhost:27017/ocrd")
    assert "secret" not in str(exc_info.value)
    assert "****" in str(exc_info.value)


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


@pytest.mark.parametrize("modified_count, expected", [(1, True), (0, False)])
@patch("ocrd_network.database.DBProcessorJob")
def test_db_complete_result_callback(mock_job, modified_count, expected):
    collection = Mock()
    collection.update_one = AsyncMock(return_value=Mock(modified_count=modified_count))
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
