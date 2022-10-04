import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from ocrd.server.main import ProcessorAPI
from ocrd.server.models.job import StateEnum
from tests.data import DUMMY_TOOL, DummyProcessor
from tests.server.mock_job import MockJob


@pytest.fixture(scope='class')
def mock_init(class_mocker: MockerFixture):
    # Patch the startup function
    return class_mocker.patch('ocrd.server.main.ProcessorAPI.startup')


@pytest.fixture(scope='class')
def mocked_job(class_mocker: MockerFixture):
    # Patch the Job class to return the MockJob
    mocked_job = class_mocker.patch('ocrd.server.main.Job', autospec=MockJob)
    mocked_job.return_value = MockJob(path='', state=StateEnum.failed, input_file_grps=['TEST'])

    # Mock the id field
    mocked_id = class_mocker.PropertyMock(return_value=1)
    type(mocked_job.return_value).id = mocked_id

    # Mock the static get function
    mocked_job.get.side_effect = MockJob.get

    return mocked_job


@pytest.fixture(scope='class')
def app(mocked_job, class_mocker: MockerFixture):
    # Make MagicMock work with async. AsyncMock is only available from Python 3.8
    async def async_magic():
        pass

    class_mocker.MagicMock.__await__ = lambda x: async_magic().__await__()

    return ProcessorAPI(
        title=DUMMY_TOOL['executable'],
        description=DUMMY_TOOL['description'],
        version='0.0.1',
        ocrd_tool=DUMMY_TOOL,
        db_url='',
        processor_class=DummyProcessor
    )


@pytest.fixture(scope='class')
def client(mock_init, app):
    with TestClient(app) as c:
        yield c

    # Check if the init function was called
    mock_init.assert_called_once()


@pytest.fixture(scope='class')
def mocked_add_task(class_mocker: MockerFixture):
    add_task = class_mocker.patch('ocrd.server.main.BackgroundTasks.add_task')
    return add_task
