from pytest import raises
from src.ocrd_network.param_validators import DatabaseParamType, ServerAddressParamType, QueueServerParamType


def test_database_param_type_positive():
    database_param_type = DatabaseParamType()
    correct_db_uris = [
        f"mongodb://db_user:db_pass@localhost:27017/",
        f"mongodb://db_user:db_pass@localhost:27017",
        f"mongodb://localhost:27017/",
        f"mongodb://localhost:27017",
        f"mongodb://localhost"
    ]
    for db_uri in correct_db_uris:
        database_param_type.convert(value=db_uri, param=None, ctx=None)


def test_database_param_type_negative():
    database_param_type = DatabaseParamType()
    incorrect_db_uris = [
        f"mongodbb://db_user:db_pass@localhost:27017",
        f"://db_user:db_pass@localhost:27017",
        f"db_user:db_pass@localhost:27017",
        f"localhost:27017",
        "localhost"
    ]
    for db_uri in incorrect_db_uris:
        with raises(Exception):
            database_param_type.convert(value=db_uri, param=None, ctx=None)


def test_queue_server_param_type_positive():
    rmq_server_param_type = QueueServerParamType()
    correct_rmq_uris = [
        f"amqp://rmq_user:rmq_pass@localhost:5672/",
        f"amqp://rmq_user:rmq_pass@localhost:5672",
        f"amqp://localhost:5672/",
        f"amqp://localhost:5672",
        f"amqp://localhost"
    ]
    for rmq_uri in correct_rmq_uris:
        rmq_server_param_type.convert(value=rmq_uri, param=None, ctx=None)


def test_queue_server_param_type_negative():
    rmq_server_param_type = QueueServerParamType()
    incorrect_rmq_uris = [
        f"amqpp://rmq_user:rmq_pass@localhost:5672",
        f"rmq_user:rmq_pass@localhost:5672",
        f"localhost:5672",
        "localhost"
    ]
    for rmq_uri in incorrect_rmq_uris:
        with raises(Exception):
            rmq_server_param_type.convert(value=rmq_uri, param=None, ctx=None)


def test_server_address_param_type_positive():
    server_address_param_type = ServerAddressParamType()
    correct_address = "localhost:8000"
    server_address_param_type.convert(value=correct_address, param=None, ctx=None)


def test_server_address_param_type_negative():
    server_address_param_type = ServerAddressParamType()
    incorrect_address = "8000:localhost"
    with raises(Exception):
        server_address_param_type.convert(value=incorrect_address, param=None, ctx=None)
