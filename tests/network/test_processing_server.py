from time import sleep
from requests import get, post
from ocrd_utils.config import config
from ocrd_network import NETWORK_AGENT_WORKER
from ocrd_network.models import StateEnum
from tests.base import assets

PROCESSING_SERVER_URL = config.PROCESSING_SERVER_URL


def poll_till_timeout_fail_or_success(test_url: str, tries: int, wait: int) -> StateEnum:
    job_state = StateEnum.unset
    while tries > 0:
        sleep(wait)
        response = get(url=test_url)
        assert response.status_code == 200, f"Processing server: {test_url}, {response.status_code}"
        job_state = response.json()["state"]
        if job_state == StateEnum.success or job_state == StateEnum.failed:
            break
        tries -= 1
    return job_state


def test_processing_server_connectivity():
    test_url = f'{PROCESSING_SERVER_URL}/'
    response = get(test_url)
    assert response.status_code == 200, \
        f'Processing server is not reachable on: {test_url}, {response.status_code}'
    message = response.json()['message']
    assert message.startswith('The home page of'), \
        f'Processing server home page message is corrupted'


# TODO: The processing workers are still not registered when deployed separately.
#  Fix that by extending the processing server.
def test_processing_server_deployed_processors():
    test_url = f'{PROCESSING_SERVER_URL}/processor'
    response = get(test_url)
    processors = response.json()
    assert response.status_code == 200, \
        f'Processing server: {test_url}, {response.status_code}'
    assert processors == [], f'Mismatch in deployed processors'


def test_processing_server_processing_request():
    path_to_mets = assets.path_to('kant_aufklaerung_1784/data/mets.xml')
    test_processing_job_input = {
        "path_to_mets": path_to_mets,
        "input_file_grps": ['OCR-D-IMG'],
        "output_file_grps": ['OCR-D-DUMMY'],
        "agent_type": NETWORK_AGENT_WORKER,
        "parameters": {}
    }
    test_processor = 'ocrd-dummy'
    test_url = f'{PROCESSING_SERVER_URL}/processor/run/{test_processor}'
    response = post(
        url=test_url,
        headers={"accept": "application/json"},
        json=test_processing_job_input
    )
    # TODO: Remove print before finalizing the PR
    print(response.json())
    assert response.status_code == 200, \
        f'Processing server: {test_url}, {response.status_code}'
    processing_job_id = response.json()["job_id"]
    assert processing_job_id

    job_state = poll_till_timeout_fail_or_success(
        test_url=f"{PROCESSING_SERVER_URL}/processor/job/{processing_job_id}",
        tries=10,
        wait=10
    )
    assert job_state == StateEnum.success


def test_processing_server_workflow_request():
    # Note: the used workflow path is volume mapped
    path_to_dummy_wf = "/ocrd-data/assets/dummy-workflow.txt"
    path_to_mets = assets.path_to('kant_aufklaerung_1784/data/mets.xml')

    # submit the workflow job
    test_url = f"{PROCESSING_SERVER_URL}/workflow/run?mets_path={path_to_mets}&page_wise=True"
    response = post(
        url=test_url,
        headers={"accept": "application/json"},
        files={"workflow": open(path_to_dummy_wf, 'rb')}
    )
    # TODO: Remove print before finalizing the PR
    print(response.json())
    assert response.status_code == 200, f"Processing server: {test_url}, {response.status_code}"
    wf_job_id = response.json()["job_id"]
    assert wf_job_id

    job_state = poll_till_timeout_fail_or_success(
        test_url=f"{PROCESSING_SERVER_URL}/workflow/job-simple/{wf_job_id}",
        tries=30,
        wait=10
    )
    assert job_state == StateEnum.success
