from pathlib import Path
from src.ocrd_network.constants import JobState
from tests.base import assets
from tests.network.config import test_config
from ocrd_network.client import Client

PROCESSING_SERVER_URL = test_config.PROCESSING_SERVER_URL
timeout = test_config.OCRD_NETWORK_CLIENT_POLLING_TIMEOUT
wait = test_config.OCRD_NETWORK_CLIENT_POLLING_SLEEP


def test_client_processing_processor():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    client = Client(PROCESSING_SERVER_URL, timeout, wait)
    req_params = {
        "path_to_mets": path_to_mets,
        "description": "OCR-D Network client request",
        "input_file_grps": ["OCR-D-IMG"],
        "output_file_grps": ["OCR-D-DUMMY-TEST-CLIENT"],
        "parameters": {},
    }
    processing_job_id = client.send_processing_job_request(processor_name="ocrd-dummy", req_params=req_params)
    assert processing_job_id
    print(f"Processing job id: {processing_job_id}")
    assert JobState.success == client.poll_job_status(processing_job_id)


def test_client_processing_workflow():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    # TODO: Improve the path resolution
    path_to_dummy_wf = f"{Path(__file__).parent.resolve()}/dummy-workflow.txt"
    client = Client(PROCESSING_SERVER_URL, timeout, wait)
    wf_job_id = client.send_workflow_job_request(path_to_dummy_wf, path_to_mets)
    print(f"Workflow job id: {wf_job_id}")
    assert JobState.success == client.poll_workflow_status(wf_job_id)
