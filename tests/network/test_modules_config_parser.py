import pytest

from ocrd_network.runtime_data.config_parser import parse_mongodb_data, parse_rabbitmq_data
from ocrd_network.runtime_data.network_services import DataMongoDB, DataRabbitMQ


@pytest.mark.parametrize(
    "parse_func, expected_type",
    [
        (parse_mongodb_data, DataMongoDB),
        (parse_rabbitmq_data, DataRabbitMQ),
    ],
)
def test_parse_network_service_data(parse_func, expected_type):
    config = {
        "address": "localhost",
        "port": "1234",
        "ssh": {
            "username": "ssh-user",
            "path_to_privkey": "/path/to/key",
            "password": "ssh-password",
        },
        "credentials": {
            "username": "service-user",
            "password": "service-password",
        },
        "skip_deployment": True
    }

    result = parse_func(config)

    assert isinstance(result, expected_type)
    assert result.host == "localhost"
    assert result.port == 1234
    assert result.ssh_username == "ssh-user"
    assert result.ssh_keypath == "/path/to/key"
    assert result.ssh_password == "ssh-password"
    assert result.cred_username == "service-user"
    assert result.cred_password == "service-password"
    assert result.skip_deployment is True


@pytest.mark.parametrize("parse_func", [parse_mongodb_data, parse_rabbitmq_data])
def test_parse_network_service_data_with_optional_fields_missing(parse_func):
    config = {"address": "localhost", "port": "1234"}
    result = parse_func(config)

    assert result.host == "localhost"
    assert result.port == 1234
    assert result.ssh_username is None
    assert result.ssh_keypath is None
    assert result.ssh_password is None
    assert result.cred_username is None
    assert result.cred_password is None
    assert result.skip_deployment is False
