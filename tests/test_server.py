import json

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from ocrd.server.main import ProcessorAPI
from .data import DUMMY_TOOL, DummyProcessor


class TestServer:

    @pytest.fixture(scope='class')
    def monkey_class(self):
        from _pytest.monkeypatch import MonkeyPatch
        monkey_patch = MonkeyPatch()
        yield monkey_patch
        monkey_patch.undo()

    @pytest.fixture(scope='class')
    def app(self, monkey_class):
        def mock_db_init(_):
            pass

        # Patch the startup function
        monkey_class.setattr(ProcessorAPI, 'startup', mock_db_init)

        return ProcessorAPI(
            title=DUMMY_TOOL['executable'],
            description=DUMMY_TOOL['description'],
            version='0.0.1',
            ocrd_tool=DUMMY_TOOL,
            db_url='',
            processor_class=DummyProcessor
        )

    @pytest.fixture(scope='class')
    def client(self, monkey_class, app):
        with TestClient(app) as c:
            yield c

    def test_get_info(self, client):
        response = client.get('/')
        assert response.status_code == 200, 'The status code is not 200.'
        assert response.json() == DUMMY_TOOL, 'The response is not the same as the input ocrd-tool.'

    def test_get_processor_cached(self, app):
        parameters = {}
        processor_1 = app.get_processor(json.dumps(parameters))
        processor_2 = app.get_processor(json.dumps(parameters))
        assert processor_1 is processor_2, 'The processor is not cached.'

    def test_get_processor_uncached(self, app):
        parameters_1 = {}
        processor_1 = app.get_processor(json.dumps(parameters_1))

        parameters_2 = {'baz': 'foo'}
        processor_2 = app.get_processor(json.dumps(parameters_2))
        assert processor_1 is not processor_2, 'The processor must not be cached.'

    def test_get_processor_invalid_parameters(self, app):
        parameters = {'unknown-key': 'unknown-value'}
        with pytest.raises(HTTPException) as exception_info:
            app.get_processor(json.dumps(parameters))

        assert exception_info.value.status_code == 400, 'Status code is not 400.'
        assert 'Invalid parameters' in exception_info.value.detail, 'Wrong message in the detail.'
