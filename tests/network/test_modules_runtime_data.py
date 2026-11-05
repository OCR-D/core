from unittest.mock import Mock
from paramiko import SSHClient
import pytest

from ocrd_network.processing_server.server import ProcessingServer
from ocrd_network.runtime_data.connection_clients import CustomDockerClient
from ocrd_network.runtime_data.deployer import Deployer
from ocrd_network.runtime_data.hosts import DataHost
from ocrd_network.runtime_data.network_agents import deploy_agent_native_get_pid_hack
from ocrd_network.runtime_data.network_services import DataMongoDB, DataRabbitMQ


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


def test_deploy_agent_native_extracts_pid_and_closes_channel():
    ssh_client = Mock()
    channel = Mock()
    stdin = Mock()
    stdout = Mock()

    ssh_client.invoke_shell.return_value = channel
    channel.makefile.side_effect = [stdin, stdout]
    stdout.read.return_value = b"command output xyz12345xyz"

    pid = deploy_agent_native_get_pid_hack(Mock(), ssh_client, "start-worker")

    assert pid == "12345"
    stdin.close.assert_called_once()
    stdout.close.assert_called_once()
    channel.close.assert_called_once()


def test_deploy_agent_native_closes_channel_when_pid_is_missing():
    ssh_client = Mock()
    channel = Mock()
    stdin = Mock()
    stdout = Mock()

    ssh_client.invoke_shell.return_value = channel
    channel.makefile.side_effect = [stdin, stdout]
    stdout.read.return_value = b"command failed"

    with pytest.raises(RuntimeError, match="Could not determine the PID"):
        deploy_agent_native_get_pid_hack(Mock(), ssh_client, "start-worker")

    stdin.close.assert_called_once()
    stdout.close.assert_called_once()
    channel.close.assert_called_once()


def test_mongodb_url_encodes_credentials():
    service = DataMongoDB(
        host="localhost",
        port=27017,
        ssh_username=None,
        ssh_keypath=None,
        ssh_password=None,
        cred_username="user@name",
        cred_password="p:a/ss#word",
        skip_deployment=True
    )

    assert service.service_url == (
        "mongodb://user%40name:p%3Aa%2Fss%23word@localhost:27017"
    )


def test_rabbitmq_url_encodes_credentials_and_default_vhost():
    service = DataRabbitMQ(
        host="localhost",
        port=5672,
        ssh_username=None,
        ssh_keypath=None,
        ssh_password=None,
        cred_username="user@name",
        cred_password="p:a/ss#word",
        skip_deployment=True
    )

    assert service.service_url == (
        "amqp://user%40name:p%3Aa%2Fss%23word@localhost:5672/%2F"
    )


def test_rabbitmq_url_encodes_custom_vhost():
    service = DataRabbitMQ(
        host="localhost",
        port=5672,
        ssh_username=None,
        ssh_keypath=None,
        ssh_password=None,
        cred_username="worker",
        cred_password="secret",
        skip_deployment=True,
        vhost="team/name"
    )

    assert service.service_url == "amqp://worker:secret@localhost:5672/team%2Fname"


def test_stop_all_attempts_every_service_when_cleanup_fails():
    deployer = Deployer.__new__(Deployer)
    deployer.log = Mock()
    deployer.stop_workers = Mock(side_effect=RuntimeError("Worker shutdown failed"))
    deployer.stop_mongodb = Mock()
    deployer.stop_rabbitmq = Mock()

    with pytest.raises(RuntimeError, match="Worker shutdown failed"):
        deployer.stop_all()

    deployer.stop_workers.assert_called_once()
    deployer.stop_mongodb.assert_called_once()
    deployer.stop_rabbitmq.assert_called_once()


def test_start_preserves_startup_error_when_cleanup_fails():
    server = ProcessingServer.__new__(ProcessingServer)
    server.log = Mock()
    server.deployer = Mock()

    startup_error = RuntimeError("RabbitMQ deployment failed")
    cleanup_error = RuntimeError("Worker shutdown failed")

    server.deployer.deploy_rabbitmq.side_effect = startup_error
    server.deployer.stop_all.side_effect = cleanup_error

    with pytest.raises(RuntimeError) as exc_info:
        server.start()

    assert exc_info.value is startup_error
    server.deployer.stop_all.assert_called_once()


def test_stop_workers_attempts_every_host_when_cleanup_fails():
    deployer = Deployer.__new__(Deployer)
    deployer.log = Mock()

    first_host = Mock()
    second_host = Mock()
    third_host = Mock()
    first_error = RuntimeError("First host shutdown failed")

    first_host.stop_workers.side_effect = first_error
    deployer.data_hosts = [first_host, second_host, third_host]

    with pytest.raises(RuntimeError) as exc_info:
        deployer.stop_workers()

    assert exc_info.value is first_error
    first_host.stop_workers.assert_called_once_with(logger=deployer.log)
    second_host.stop_workers.assert_called_once_with(logger=deployer.log)
    third_host.stop_workers.assert_called_once_with(logger=deployer.log)
