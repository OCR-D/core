"""
Unit tests for RabbitMQ helper functions.
These tests use mocks exclusively and do not require a running RabbitMQ server.
"""

from unittest.mock import MagicMock, call

import pytest
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker
from requests.exceptions import HTTPError, RequestException

from ocrd_network.rabbitmq_utils import helpers


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def rmq_data():
    return {
        "host": "rabbitmq.example",
        "port": 5672,
        "vhost": "/",
        "username": "test-user",
        "password": "test-password"
    }


# ---------------------------------------------------------------------------
# Connection handling
# ---------------------------------------------------------------------------

def test_connect_client_retries_and_returns_client(
    monkeypatch, logger, rmq_data
):
    client = MagicMock()
    client.authenticate_and_connect.side_effect = [AMQPConnectionError(), None]
    factory = MagicMock(return_value=client)
    sleep = MagicMock()

    monkeypatch.setattr(helpers, "RMQConsumer", factory)
    monkeypatch.setattr(helpers, "sleep", sleep)

    result = helpers.__connect_rabbitmq_client(logger, "consumer", rmq_data, attempts=2, delay=0)

    assert result is client
    assert factory.call_count == 2
    assert client.authenticate_and_connect.call_args_list == [
        call(username=rmq_data["username"], password=rmq_data["password"]),
        call(username=rmq_data["username"], password=rmq_data["password"])
    ]

    sleep.assert_called_once_with(0)


def test_connect_client_raises_after_retry_exhaustion(
    monkeypatch, logger, rmq_data
):
    client = MagicMock()
    client.authenticate_and_connect.side_effect = AMQPConnectionError()

    factory = MagicMock(return_value=client)
    sleep = MagicMock()

    monkeypatch.setattr(helpers, "RMQPublisher", factory)
    monkeypatch.setattr(helpers, "sleep", sleep)

    with pytest.raises(RuntimeError, match="Failed to establish connection"):
        helpers.__connect_rabbitmq_client(logger, "publisher", rmq_data, attempts=3, delay=0)

    assert factory.call_count == 3
    assert client.authenticate_and_connect.call_count == 3
    assert sleep.call_count == 3


def test_connect_client_rejects_invalid_type_without_retrying(
    monkeypatch, logger, rmq_data
):
    sleep = MagicMock()
    monkeypatch.setattr(helpers, "sleep", sleep)
    with pytest.raises(RuntimeError, match="client type"):
        helpers.__connect_rabbitmq_client(logger, "unsupported", rmq_data, attempts=4, delay=0)
    sleep.assert_not_called()


def test_connect_client_reports_missing_connection_data(
    logger, rmq_data
):
    malformed_data = dict(rmq_data)
    del malformed_data["password"]
    with pytest.raises(Exception, match="Failed to parse RabbitMQ connection data"):
        helpers.__connect_rabbitmq_client(logger, "consumer", malformed_data)


# ---------------------------------------------------------------------------
# Queue existence
# ---------------------------------------------------------------------------

def test_check_if_queue_exists_returns_false_without_connecting(logger, rmq_data, monkeypatch):
    connect = MagicMock()
    monkeypatch.setattr(helpers, "connect_rabbitmq_publisher", connect)
    assert helpers.check_if_queue_exists(logger, rmq_data, None) is False
    connect.assert_not_called()


def test_check_if_queue_exists_returns_true_and_closes_publisher(
    logger, rmq_data, monkeypatch
):
    publisher = MagicMock()
    monkeypatch.setattr(helpers, "connect_rabbitmq_publisher", MagicMock(return_value=publisher))
    assert helpers.check_if_queue_exists(logger, rmq_data, "worker-a") is True
    publisher.create_queue.assert_called_once_with("worker-a", passive=True)
    publisher.close_connection.assert_called_once_with()


def test_check_if_queue_exists_returns_false_and_closes_publisher(logger, rmq_data, monkeypatch):
    publisher = MagicMock()
    publisher.create_queue.side_effect = ChannelClosedByBroker(404, "NOT_FOUND")
    monkeypatch.setattr(helpers, "connect_rabbitmq_publisher", MagicMock(return_value=publisher))
    assert helpers.check_if_queue_exists(logger, rmq_data, "missing-worker") is False
    publisher.close_connection.assert_called_once_with()


# ---------------------------------------------------------------------------
# RabbitMQ HTTP API
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "exception",
    [
        HTTPError("HTTP 500"),
        RequestException("request failed")
    ],
)
def test_get_message_queues_returns_empty_list_on_http_errors(
    monkeypatch, logger, rmq_data, exception
):
    response = MagicMock()
    response.status_code = 500
    response.text = "Internal Server Error"
    response.raise_for_status.side_effect = exception
    monkeypatch.setattr(helpers, "get", MagicMock(return_value=response))
    assert helpers.get_message_queues(logger, rmq_data) == []


def test_get_message_queues_returns_empty_list_when_request_raises(
    monkeypatch, logger, rmq_data
):
    monkeypatch.setattr(helpers, "get", MagicMock(side_effect=RequestException("network unavailable")))
    assert helpers.get_message_queues(logger, rmq_data) == []


def test_get_message_queues_returns_queue_names(monkeypatch, logger, rmq_data):
    response = MagicMock()
    response.json.return_value = [
        {"name": "queue-a"},
        {"name": "queue-b"}
    ]
    monkeypatch.setattr(helpers, "get", MagicMock(return_value=response))
    assert helpers.get_message_queues(logger, rmq_data) == ["queue-a", "queue-b"]


# ---------------------------------------------------------------------------
# RabbitMQ availability
# ---------------------------------------------------------------------------

def test_verify_rabbitmq_available_closes_temporary_publisher(monkeypatch, logger):
    publisher = MagicMock()
    monkeypatch.setattr(helpers, "verify_and_parse_mq_uri", MagicMock(return_value={"host": "rabbitmq.example"}))
    monkeypatch.setattr(helpers, "connect_rabbitmq_publisher", MagicMock(return_value=publisher))
    helpers.verify_rabbitmq_available(logger, "amqp://example")
    publisher.close_connection.assert_called_once_with()


def test_connect_publisher_closes_if_confirmation_setup_fails(
    monkeypatch, logger, rmq_data
):
    publisher = MagicMock()
    publisher.enable_delivery_confirmations.side_effect = (RuntimeError("confirmation setup failed"))
    monkeypatch.setattr(helpers, "__connect_rabbitmq_client", MagicMock(return_value=publisher))
    with pytest.raises(RuntimeError, match="confirmation setup failed"):
        helpers.connect_rabbitmq_publisher(logger, rmq_data, enable_acks=True)
    publisher.close_connection.assert_called_once_with()
