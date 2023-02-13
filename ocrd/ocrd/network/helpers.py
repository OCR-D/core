from typing import Tuple
from re import split
from os import environ
from os.path import join, exists


def verify_database_url(mongodb_address: str) -> str:
    database_prefix = 'mongodb://'
    if not mongodb_address.startswith(database_prefix):
        error_msg = f'The database address must start with a prefix: {database_prefix}'
        raise ValueError(error_msg)

    address_without_prefix = mongodb_address[len(database_prefix):]
    print(f'Address without prefix: {address_without_prefix}')
    elements = address_without_prefix.split(':', 1)
    if len(elements) != 2:
        raise ValueError('The database address is in wrong format')
    db_host = elements[0]
    db_port = int(elements[1])
    mongodb_url = f'{database_prefix}{db_host}:{db_port}'
    return mongodb_url


def verify_and_parse_rabbitmq_addr(rabbitmq_address: str) -> Tuple[str, int, str]:
    elements = split(pattern=r':|/', string=rabbitmq_address)
    if len(elements) == 3:
        rmq_host = elements[0]
        rmq_port = int(elements[1])
        rmq_vhost = f'/{elements[2]}'
        return rmq_host, rmq_port, rmq_vhost

    if len(elements) == 2:
        rmq_host = elements[0]
        rmq_port = int(elements[1])
        rmq_vhost = '/'  # The default global vhost
        return rmq_host, rmq_port, rmq_vhost

    raise ValueError('The RabbitMQ address is in wrong format. Expected format: {host}:{port}/{vhost}')


def get_workspaces_dir() -> str:
    """get the path to the workspaces folder

    The processing-workers must have access to the workspaces. First idea is that they are provided
    via nfs and always available under $XDG_DATA_HOME/ocrd-workspaces. This function provides the
    absolute path to the folder and raises a ValueError if it is not available
    """
    if 'XDG_DATA_HOME' in environ:
        xdg_data_home = environ['XDG_DATA_HOME']
    else:
        xdg_data_home = join(environ['HOME'], '.local', 'share')
    res = join(xdg_data_home, 'ocrd-workspaces')
    if not exists(res):
        raise ValueError('Ocrd-Workspaces directory not found. Expected \'{res}\'')
    return res
