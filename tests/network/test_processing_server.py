from requests import get, post
from ocrd_utils.config import config
from ocrd_network import NETWORK_AGENT_WORKER

PROCESSING_SERVER_URL = config.PROCESSING_SERVER_URL


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


# TODO: Still failing test with internal error 500
def _test_processing_server_processing_request():
    # Note: the used path is volume mapped
    test_processing_job_input = {
        "path_to_mets": "/tmp/assets/kant_aufklaerung_1784/data/mets.xml",
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
    assert response.status_code == 200, \
        f'Processing server: {test_url}, {response.status_code}'


def test_processing_server_workflow_request():
    # Note: the used paths are volume mapped
    path_to_mets = "/tmp/assets/kant_aufklaerung_1784/data/mets.xml"
    path_to_dummy_wf = "/tmp/assets/dummy-workflow.txt"

    test_url = f"{PROCESSING_SERVER_URL}/workflow?mets_path={path_to_mets}&page_wise=False"
    response = post(
        url=test_url,
        files={"workflow": open(path_to_dummy_wf, 'rb')}
    )
    assert response.status_code == 201, \
        f'Processing server: {test_url}, {response.status_code}'

    # TODO: Check workflow status here
