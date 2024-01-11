from pathlib import Path
from pkg_resources import resource_filename
from pytest import fixture

pytest_plugins = [
    "tests.network.fixtures_mongodb",
    "tests.network.fixtures_rabbitmq"
]


@fixture(scope="session")
def docker_compose_file():
    return Path(resource_filename("tests", "network"), "docker-compose.yml")
