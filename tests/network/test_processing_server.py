from requests import get
from ocrd_utils.config import config

PROCESSING_SERVER_URL = config.PROCESSING_SERVER_URL


def test_processing_server_connectivity():
    test_url = f'{PROCESSING_SERVER_URL}/'
    response = get(test_url)
    assert response.status_code == 200, \
        f'Processing server is not reachable on: {test_url}, {response.status_code}'
    message = response.json()['message']
    assert message.startsWith('The home page of'), \
        f'Processing server home page message is corrupted'


# TODO: The processing workers are still not registered when deployed separately.
#  Fix that by extending the processing server.
def test_processing_server_deployed_processors():
    test_url = f'{PROCESSING_SERVER_URL}/processor'
    response = get(test_url)
    processors = response.json()
    assert response.status_code == 200, \
        f'Processing server is not reachable on: {test_url}, {response.status_code}'
    assert processors == [], f'Mismatch in deployed processors'
