import pytest
from fastapi.testclient import TestClient

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
        is_db_init = False

        def mock_db_init(_):
            nonlocal is_db_init
            is_db_init = True

        monkey_class.setattr(ProcessorAPI, 'startup', mock_db_init)

        app = ProcessorAPI(
            title=TestServer.ocrd_tool['executable'],
            description=TestServer.ocrd_tool['description'],
            version='0.0.1',
            ocrd_tool=TestServer.ocrd_tool,
            db_url='',
            processor_class=DummyProcessor
        )

        with TestClient(app) as c:
            # Make sure that the database is initialized
            assert is_db_init, 'Database is not initialized.'

            yield c

    def test_get_info(self, client):
        response = client.get('/')
        assert response.status_code == 200, 'The status code is not 200.'
        assert response.json() == TestServer.ocrd_tool, 'The response is not the same as the input ocrd-tool.'
