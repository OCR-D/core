import pytest
from pytest_mock import MockerFixture

from ..data import DUMMY_TOOL, DummyProcessor
from ocrd.server.main import ProcessorAPI
from fastapi.testclient import TestClient

from ocrd.server.models.job import StateEnum
from ..server.mock_job import MockJob


@pytest.fixture(scope='class')
def mock_init(class_mocker: MockerFixture):
    # Patch the startup function
    return class_mocker.patch('ocrd.server.main.ProcessorAPI.startup')


@pytest.fixture(scope='class')
def app(class_mocker: MockerFixture):
    # Make MagicMock work with async. AsyncMock is only available from Python 3.8
    async def async_magic():
        pass

    class_mocker.MagicMock.__await__ = lambda x: async_magic().__await__()

    try:
        # Patch the connection to MongoDB
        class_mocker.patch('beanie.odm.interfaces.getters.OtherGettersInterface.get_motor_collection')
    except ModuleNotFoundError:
        # For Python 3.6 with older Beanie version
        class_mocker.patch('beanie.odm.documents.Document.get_motor_collection')

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
def mocked_job(class_mocker: MockerFixture):
    # Patch the Job class to return the MockJob
    mocked_job = class_mocker.patch('ocrd.server.main.Job', autospec=MockJob)
    mocked_job.return_value = MockJob(path='', state=StateEnum.failed, input_file_grps=['TEST'])

    # Mock the id field
    mocked_id = class_mocker.PropertyMock(return_value=1)
    type(mocked_job.return_value).id = mocked_id

    return mocked_job


@pytest.fixture(scope='class')
def mocked_add_task(class_mocker: MockerFixture):
    add_task = class_mocker.patch('fastapi.BackgroundTasks.add_task')
    return add_task
