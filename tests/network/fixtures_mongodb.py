from pymongo import MongoClient, uri_parser as mongo_uri_parser
from pytest import fixture
from .constants import DB_NAME
from .utils import is_url_responsive


def verify_database_uri(mongodb_address: str) -> str:
    try:
        # perform validation check
        mongo_uri_parser.parse_uri(uri=mongodb_address, validate=True)
    except Exception as error:
        raise ValueError(f"The MongoDB address '{mongodb_address}' is in wrong format, {error}")
    return mongodb_address


@fixture(scope="package", name="mongo_db")
def fixture_mongo_db(docker_ip, docker_services):
    port = docker_services.port_for("ocrd_network_mongo_db", 27017)
    test_url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=10.0,
        pause=0.1,
        check=lambda: is_url_responsive(test_url, retries=30)
    )


@fixture(scope="package", name="mongo_client")
def fixture_mongo_client(docker_ip, docker_services, mongo_db):
    mongodb_port = docker_services.port_for("ocrd_network_mongo_db", 27017)
    mongodb_url = f"mongodb://network_test:network_test@{docker_ip}:{mongodb_port}"
    mongo_client = MongoClient(mongodb_url, serverSelectionTimeoutMS=3000)
    yield mongo_client


@fixture(scope="package", name="mongo_processor_jobs")
def fixture_mongo_processor_jobs(mongo_client):
    mydb = mongo_client[DB_NAME]
    processor_jobs_collection = mydb["DBProcessorJob"]
    yield processor_jobs_collection
    processor_jobs_collection.drop()


@fixture(scope="package", name="mongo_workflow_jobs")
def fixture_mongo_workflow_jobs(mongo_client):
    mydb = mongo_client[DB_NAME]
    workflow_jobs_collection = mydb["DBWorkflowJob"]
    yield workflow_jobs_collection
    workflow_jobs_collection.drop()
