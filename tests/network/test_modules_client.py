from unittest.mock import Mock
import pytest
from ocrd_network.client import Client


def test_client_uses_default_server_address(monkeypatch):
    monkeypatch.setattr(
        "ocrd_network.client.config.OCRD_NETWORK_SERVER_ADDR_PROCESSING",
        "http://default-server"
    )
    client = Client(None)
    assert client.server_addr_processing == "http://default-server"


def test_client_rejects_invalid_server_protocol():
    with pytest.raises(ValueError, match="Wrong/Missing protocol"):
        Client("localhost:8080")


def test_client_initializes_polling_configuration():
    client = Client("http://server", timeout=10, wait=3)
    assert client.polling_timeout == 10
    assert client.polling_wait == 3
    assert client.polling_tries == 3


def test_client_forwards_processing_request(monkeypatch):
    post_request = Mock(return_value="job-123")
    monkeypatch.setattr("ocrd_network.client.post_ps_processing_request", post_request)
    client = Client("http://server")
    job_input = {"input_file_grps": ["DEFAULT"]}
    result = client.send_processing_job_request("ocrd-processor-test", job_input)
    assert result == "job-123"
    post_request.assert_called_once_with(
        ps_server_host="http://server",
        processor="ocrd-processor-test",
        job_input=job_input
    )


def test_client_forwards_workflow_request(monkeypatch):
    post_request = Mock(return_value="workflow-123")
    monkeypatch.setattr("ocrd_network.client.post_ps_workflow_request", post_request)
    client = Client("http://server")
    result = client.send_workflow_job_request(
        path_to_wf="/workflow.yml",
        path_to_mets="/workspace/mets.xml",
        page_wise=True,
        callback_url="http://callback"
    )
    assert result == "workflow-123"
    post_request.assert_called_once_with(
        ps_server_host="http://server",
        path_to_wf="/workflow.yml",
        path_to_mets="/workspace/mets.xml",
        page_wise=True,
        callback_url="http://callback"
    )
