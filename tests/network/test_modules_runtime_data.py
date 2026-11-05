from unittest.mock import Mock
from paramiko import SSHClient
import pytest

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

    monkeypatch.setattr(
        "ocrd_network.runtime_data.hosts.create_ssh_client",
        lambda *args: ssh_client
    )
    monkeypatch.setattr(
        host, "_DataHost__stop_network_agent_resource_manager_server", lambda logger: None
    )

    def fail_stop(*args, **kwargs):
        raise RuntimeError("Simulated worker stop failure")

    monkeypatch.setattr(host, "_DataHost__stop_worker", fail_stop)

    with pytest.raises(RuntimeError, match="Simulated worker stop failure"):
        host.stop_workers(Mock())

    ssh_client.close.assert_called_once()
