from typing import Tuple
from re import split

from ocrd.network.rabbitmq_utils import (
    OcrdProcessingMessage,
    OcrdResultMessage
)


def verify_database_url(mongodb_address: str) -> str:
    database_prefix = "mongodb://"
    if not mongodb_address.startswith(database_prefix):
        error_msg = f"The database address must start with a prefix: {database_prefix}"
        raise ValueError(error_msg)

    address_without_prefix = mongodb_address[len(database_prefix):]
    print(f"Address without prefix: {address_without_prefix}")
    elements = address_without_prefix.split(':', 1)
    if len(elements) != 2:
        raise ValueError("The database address is in wrong format")
    db_host = elements[0]
    db_port = int(elements[1])
    mongodb_url = f"{database_prefix}{db_host}:{db_port}"
    return mongodb_url


def verify_and_parse_rabbitmq_addr(rabbitmq_address: str) -> Tuple[str, int, str]:
    elements = split(pattern=r':|/', string=rabbitmq_address)
    if len(elements) == 3:
        rmq_host = elements[0]
        rmq_port = int(elements[1])
        rmq_vhost = f"/{elements[2]}"
        return rmq_host, rmq_port, rmq_vhost

    if len(elements) == 2:
        rmq_host = elements[0]
        rmq_port = int(elements[1])
        rmq_vhost = "/"  # The default global vhost
        return rmq_host, rmq_port, rmq_vhost

    raise ValueError("The RabbitMQ address is in wrong format. Expected format: {host}:{port}/{vhost}")


def construct_dummy_processing_message() -> OcrdProcessingMessage:
    return OcrdProcessingMessage(
        job_id="dummy-job-id",
        processor_name="ocrd-dummy",
        created_time=None,  # Auto generated if None
        path_to_mets="/home/mm/Desktop/ws_example/mets.xml",
        workspace_id=None,  # Not required, workspace is not uploaded through the Workspace Server
        input_file_grps=["DEFAULT"],
        output_file_grps=["DUMMY-OUTPUT"],
        page_id="PHYS0001..PHYS0003",  # Process only the first 3 pages
        parameters={},
        result_queue_name=None  # Not implemented yet, do not set
    )


def construct_dummy_result_message() -> OcrdResultMessage:
    return OcrdResultMessage(
        job_id="dummy-job_id",
        status="RUNNING",
        workspace_id="dummy-workspace_id",
        path_to_mets="/home/mm/Desktop/ws_example/mets.xml"
    )
