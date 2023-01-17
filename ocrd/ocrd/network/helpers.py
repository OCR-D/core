from typing import Tuple
from re import split


def verify_and_build_database_url(mongodb_address: str, database_prefix: str = "mongodb://") -> str:
    elements = mongodb_address.split(':', 1)
    if len(elements) != 2:
        raise ValueError("The database address is in wrong format")
    db_host = elements[0]
    db_port = int(elements[1])
    mongodb_url = f"{database_prefix}{db_host}:{db_port}"
    return mongodb_url


def verify_and_parse_rabbitmq_addr(rabbitmq_address: str) -> Tuple[str, int, str]:
    elements = split(pattern=r':|/', string=rabbitmq_address)
    if len(elements) != 3:
        raise ValueError("The RabbitMQ address is in wrong format")
    rmq_host = elements[0]
    rmq_port = int(elements[1])
    # Handle the case with default virtual host
    rmq_vhost = elements[2] if elements[2] else '/'
    return rmq_host, rmq_port, rmq_vhost
