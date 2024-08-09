from pathlib import Path
from src.ocrd_network.constants import AgentType, JobState
from tests.base import assets
from tests.network.config import test_config
from ocrd_network.client import Client

PROCESSING_SERVER_URL = test_config.PROCESSING_SERVER_URL


def test_client_processing_processor():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    client = Client(server_addr_processing=PROCESSING_SERVER_URL)
    req_params = {
        "path_to_mets": path_to_mets,
        "description": "OCR-D Network client request",
        "input_file_grps": ["OCR-D-IMG"],
        "output_file_grps": ["OCR-D-DUMMY-TEST-CLIENT"],
        "parameters": {},
        "agent_type": AgentType.PROCESSING_WORKER
    }
    processing_job_id = client.send_processing_job_request(processor_name="ocrd-dummy", req_params=req_params)
    assert processing_job_id
    print(f"Processing job id: {processing_job_id}")
    assert JobState.success == client.poll_job_status_till_timeout_fail_or_success(processing_job_id)


def test_client_processing_workflow():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    # TODO: Improve the path resolution
    path_to_dummy_wf = f"{Path(__file__).parent.resolve()}/dummy-workflow.txt"
    client = Client(server_addr_processing=PROCESSING_SERVER_URL)
    wf_job_id = client.send_workflow_job_request(path_to_dummy_wf, path_to_mets)
    print(f"Workflow job id: {wf_job_id}")
    assert JobState.success == client.poll_wf_status_till_timeout_fail_or_success(wf_job_id)
