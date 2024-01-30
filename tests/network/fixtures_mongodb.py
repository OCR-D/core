from pytest import fixture
from src.ocrd_network.database import sync_initiate_database
from src.ocrd_network.utils import verify_database_uri
from tests.network.config import test_config


@fixture(scope="package", name="mongo_client")
def fixture_mongo_client():
    verify_database_uri(test_config.DB_URL)
    sync_initiate_database(test_config.DB_URL, test_config.DB_NAME)
