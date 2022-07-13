import json

import pytest
from fastapi import HTTPException, BackgroundTasks
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from ocrd.server.main import ProcessorAPI
from ocrd.server.models.job import JobInput, StateEnum
from tests.base import copy_of_directory, assets
from .mock_job import MockJob
from ..data import DUMMY_TOOL, DummyProcessor


class TestServer:

    @pytest.fixture(scope='class')
    def monkey_class(self):
        from _pytest.monkeypatch import MonkeyPatch
        monkey_patch = MonkeyPatch()
        yield monkey_patch
        monkey_patch.undo()

    @pytest.fixture(scope='class')
    def app(self, monkey_class, class_mocker: MockerFixture):
        def mock_db_init(_):
            pass

        def mock_background_task(*args, **kwargs):
            pass

        # Patch the startup function
        monkey_class.setattr(ProcessorAPI, 'startup', mock_db_init)

        # Patch the BackgroundTasks.add_task function
        monkey_class.setattr(BackgroundTasks, 'add_task', mock_background_task)

        # Make MagicMock work with async. AsyncMock is only available from Python 3.8
        async def async_magic():
            pass

        class_mocker.MagicMock.__await__ = lambda x: async_magic().__await__()

        # Patch the connection to MongoDB
        class_mocker.patch('beanie.odm.interfaces.getters.OtherGettersInterface.get_motor_collection')

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

    def test_post_data(self, client, mocker: MockerFixture):
        # Patch the Job class to return the MockJob
        mocked_job = mocker.patch('ocrd.server.main.Job', autospec=MockJob)
        mocked_job.return_value = MockJob(path='', state=StateEnum.failed, input_file_grps=['TEST'])

        # Mock the id field
        mocked_id = mocker.PropertyMock(return_value=1)
        type(mocked_job.return_value).id = mocked_id

        with copy_of_directory(assets.url_of('SBB0000F29300010000/data')) as ws_dir:
            job_input = JobInput(
                path=f'{ws_dir}/mets.xml',
                description='Test run',
                input_file_grps=['OCR-D-IMG'],
                output_file_grps=['OUTPUT']
            )
            response = client.post(url='/', json=job_input.dict(exclude_unset=True, exclude_none=True))

        mocked_job.assert_called_with(**job_input.dict(exclude_unset=True, exclude_none=True), state=StateEnum.queued)
        assert response.status_code == 202, 'The status code is not 202.'
