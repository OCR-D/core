from ocrd.processor.helpers import get_processor
from ocrd.server.models.job import JobInput, StateEnum
from tests.base import copy_of_directory, assets
from ..data import DUMMY_TOOL, DummyProcessor


class TestServer:

    def test_get_info(self, client):
        response = client.get('/')
        assert response.status_code == 200, 'The status code is not 200.'
        assert response.json() == DUMMY_TOOL, 'The response is not the same as the input ocrd-tool.'

    def test_get_processor_cached(self):
        parameters = {}
        processor_1 = get_processor(parameters, DummyProcessor)
        processor_2 = get_processor(parameters, DummyProcessor)
        assert isinstance(processor_1, DummyProcessor), 'The processor is not from the correct class.'
        assert processor_1 is processor_2, 'The processor is not cached.'

    def test_get_processor_uncached(self):
        parameters_1 = {}
        processor_1 = get_processor(parameters_1, DummyProcessor)

        parameters_2 = {'baz': 'foo'}
        processor_2 = get_processor(parameters_2, DummyProcessor)
        assert processor_1 is not processor_2, 'The processor must not be cached.'

    def test_post_data(self, mocked_job, mocked_add_task, client):
        with copy_of_directory(assets.url_of('SBB0000F29300010000/data')) as ws_dir:
            job_input = JobInput(
                path=f'{ws_dir}/mets.xml',
                description='Test run',
                input_file_grps=['OCR-D-IMG'],
                output_file_grps=['OUTPUT']
            )
            response = client.post(url='/', json=job_input.dict(exclude_unset=True, exclude_none=True))

        # Make sure that the job is created with proper arguments (esp. state == QUEUED)
        mocked_job.assert_called_with(**job_input.dict(exclude_unset=True, exclude_none=True), state=StateEnum.queued)

        # Make sure that the background task is run with proper arguments
        args, kwargs = mocked_add_task.call_args
        assert kwargs['processor_class'] is DummyProcessor
        assert kwargs['job_id'] == mocked_job.return_value.id
        assert kwargs['page_id'] == job_input.page_id
        assert kwargs['input_file_grps'] == job_input.input_file_grps
        assert kwargs['output_file_grps'] == job_input.output_file_grps

        assert response.status_code == 202, 'The status code is not 202.'

    def test_post_invalid_parameter(self, mocked_job, client):
        with copy_of_directory(assets.url_of('SBB0000F29300010000/data')) as ws_dir:
            job_input = JobInput(
                path=f'{ws_dir}/mets.xml',
                description='Test run',
                input_file_grps=['OCR-D-IMG'],
                output_file_grps=['OUTPUT'],
                parameters={'unknown-key': 'unknown-value'}
            )
            response = client.post(url='/', json=job_input.dict(exclude_unset=True, exclude_none=True))

            assert response.status_code == 400, 'Status code is not 400.'

    def test_get_job(self, client):
        job_id = '60cd778664dc9f75f4aadec8'
        response = client.get(f'/{job_id}')
        assert response.status_code == 200, 'The status code is not 200.'

    def test_get_unknown_job(self, client):
        job_id = '60cd778664dc9f75f4aadec9'
        response = client.get(f'/{job_id}')
        assert response.status_code == 404, 'The status code is not 404.'
