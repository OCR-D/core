from pymongo import uri_parser as mongo_uri_parser
from pytest import fixture
from ocrd_utils.config import config
from ocrd_network.database import sync_initiate_database


def verify_database_uri(mongodb_address: str) -> str:
    try:
        # perform validation check
        mongo_uri_parser.parse_uri(uri=mongodb_address, validate=True)
    except Exception as error:
        raise ValueError(f"The MongoDB address '{mongodb_address}' is in wrong format, {error}")
    return mongodb_address


@fixture(scope="package", name="mongo_client")
def fixture_mongo_client():
    sync_initiate_database(config.DB_URL, config.DB_NAME)
