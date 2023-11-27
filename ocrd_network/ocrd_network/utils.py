from datetime import datetime
from functools import wraps
from pika import URLParameters
from pymongo import uri_parser as mongo_uri_parser
from re import match as re_match
from requests import Session as Session_TCP
from requests_unixsocket import Session as Session_UDS
from typing import Dict, List
from uuid import uuid4
from yaml import safe_load

from ocrd import Resolver, Workspace
from ocrd_validators import ProcessingServerConfigValidator
from .rabbitmq_utils import OcrdResultMessage
from ocrd.task_sequence import ProcessorTask


# Based on: https://gist.github.com/phizaz/20c36c6734878c6ec053245a477572ec
def call_sync(func):
    import asyncio

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return asyncio.get_event_loop().run_until_complete(result)
        return result
    return func_wrapper


def calculate_execution_time(start: datetime, end: datetime) -> int:
    """
    Calculates the difference between `start` and `end` datetime.
    Returns the result in milliseconds
    """
    return int((end - start).total_seconds() * 1000)


def generate_created_time() -> int:
    return int(datetime.utcnow().timestamp())


def generate_id() -> str:
    """
    Generate the id to be used for processing job ids.
    Note, workspace_id and workflow_id in the reference
    WebAPI implementation are produced in the same manner
    """
    return str(uuid4())


def validate_and_load_config(config_path: str) -> Dict:
    # Load and validate the config
    with open(config_path) as fin:
        config = safe_load(fin)
    report = ProcessingServerConfigValidator.validate(config)
    if not report.is_valid:
        raise Exception(f'Processing-Server configuration file is invalid:\n{report.errors}')
    return config


def verify_database_uri(mongodb_address: str) -> str:
    try:
        # perform validation check
        mongo_uri_parser.parse_uri(uri=mongodb_address, validate=True)
    except Exception as error:
        raise ValueError(f"The database address '{mongodb_address}' is in wrong format, {error}")
    return mongodb_address


def verify_and_parse_mq_uri(rabbitmq_address: str):
    """
    Check the full list of available parameters in the docs here:
    https://pika.readthedocs.io/en/stable/_modules/pika/connection.html#URLParameters
    """

    uri_pattern = r"^(?:([^:\/?#\s]+):\/{2})?(?:([^@\/?#\s]+)@)?([^\/?#\s]+)?(?:\/([^?#\s]*))?(?:[?]([^#\s]+))?\S*$"
    match = re_match(pattern=uri_pattern, string=rabbitmq_address)
    if not match:
        raise ValueError(f"The message queue server address is in wrong format: '{rabbitmq_address}'")
    url_params = URLParameters(rabbitmq_address)

    parsed_data = {
        'username': url_params.credentials.username,
        'password': url_params.credentials.password,
        'host': url_params.host,
        'port': url_params.port,
        'vhost': url_params.virtual_host
    }
    return parsed_data


def download_ocrd_all_tool_json(ocrd_all_url: str):
    if not ocrd_all_url:
        raise ValueError(f'The URL of ocrd all tool json is empty')
    headers = {'Accept': 'application/json'}
    response = Session_TCP().get(ocrd_all_url, headers=headers)
    if not response.status_code == 200:
        raise ValueError(f"Failed to download ocrd all tool json from: '{ocrd_all_url}'")
    return response.json()


def post_to_callback_url(logger, callback_url: str, result_message: OcrdResultMessage):
    logger.info(f'Posting result message to callback_url "{callback_url}"')
    headers = {"Content-Type": "application/json"}
    json_data = {
        "job_id": result_message.job_id,
        "state": result_message.state,
        "path_to_mets": result_message.path_to_mets,
        "workspace_id": result_message.workspace_id
    }
    response = Session_TCP().post(url=callback_url, headers=headers, json=json_data)
    logger.info(f'Response from callback_url "{response}"')


def get_ocrd_workspace_instance(mets_path: str, mets_server_url: str = None) -> Workspace:
    if mets_server_url:
        if not is_mets_server_running(mets_server_url=mets_server_url):
            raise RuntimeError(f'The mets server is not running: {mets_server_url}')
    return Resolver().workspace_from_url(mets_url=mets_path, mets_server_url=mets_server_url)


def get_ocrd_workspace_physical_pages(mets_path: str, mets_server_url: str = None) -> List[str]:
    return get_ocrd_workspace_instance(mets_path=mets_path, mets_server_url=mets_server_url).mets.physical_pages


def is_mets_server_running(mets_server_url: str) -> bool:
    protocol = 'tcp' if (mets_server_url.startswith('http://') or mets_server_url.startswith('https://')) else 'uds'
    session = Session_TCP() if protocol == 'tcp' else Session_UDS()
    mets_server_url = mets_server_url if protocol == 'tcp' else f'http+unix://{mets_server_url.replace("/", "%2F")}'
    try:
        response = session.get(url=f'{mets_server_url}/workspace_path')
    except Exception:
        return False
    if response.status_code == 200:
        return True
    return False


def stop_mets_server(mets_server_url: str) -> bool:
    protocol = 'tcp' if (mets_server_url.startswith('http://') or mets_server_url.startswith('https://')) else 'uds'
    session = Session_TCP() if protocol == 'tcp' else Session_UDS()
    mets_server_url = mets_server_url if protocol == 'tcp' else f'http+unix://{mets_server_url.replace("/", "%2F")}'
    try:
        response = session.delete(url=f'{mets_server_url}/')
    except Exception:
        return False
    if response.status_code == 200:
        return True
    return False


def validate_workflow(workflow: str, logger=None) -> bool:
    """ Check that workflow is not empty and parseable to a lists of ProcessorTask
    """
    if not workflow.strip():
        if logger:
            logger.info("Workflow is invalid (empty string)")
        return False
    try:
        tasks_list = workflow.splitlines()
        [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
    except ValueError as e:
        if logger:
            logger.info(f"Workflow is invalid, parsing to ProcessorTasks failed: {e}")
        return False
    return True
