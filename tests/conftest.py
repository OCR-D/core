from pytest import fixture
from pathlib import Path

pytest_plugins = [
    "tests.network.fixtures_mongodb",
    "tests.network.fixtures_rabbitmq"
]


@fixture(scope="session")
def docker_compose_file(pytestconfig):
    return Path(str(pytestconfig.rootdir), "tests", "network", "docker-compose.yml")
