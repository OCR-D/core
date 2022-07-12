import pytest

from fastapi.testclient import TestClient

import ocrd.server.database
from ocrd.processor.builtin.dummy_processor import DummyProcessor
from ocrd.server.main import ProcessorAPI


class TestServer:
    ocrd_tool = {
        'executable': 'ocrd-dummy',
        'description': 'Bare-bones processor that copies file from input group to output group',
        'steps': ['preprocessing/optimization'],
        'categories': ['Image preprocessing'],
        'input_file_grp': ['DUMMY_INPUT'],
        'output_file_grp': ['DUMMY_OUTPUT']
    }

    @pytest.fixture(scope='class')
    def monkey_class(self):
        from _pytest.monkeypatch import MonkeyPatch
        monkey_patch = MonkeyPatch()
        yield monkey_patch
        monkey_patch.undo()

    @pytest.fixture(scope='class')
    def client(self, monkey_class):
        def mock_db_init():
            print('Database initiated.')

        monkey_class.setattr(ocrd.server.database, 'initiate_database', mock_db_init)

        app = ProcessorAPI(
            title=TestServer.ocrd_tool['executable'],
            description=TestServer.ocrd_tool['description'],
            version='0.0.1',
            ocrd_tool=TestServer.ocrd_tool,
            db_url='',
            processor_class=DummyProcessor
        )
        client = TestClient(app)
        return client

    def test_get_info(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert response.json() == TestServer.ocrd_tool
