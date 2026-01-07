from json import loads
from pathlib import Path
from requests import get as request_get
from src.ocrd_network.client_utils import (
    poll_job_status_till_timeout_fail_or_success, poll_wf_status_till_timeout_fail_or_success,
    post_ps_processing_request, post_ps_workflow_request, get_ps_processing_job_log, get_ps_workflow_job_status)
from src.ocrd_network.constants import JobState
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


def test_processing_server_deployed_processors():
    test_url = f"{PROCESSING_SERVER_URL}/processor"
    response = request_get(test_url)
    processors = response.json()
    assert response.status_code == 200, f"Processing server: {test_url}, {response.status_code}"
    assert "ocrd-dummy" in processors


def test_processing_server_processing_request():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    input_file_grp = "OCR-D-IMG"
    output_file_grp = f"OCR-D-DUMMY-TEST-PS"
    test_processing_job_input = {
        "path_to_mets": path_to_mets,
        "input_file_grps": [input_file_grp],
        "output_file_grps": [output_file_grp],
        "parameters": {}
    }
    test_processor = "ocrd-dummy"
    process_job_id = post_ps_processing_request(PROCESSING_SERVER_URL, test_processor, test_processing_job_input)
    job_end_status = poll_job_status_till_timeout_fail_or_success(PROCESSING_SERVER_URL, process_job_id, tries=10, wait=10)
    print(f"\nChecking the log file of the job")
    job_log = get_ps_processing_job_log(PROCESSING_SERVER_URL, process_job_id)
    print(f"\nThe job log file returned:\n{job_log.content.decode('utf-8')}")
    assert job_end_status == JobState.success

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
    job_end_status = poll_wf_status_till_timeout_fail_or_success(PROCESSING_SERVER_URL, wf_job_id, tries=10, wait=10)

    print(f"\nChecking the dictionary of processing jobs")
    response = get_ps_workflow_job_status(PROCESSING_SERVER_URL, wf_job_id)
    processing_jobs = loads(response.content.decode("utf-8"))
    print(f"processing_jobs: {processing_jobs}")
    if "failed-processor-tasks" in processing_jobs:
        failed_processor_tasks: dict = processing_jobs["failed-processor-tasks"]
        for failed_processor, failed_job_ids in failed_processor_tasks.items():
            print(f"\nChecking {failed_processor} log files")
            for failed_job_id in failed_job_ids:
                print(f"\nChecking the log file of failed job id: {failed_job_id['job_id']}")
                job_log = get_ps_processing_job_log(PROCESSING_SERVER_URL, failed_job_id['job_id'])
                print(f"\nThe job log file returned:\n{job_log.content.decode('utf-8')}")

    assert job_end_status == JobState.success

    # Check the existence of the results locally
    # The output file groups are defined in the `path_to_dummy_wf`
    # assert Path(assets.path_to(f"{workspace_root}/OCR-D-DUMMY1")).exists()
    # assert Path(assets.path_to(f"{workspace_root}/OCR-D-DUMMY2")).exists()
    # assert Path(assets.path_to(f"{workspace_root}/OCR-D-DUMMY3")).exists()
