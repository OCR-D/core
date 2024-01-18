from requests import get
from ocrd_utils.config import config

PROCESSING_SERVER_URL = config.PROCESSING_SERVER_URL


def test_processing_server_connectivity():
    test_url = f'{PROCESSING_SERVER_URL}/'
    response = get(test_url)
    assert response.status_code == 200, \
        f'Processing server is not reachable on: {test_url}, {response.status_code}'


def _test_processing_server_deployed_processors():
    test_url = f'{PROCESSING_SERVER_URL}/processor'
    response = get(test_url)
    assert response.status_code == 200, \
        f'Processing server is not reachable on: {test_url}, {response.status_code}'
