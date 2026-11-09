import json
from unittest.mock import Mock, call
import pytest
from requests.exceptions import RequestException, JSONDecodeError
from ocrd_network.constants import JobState
from ocrd_network.client_utils import (
    _poll_endpoint_status,
    _raise_if_error,
    get_ps_processing_job_status,
    post_ps_processing_request,
    post_ps_workflow_request,
    verify_server_protocol,
)


def test_poll_endpoint_status_stops_on_success(monkeypatch):
    status = Mock(side_effect=[JobState.unset, JobState.success])
    sleep = Mock()
    monkeypatch.setattr("ocrd_network.client_utils.get_ps_processing_job_status", status)
    monkeypatch.setattr("ocrd_network.client_utils.sleep", sleep)
    result = _poll_endpoint_status("http://server", "job-1", "processor", 5, 1)
    assert result == JobState.success
    assert status.call_count == 2
    assert sleep.call_count == 2


def test_poll_endpoint_status_stops_on_failure(monkeypatch):
    status = Mock(return_value=JobState.failed)
    monkeypatch.setattr("ocrd_network.client_utils.get_ps_processing_job_status", status)
    monkeypatch.setattr("ocrd_network.client_utils.sleep", Mock())
    result = _poll_endpoint_status("http://server", "job-1", "processor", 5, 1)
    assert result == JobState.failed
    status.assert_called_once_with("http://server", "job-1")


def test_poll_endpoint_status_returns_last_state_on_timeout(monkeypatch):
    status = Mock(return_value=JobState.unset)
    sleep = Mock()
    monkeypatch.setattr("ocrd_network.client_utils.get_ps_processing_job_status", status)
    monkeypatch.setattr("ocrd_network.client_utils.sleep", sleep)
    result = _poll_endpoint_status("http://server", "job-1", "processor", 3, 2)
    assert result == JobState.unset
    assert status.call_count == 3
    assert sleep.call_count == 3


def test_poll_endpoint_status_rejects_unknown_job_type():
    with pytest.raises(ValueError, match="Unknown job type"):
        _poll_endpoint_status("http://server", "job-1", "unknown", 3, 1)


def test_poll_endpoint_status_with_zero_tries(monkeypatch):
    status = Mock()
    sleep = Mock()
    monkeypatch.setattr("ocrd_network.client_utils.get_ps_processing_job_status", status)
    monkeypatch.setattr("ocrd_network.client_utils.sleep", sleep)
    result = _poll_endpoint_status("http://server", "job-1", "processor", 0, 1)
    assert result == JobState.unset
    status.assert_not_called()
    sleep.assert_not_called()


def test_raise_if_error_accepts_successful_response():
    response = Mock()
    response.raise_for_status.return_value = None
    _raise_if_error(response)
    response.raise_for_status.assert_called_once()


def test_raise_if_error_extracts_json_detail():
    response = Mock()
    response.raise_for_status.side_effect = RequestException("HTTP error")
    response.json.return_value = {"detail": "Job not found"}
    with pytest.raises(RequestException) as error:
        _raise_if_error(response)
    assert error.value.detail_message == "Job not found"


def test_raise_if_error_uses_response_text_for_invalid_json():
    response = Mock()
    response.raise_for_status.side_effect = RequestException("HTTP error")
    response.json.side_effect = JSONDecodeError("Invalid JSON", "invalid", 0)
    response.text = "Internal server error"
    with pytest.raises(RequestException) as error:
        _raise_if_error(response)
    assert error.value.detail_message == "Internal server error"


def test_verify_server_protocol_accepts_http_and_https():
    verify_server_protocol("http://localhost:8080")
    verify_server_protocol("https://localhost:8080")


def test_verify_server_protocol_rejects_missing_protocol():
    with pytest.raises(ValueError, match="Wrong/Missing protocol"):
        verify_server_protocol("localhost:8080")


def test_get_processing_job_status(monkeypatch):
    response = Mock()
    response.json.return_value = {"state": "SUCCESS"}
    request_get = Mock(return_value=response)
    monkeypatch.setattr("ocrd_network.client_utils.request_get", request_get)
    result = get_ps_processing_job_status("http://server", "job-1")
    assert result == JobState.success
    request_get.assert_called_once_with(
        url="http://server/processor/job/job-1",
        headers={"accept": "application/json; charset=utf-8"}
    )


def test_post_processing_request(monkeypatch):
    response = Mock()
    response.json.return_value = {"job_id": "job-123"}
    request_post = Mock(return_value=response)
    monkeypatch.setattr("ocrd_network.client_utils.request_post", request_post)
    job_input = {"input_file_grps": ["DEFAULT"]}
    result = post_ps_processing_request("http://server", "ocrd-processor-test", job_input)
    assert result == "job-123"
    request_post.assert_called_once_with(
        url="http://server/processor/run/ocrd-processor-test",
        headers={"accept": "application/json; charset=utf-8"},
        json=job_input
    )


def test_post_workflow_request_uploads_and_closes_file(tmp_path, monkeypatch):
    workflow_file = tmp_path / "workflow.yml"
    workflow_file.write_text("steps: []")
    response = Mock()
    response.text = json.dumps({"job_id": "workflow-123"})
    request_post = Mock(return_value=response)
    monkeypatch.setattr("ocrd_network.client_utils.request_post", request_post)
    result = post_ps_workflow_request(
        "http://server",
        str(workflow_file),
        "/workspace/mets.xml",
        page_wise=True,
        callback_url="http://callback"
    )
    assert result == "workflow-123"
    args = request_post.call_args
    assert args.kwargs["url"] == (
        "http://server/workflow/run?mets_path=%2Fworkspace%2Fmets.xml"
        "&page_wise=True&workflow_callback_url=http%3A%2F%2Fcallback"
    )
    assert args.kwargs["files"]["workflow"].closed


def test_post_workflow_request_closes_file_when_request_fails(tmp_path, monkeypatch):
    workflow_file = tmp_path / "workflow.yml"
    workflow_file.write_text("steps: []")
    request_post = Mock(side_effect=RequestException("Connection failed"))
    monkeypatch.setattr("ocrd_network.client_utils.request_post", request_post)
    with pytest.raises(RequestException, match="Connection failed"):
        post_ps_workflow_request("http://server", str(workflow_file), "/workspace/mets.xml")
    uploaded_file = request_post.call_args.kwargs["files"]["workflow"]
    assert uploaded_file.closed


def test_post_workflow_request_accepts_workflow_content(monkeypatch):
    response = Mock()
    response.text = json.dumps({"job_id": "workflow-123"})
    request_post = Mock(return_value=response)
    monkeypatch.setattr("ocrd_network.client_utils.request_post", request_post)
    result = post_ps_workflow_request("http://server", "steps: []", "/workspace/mets.xml")
    assert result == "workflow-123"
    assert request_post.call_args.kwargs["files"] == {"workflow": "steps: []"}
