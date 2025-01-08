import json
from requests import get as request_get, post as request_post
from time import sleep
from .constants import JobState, NETWORK_PROTOCOLS


def _poll_endpoint_status(ps_server_host: str, job_id: str, job_type: str, tries: int, wait: int, print_state: bool = False) -> JobState:
    if job_type not in ["workflow", "processor"]:
        raise ValueError(f"Unknown job type '{job_type}', expected 'workflow' or 'processor'")
    job_state = JobState.unset
    while tries > 0:
        sleep(wait)
        if job_type == "processor":
            job_state = get_ps_processing_job_status(ps_server_host, job_id)
        if job_type == "workflow":
            job_state = get_ps_workflow_job_status(ps_server_host, job_id)
        if print_state:
            print(f"State of the {job_type} job {job_id}: {job_state}")
        if job_state == JobState.success or job_state == JobState.failed:
            break
        tries -= 1
    return job_state


def poll_job_status_till_timeout_fail_or_success(
    ps_server_host: str, job_id: str, tries: int, wait: int, print_state: bool = False) -> JobState:
    return _poll_endpoint_status(ps_server_host, job_id, "processor", tries, wait, print_state)


def poll_wf_status_till_timeout_fail_or_success(
    ps_server_host: str, job_id: str, tries: int, wait: int, print_state: bool = False) -> JobState:
    return _poll_endpoint_status(ps_server_host, job_id, "workflow", tries, wait, print_state)


def get_ps_deployed_processors(ps_server_host: str):
    request_url = f"{ps_server_host}/processor"
    response = request_get(url=request_url, headers={"accept": "application/json; charset=utf-8"})
    assert response.status_code == 200, f"Processing server: {request_url}, {response.status_code}"
    return response.json()


def get_ps_deployed_processor_ocrd_tool(ps_server_host: str, processor_name: str):
    request_url = f"{ps_server_host}/processor/info/{processor_name}"
    response = request_get(url=request_url, headers={"accept": "application/json; charset=utf-8"})
    assert response.status_code == 200, f"Processing server: {request_url}, {response.status_code}"
    return response.json()


def get_ps_processing_job_log(ps_server_host: str, processing_job_id: str):
    request_url = f"{ps_server_host}/processor/log/{processing_job_id}"
    response = request_get(url=request_url, headers={"accept": "application/json; charset=utf-8"})
    return response


def get_ps_processing_job_status(ps_server_host: str, processing_job_id: str) -> JobState:
    request_url = f"{ps_server_host}/processor/job/{processing_job_id}"
    response = request_get(url=request_url, headers={"accept": "application/json; charset=utf-8"})
    assert response.status_code == 200, f"Processing server: {request_url}, {response.status_code}"
    job_state = response.json()["state"]
    assert job_state
    return getattr(JobState, job_state.lower())

def get_ps_workflow_job_status(ps_server_host: str, workflow_job_id: str) -> JobState:
    request_url = f"{ps_server_host}/workflow/job-simple/{workflow_job_id}"
    response = request_get(url=request_url, headers={"accept": "application/json; charset=utf-8"})
    assert response.status_code == 200, f"Processing server: {request_url}, {response.status_code}"
    job_state = response.json()["state"]
    assert job_state
    return getattr(JobState, job_state.lower())


def post_ps_processing_request(ps_server_host: str, processor: str, job_input: dict) -> str:
    request_url = f"{ps_server_host}/processor/run/{processor}"
    response = request_post(
        url=request_url,
        headers={"accept": "application/json; charset=utf-8"},
        json=job_input
    )
    assert response.status_code == 200, f"Processing server: {request_url}, {response.status_code}"
    processing_job_id = response.json()["job_id"]
    assert processing_job_id
    return processing_job_id


def post_ps_workflow_request(
    ps_server_host: str,
    path_to_wf: str,
    path_to_mets: str,
    page_wise: bool = False,
) -> str:
    request_url = f"{ps_server_host}/workflow/run?mets_path={path_to_mets}&page_wise={'True' if page_wise else 'False'}"
    response = request_post(
        url=request_url,
        headers={"accept": "application/json; charset=utf-8"},
        files={"workflow": open(path_to_wf, "rb")}
    )
    # print(response.json())
    # print(response.__dict__)
    json_resp_raw = response.text
    # print(f'post_ps_workflow_request >> {response.status_code}')
    # print(f'post_ps_workflow_request >> {json_resp_raw}')
    assert response.status_code == 200, f"Processing server: {request_url}, {response.status_code}"
    wf_job_id = json.loads(json_resp_raw)["job_id"]
    assert wf_job_id
    return wf_job_id


def verify_server_protocol(address: str):
    for protocol in NETWORK_PROTOCOLS:
        if address.startswith(protocol):
            return
    raise ValueError(f"Wrong/Missing protocol in the server address: {address}, must be one of: {NETWORK_PROTOCOLS}")
