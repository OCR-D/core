from datetime import datetime
from functools import wraps
from os import environ
from pika import URLParameters
from pymongo import uri_parser as mongo_uri_parser
from re import match as re_match
import requests
from typing import Dict
from uuid import uuid4
from yaml import safe_load

from ocrd_validators import ProcessingServerConfigValidator


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


def tf_disable_interactive_logs():
    try:
        # This env variable must be set before importing from Keras
        environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        from tensorflow.keras.utils import disable_interactive_logging
        # Enabled interactive logging throws an exception
        # due to a call of sys.stdout.flush()
        disable_interactive_logging()
    except Exception:
        # Nothing should be handled here if TF is not available
        pass


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
    response = requests.get(ocrd_all_url, headers=headers)
    if not response.status_code == 200:
        raise ValueError(f"Failed to download ocrd all tool json from: '{ocrd_all_url}'")
    return response.json()
