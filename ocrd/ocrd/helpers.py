from typing import Tuple


def parse_server_input(input_str: str) -> Tuple[str, int, str]:
    """
    Parse the string into 3 parts, IP address, port, and Mongo database connection string.

    Args:
        input_str (str): a string with the format ``ip:port:db``, where ``ip`` and ``port`` is where the server listens
            on, and ``db`` is a connection string to a Mongo database.

    Returns:

    """
    elements = input_str.split(':', 2)
    if len(elements) != 3:
        raise ValueError
    ip = elements[0]
    port = int(elements[1])
    mongo_url = elements[2]

    return ip, port, mongo_url
