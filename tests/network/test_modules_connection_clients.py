from unittest.mock import Mock
import pytest
from paramiko import AutoAddPolicy
from ocrd_network.runtime_data.connection_clients import CustomDockerClient, create_docker_client, create_ssh_client


@pytest.mark.parametrize("password,keypath", [("", ""), ("password", "/path/to/key")])
def test_create_docker_client_invalid_credentials(password, keypath):
    with pytest.raises(ValueError):
        create_docker_client("host", "user", password, keypath)


def test_create_ssh_client_success(monkeypatch):
    ssh_client = Mock()
    monkeypatch.setattr("ocrd_network.runtime_data.connection_clients.SSHClient", Mock(return_value=ssh_client))
    result = create_ssh_client("host", "user", "password", "")
    assert result is ssh_client
    assert ssh_client.set_missing_host_key_policy.call_args.args[0] is AutoAddPolicy
    ssh_client.connect.assert_called_once_with(hostname="host", username="user", password="password", key_filename="")


def test_create_ssh_client_connection_error(monkeypatch):
    ssh_client = Mock()
    ssh_client.connect.side_effect = RuntimeError("Connection failed")
    monkeypatch.setattr("ocrd_network.runtime_data.connection_clients.SSHClient", Mock(return_value=ssh_client))
    with pytest.raises(Exception, match="Error creating SSHClient of host 'host'") as error:
        create_ssh_client("host", "user", "password", "")
    assert isinstance(error.value.__cause__, RuntimeError)


def test_create_docker_client_success(monkeypatch):
    api_client = Mock()
    api_client._retrieve_server_version.return_value = "1.44"
    adapter = Mock()
    monkeypatch.setattr("ocrd_network.runtime_data.connection_clients.APIClient", Mock(return_value=api_client))
    monkeypatch.setattr(CustomDockerClient, "CustomSshHttpAdapter", Mock(return_value=adapter))
    client = create_docker_client("host", "user", "password", "")
    assert client.api is api_client
    assert api_client._version == "1.44"
    api_client.mount.assert_called_once_with(prefix="http+docker://ssh", adapter=adapter)


def test_create_docker_client_closes_api_on_initialization_error(monkeypatch):
    api_client = Mock()
    api_client.mount.side_effect = RuntimeError("Mount failed")
    monkeypatch.setattr("ocrd_network.runtime_data.connection_clients.APIClient", Mock(return_value=api_client))
    monkeypatch.setattr(CustomDockerClient, "CustomSshHttpAdapter", Mock(return_value=Mock()))
    with pytest.raises(RuntimeError, match="Mount failed"):
        create_docker_client("host", "user", "password", "")
    api_client.close.assert_called_once()
