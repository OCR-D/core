from pymongo import MongoClient, uri_parser as mongo_uri_parser
from pytest import fixture
from ocrd_utils.config import config
from ocrd_network.database import sync_initiate_database

DB_NAME = config.DB_NAME
DB_URL = config.DB_URL


def verify_database_uri(mongodb_address: str) -> str:
    try:
        # perform validation check
        mongo_uri_parser.parse_uri(uri=mongodb_address, validate=True)
    except Exception as error:
        raise ValueError(f"The MongoDB address '{mongodb_address}' is in wrong format, {error}")
    return mongodb_address


@fixture(scope="package", name="mongo_client")
def fixture_mongo_client():
    sync_initiate_database(DB_URL, DB_NAME)
    mongo_client = MongoClient(DB_URL, serverSelectionTimeoutMS=3000)
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
