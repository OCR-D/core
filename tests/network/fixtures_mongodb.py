from pytest import fixture
from src.ocrd_network.database import sync_initiate_database
from src.ocrd_network.utils import verify_database_uri
from src.ocrd_utils.config import config


@fixture(scope="package", name="mongo_client")
def fixture_mongo_client():
    verify_database_uri(config.DB_URL)
    sync_initiate_database(config.DB_URL, config.DB_NAME)
