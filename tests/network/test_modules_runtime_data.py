from unittest.mock import Mock
from paramiko import SSHClient
import pytest

from ocrd_network.runtime_data.connection_clients import CustomDockerClient
from ocrd_network.runtime_data.hosts import DataHost


def test_worker_instances_are_independent():
    host = DataHost(
        host="localhost",
        username="user",
        password="password",
        keypath="",
        workers=[
            {
                "name": "ocrd-example",
                "number_of_instance": 3,
                "deploy_type": "native"
            }
        ],
        servers=[]
    )

    workers = host.workers_native

    assert len(workers) == 3
    assert workers[0] is not workers[1]
    assert workers[1] is not workers[2]
    assert workers[0] is not workers[2]

    workers[0].pid = "123"

    assert workers[0].pid == "123"
    assert workers[1].pid is None
    assert workers[2].pid is None


def test_ssh_client_is_closed_when_worker_deployment_fails(monkeypatch):
    host = DataHost(
        host="localhost",
        username="user",
        password="password",
        keypath="",
        workers=[{"name": "ocrd-example", "number_of_instance": 1}],
        servers=[]
    )
    ssh_client = Mock(spec=SSHClient)

    monkeypatch.setattr("ocrd_network.runtime_data.hosts.create_ssh_client", lambda *args: ssh_client)
    monkeypatch.setattr(host, "_DataHost__deploy_network_agent_resource_manager_server", lambda logger: None)

    def fail_deployment(*args, **kwargs):
        raise RuntimeError("Simulated deployment failure")

    monkeypatch.setattr(host, "_DataHost__deploy_all_workers", fail_deployment)

    with pytest.raises(RuntimeError, match="Simulated deployment failure"):
        host.deploy_workers(Mock(), "mongodb://localhost", "amqp://localhost")

    ssh_client.close.assert_called_once()


def test_ssh_client_is_closed_when_worker_stop_fails(monkeypatch):
    host = DataHost(
        host="localhost",
        username="user",
        password="password",
        keypath="",
        workers=[{"name": "ocrd-example", "number_of_instance": 1}],
        servers=[]
    )
    ssh_client = Mock(spec=SSHClient)

    monkeypatch.setattr("ocrd_network.runtime_data.hosts.create_ssh_client", lambda *args: ssh_client)
    monkeypatch.setattr(host, "_DataHost__stop_network_agent_resource_manager_server", lambda logger: None)

    def fail_stop(*args, **kwargs):
        raise RuntimeError("Simulated worker stop failure")

    monkeypatch.setattr(host, "_DataHost__stop_worker", fail_stop)

    with pytest.raises(RuntimeError, match="Simulated worker stop failure"):
        host.stop_workers(Mock())

    ssh_client.close.assert_called_once()


@pytest.mark.parametrize(
    "kwargs, error_message",
    [
        ({}, "Missing credentials"),
        ({"password": "secret", "keypath": "/path/to/key"}, "Conflicting credentials")
    ]
)
def test_docker_client_rejects_invalid_credentials(kwargs, error_message):
    with pytest.raises(ValueError, match=error_message):
        CustomDockerClient(user="user", host="localhost", **kwargs)


def test_custom_docker_client_detects_version_after_mounting_adapter(monkeypatch):
    api = Mock()
    adapter = Mock()
    api_client_kwargs = {}

    def create_api_client(**kwargs):
        api_client_kwargs.update(kwargs)
        return api

    def retrieve_server_version():
        assert api.mount.called, "Custom SSH adapter must be mounted before version detection"
        return "1.42"

    api._retrieve_server_version.side_effect = retrieve_server_version

    monkeypatch.setattr("ocrd_network.runtime_data.connection_clients.APIClient", create_api_client)
    monkeypatch.setattr(
        CustomDockerClient,
        "CustomSshHttpAdapter",
        staticmethod(lambda **kwargs: adapter)
    )

    client = CustomDockerClient(user="user", host="localhost", password="secret")
    assert api_client_kwargs["version"] == "1.44"
    api.mount.assert_called_once_with(prefix="http+docker://ssh", adapter=adapter)
    api._retrieve_server_version.assert_called_once()
    assert api._version == "1.42"
    assert client.api is api


def test_custom_docker_client_closes_api_when_version_detection_fails(monkeypatch):
    api = Mock()
    adapter = Mock()

    monkeypatch.setattr("ocrd_network.runtime_data.connection_clients.APIClient", lambda **kwargs: api)
    monkeypatch.setattr(
        CustomDockerClient,
        "CustomSshHttpAdapter",
        staticmethod(lambda **kwargs: adapter)
    )

    api._retrieve_server_version.side_effect = RuntimeError("Version detection failed")
    with pytest.raises(RuntimeError, match="Version detection failed"):
        CustomDockerClient(user="user", host="localhost", password="secret")
    api.close.assert_called_once()
