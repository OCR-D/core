from pytest import fixture
from os.path import join

pytest_plugins = [
    "tests.network.fixtures_mongodb",
    "tests.network.fixtures_rabbitmq"
]


@fixture(scope="session")
def docker_compose_file(pytestconfig):
    return join(str(pytestconfig.rootdir), "docker-compose.yml")
