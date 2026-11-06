from unittest.mock import Mock, patch

import requests
from ocrd_network.utils import is_url_responsive


@patch("ocrd_network.utils.requests_get")
def test_is_url_responsive_success(mock_get):
    mock_get.return_value = Mock(status_code=200)
    assert is_url_responsive("http://localhost", tries=3) is True
    mock_get.assert_called_once()


@patch("ocrd_network.utils.sleep")
@patch("ocrd_network.utils.requests_get")
def test_is_url_responsive_retries_after_exception(mock_get, mock_sleep):
    mock_get.side_effect = [requests.ConnectionError(), Mock(status_code=200)]
    assert is_url_responsive("http://localhost", tries=3) is True
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once()


@patch("ocrd_network.utils.sleep")
@patch("ocrd_network.utils.requests_get")
def test_is_url_responsive_returns_false_after_failures(mock_get, mock_sleep):
    mock_get.side_effect = requests.ConnectionError()
    assert is_url_responsive("http://localhost", tries=3) is False
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2


@patch("ocrd_network.utils.sleep")
@patch("ocrd_network.utils.requests_get")
def test_is_url_responsive_retries_after_non_200(mock_get, mock_sleep):
    mock_get.side_effect = [Mock(status_code=503), Mock(status_code=200)]
    assert is_url_responsive("http://localhost", tries=3) is True
    assert mock_get.call_count == 2
