from time import sleep
from requests import get, post
from src.ocrd_network.models import StateEnum
from tests.base import assets
from tests.network.config import test_config

PROCESSING_SERVER_URL = test_config.PROCESSING_SERVER_URL


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


def test_ocrd_all_workflow():
    # This tests is supposed to with ocrd_all not with just core on its own
    # Note: the used workflow path is volume mapped
    path_to_wf = "/ocrd-data/assets/ocrd_all-test-workflow.txt"
    path_to_mets = "/data/mets.xml"

    # submit the workflow job
    test_url = f"{PROCESSING_SERVER_URL}/workflow/run?mets_path={path_to_mets}&page_wise=True"
    response = post(
        url=test_url,
        headers={"accept": "application/json"},
        files={"workflow": open(path_to_wf, 'rb')}
    )
    # print(response.json())
    assert response.status_code == 200, (
        f"Processing server: {test_url}, {response.status_code}. "
        f"Response text: {response.text}"
    )
    wf_job_id = response.json()["job_id"]
    assert wf_job_id

    job_state = poll_till_timeout_fail_or_success(
        test_url=f"{PROCESSING_SERVER_URL}/workflow/job-simple/{wf_job_id}",
        tries=30,
        wait=10
    )
    assert job_state == StateEnum.success
