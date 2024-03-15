from requests import get, post
from time import sleep
from src.ocrd_network.models import StateEnum


def poll_job_till_timeout_fail_or_success(
    test_url: str,
    tries: int = 10,
    wait: int = 10
) -> StateEnum:
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


def post_ps_processing_request(ps_server_host: str, test_processor: str, test_job_input: dict) -> str:
    test_url = f"{ps_server_host}/processor/run/{test_processor}"
    response = post(
        url=test_url,
        headers={"accept": "application/json"},
        json=test_job_input
    )
    # print(response.json())
    assert response.status_code == 200, \
        f"Processing server: {test_url}, {response.status_code}"
    processing_job_id = response.json()["job_id"]
    assert processing_job_id
    return processing_job_id


# TODO: Can be extended to include other parameters such as page_wise
def post_ps_workflow_request(ps_server_host: str, path_to_test_wf: str, path_to_test_mets: str) -> str:
    test_url = f"{ps_server_host}/workflow/run?mets_path={path_to_test_mets}&page_wise=True"
    response = post(
        url=test_url,
        headers={"accept": "application/json"},
        files={"workflow": open(path_to_test_wf, "rb")}
    )
    # print(response.json())
    assert response.status_code == 200, f"Processing server: {test_url}, {response.status_code}"
    wf_job_id = response.json()["job_id"]
    assert wf_job_id
    return wf_job_id
