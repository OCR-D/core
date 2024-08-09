from pathlib import Path
from requests import get as request_get
from src.ocrd_network.client_utils import (
    poll_job_status_till_timeout_fail_or_success, poll_wf_status_till_timeout_fail_or_success,
    post_ps_processing_request, post_ps_workflow_request)
from src.ocrd_network.constants import AgentType, JobState
from src.ocrd_network.logging_utils import get_processing_job_logging_file_path
from tests.base import assets
from tests.network.config import test_config


PROCESSING_SERVER_URL = test_config.PROCESSING_SERVER_URL


def test_processing_server_connectivity():
    test_url = f"{PROCESSING_SERVER_URL}/"
    response = request_get(test_url)
    assert response.status_code == 200, f"Processing server is not reachable on: {test_url}, {response.status_code}"
    message = response.json()["message"]
    assert message.startswith("The home page of"), f"Processing server home page message is corrupted"


# TODO: The processing workers are still not registered when deployed separately.
#  Fix that by extending the processing server.
def test_processing_server_deployed_processors():
    test_url = f"{PROCESSING_SERVER_URL}/processor"
    response = request_get(test_url)
    processors = response.json()
    assert response.status_code == 200, f"Processing server: {test_url}, {response.status_code}"
    assert processors == [], f"Mismatch in deployed processors"


def test_processing_server_processing_request():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    input_file_grp = "OCR-D-IMG"
    output_file_grp = f"OCR-D-DUMMY-TEST-PS"
    test_processing_job_input = {
        "path_to_mets": path_to_mets,
        "input_file_grps": [input_file_grp],
        "output_file_grps": [output_file_grp],
        "agent_type": AgentType.PROCESSING_WORKER,
        "parameters": {}
    }
    test_processor = "ocrd-dummy"
    process_job_id = post_ps_processing_request(PROCESSING_SERVER_URL, test_processor, test_processing_job_input)
    job_state = poll_job_status_till_timeout_fail_or_success(PROCESSING_SERVER_URL, process_job_id, tries=10, wait=10)
    assert job_state == JobState.success

    # Check the existence of the results locally
    # assert Path(assets.path_to(f"{workspace_root}/{output_file_grp}")).exists()
    # path_to_log_file = get_processing_job_logging_file_path(job_id=processing_job_id)
    # assert Path(path_to_log_file).exists()


def test_processing_server_workflow_request():
    # Note: the used workflow path is volume mapped
    path_to_dummy_wf = "/ocrd-data/assets/dummy-workflow.txt"
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    wf_job_id = post_ps_workflow_request(PROCESSING_SERVER_URL, path_to_dummy_wf, path_to_mets)
    job_state = poll_wf_status_till_timeout_fail_or_success(PROCESSING_SERVER_URL, wf_job_id, tries=10, wait=10)
    assert job_state == JobState.success

    # Check the existence of the results locally
    # The output file groups are defined in the `path_to_dummy_wf`
    # assert Path(assets.path_to(f"{workspace_root}/OCR-D-DUMMY1")).exists()
    # assert Path(assets.path_to(f"{workspace_root}/OCR-D-DUMMY2")).exists()
    # assert Path(assets.path_to(f"{workspace_root}/OCR-D-DUMMY3")).exists()
