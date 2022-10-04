from typing import Tuple


def parse_server_input(input_str: str) -> Tuple[str, int, str]:
    """
    Parse the string into 3 parts, IP address, port, and Mongo database connection string.

    Args:
        input_str (str): a string with the format ``ip:port:db``, where ``ip`` and ``port`` is where the server listens
            on, and ``db`` is a connection string to a Mongo database.

    Returns:
        str, int, str: the IP, port, and Mongo DB connection string respectively.
    """
    elements = input_str.split(':', 2)
    if len(elements) != 3:
        raise ValueError
    ip = elements[0]
    port = int(elements[1])
    mongo_url = elements[2]

    return ip, port, mongo_url


def parse_version_string(version_str: str) -> str:
    """
    Get the version number from the output of the :py:function:`~ocrd.processor.base.Processor.show_version`.

    Args:
        version_str (str): A string which looks like this ``Version %s, ocrd/core %s``

    Returns:
        str: the string between the word ``Version`` and the first comma
    """
    first_split = version_str.split(',')
    second_split = first_split[0].split(' ')
    return second_split[1]
