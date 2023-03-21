from functools import wraps
from re import match as re_match
from pika import URLParameters
from pymongo import uri_parser as mongo_uri_parser


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
