import pytest

from ocrd.helpers import parse_server_input


class TestHelper:

    def test_parse_server_input_success(self):
        init_ip = '0.0.0.0'
        ini_port = 80
        init_mongo_url = 'mongodb://localhost:27017'
        input_str = f'{init_ip}:{ini_port}:{init_mongo_url}'

        ip, port, mongo_url = parse_server_input(input_str)
        assert init_ip == ip
        assert ini_port == port
        assert init_mongo_url == mongo_url

    def test_parse_server_input_wrong_format(self):
        init_ip = '0.0.0.0'
        ini_port = 80

        # Input without MongoDB connection string
        input_str = f'{init_ip}:{ini_port}'

        with pytest.raises(ValueError):
            parse_server_input(input_str)
