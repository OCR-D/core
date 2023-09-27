from datetime import datetime
import logging
from os import getpid
from subprocess import run, PIPE
import uvicorn

from fastapi import FastAPI, HTTPException, status

from ocrd_utils import (
    initLogging,
    get_ocrd_tool_json,
    getLogger,
    parse_json_string_with_comments,
)
from .database import (
    DBProcessorJob,
    db_get_workspace,
    db_update_processing_job,
    initiate_database
)
from .models import (
    PYJobInput,
    PYJobOutput,
    PYOcrdTool,
    StateEnum
)
from .process_helpers import invoke_processor
from .rabbitmq_utils import OcrdResultMessage
from .server_utils import (
    _get_processor_job,
    validate_and_return_mets_path,
    validate_job_input
)
from .utils import (
    calculate_execution_time,
    post_to_callback_url,
    generate_id,
)


class ProcessorServer(FastAPI):
    def __init__(self, mongodb_addr: str, processor_name: str = "", processor_class=None):
        if not (processor_name or processor_class):
            raise ValueError('Either "processor_name" or "processor_class" must be provided')
        initLogging()
        super().__init__(
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            title=f'OCR-D Processor Server',
            description='OCR-D Processor Server'
        )
        logging_suffix = f'{processor_name}.{getpid()}'
        self.log = getLogger('ocrd_network.processor_server')
        file_handler = logging.FileHandler(f'/tmp/ocrd_server_{logging_suffix}.log', mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.log.addHandler(file_handler)

        self.db_url = mongodb_addr
        self.processor_name = processor_name
        self.processor_class = processor_class
        self.ocrd_tool = None
        self.version = None

        self.version = self.get_version()
        self.ocrd_tool = self.get_ocrd_tool()

        if not self.ocrd_tool:
            raise Exception(f"The ocrd_tool is empty or missing")

        if not self.processor_name:
            self.processor_name = self.ocrd_tool['executable']

        # Create routes
        self.router.add_api_route(
            path='/',
            endpoint=self.get_processor_info,
            methods=['GET'],
            tags=['Processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about this processor.',
            response_model=PYOcrdTool,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/',
            endpoint=self.create_processor_task,
            methods=['POST'],
            tags=['Processing'],
            status_code=status.HTTP_202_ACCEPTED,
            summary='Submit a job to this processor.',
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/{job_id}',
            endpoint=self.get_processor_job,
            methods=['GET'],
            tags=['Processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about a job based on its ID',
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

    async def on_startup(self):
        await initiate_database(db_url=self.db_url)

    async def on_shutdown(self) -> None:
        """
        TODO: Perform graceful shutdown operations here
        """
        pass

    async def get_processor_info(self):
        if not self.ocrd_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Empty or missing ocrd_tool'
            )
        return self.ocrd_tool

    # Note: The Processing server pushes to a queue, while
    #  the Processor Server creates (pushes to) a background task
    async def create_processor_task(self, job_input: PYJobInput):
        validate_job_input(self.log, self.processor_name, self.ocrd_tool, job_input)
        job_input.path_to_mets = await validate_and_return_mets_path(self.log, job_input)

        job = None
        # The request is not forwarded from the Processing Server, assign a job_id
        if not job_input.job_id:
            job_id = generate_id()
            # Create a DB entry
            job = DBProcessorJob(
                **job_input.dict(exclude_unset=True, exclude_none=True),
                job_id=job_id,
                processor_name=self.processor_name,
                state=StateEnum.queued
            )
            await job.insert()
        await self.run_processor_task(job=job)
        return job.to_job_output()

    async def run_processor_task(self, job: DBProcessorJob):
        execution_failed = False
        start_time = datetime.now()
        await db_update_processing_job(
            job_id=job.job_id,
            state=StateEnum.running,
            start_time=start_time
        )

        mets_server_url = await db_get_workspace(workspace_mets_path=job.path_to_mets).mets_server_url
        try:
            invoke_processor(
                processor_class=self.processor_class,
                executable=self.processor_name,
                abs_path_to_mets=job.path_to_mets,
                input_file_grps=job.input_file_grps,
                output_file_grps=job.output_file_grps,
                page_id=job.page_id,
                parameters=job.parameters,
                mets_server_url=mets_server_url
            )
        except Exception as error:
            self.log.debug(f"processor_name: {self.processor_name}, path_to_mets: {job.path_to_mets}, "
                           f"input_grps: {job.input_file_grps}, output_file_grps: {job.output_file_grps}, "
                           f"page_id: {job.page_id}, parameters: {job.parameters}")
            self.log.exception(error)
            execution_failed = True
        end_time = datetime.now()
        exec_duration = calculate_execution_time(start_time, end_time)
        job_state = StateEnum.success if not execution_failed else StateEnum.failed
        await db_update_processing_job(
            job_id=job.job_id,
            state=job_state,
            end_time=end_time,
            exec_time=f'{exec_duration} ms'
        )
        result_message = OcrdResultMessage(
            job_id=job.job_id,
            state=job_state.value,
            path_to_mets=job.path_to_mets,
            # May not be always available
            workspace_id=job.workspace_id
        )
        self.log.info(f'Result message: {result_message}')
        if job.callback_url:
            # If the callback_url field is set,
            # post the result message (callback to a user defined endpoint)
            post_to_callback_url(self.log, job.callback_url, result_message)
        if job.internal_callback_url:
            # If the internal callback_url field is set,
            # post the result message (callback to Processing Server endpoint)
            post_to_callback_url(self.log, job.internal_callback_url, result_message)

    def get_ocrd_tool(self):
        if self.ocrd_tool:
            return self.ocrd_tool
        if self.processor_class:
            # The way of accessing ocrd tool like in the line below may be problematic
            # ocrd_tool = self.processor_class(workspace=None, version=True).ocrd_tool
            ocrd_tool = parse_json_string_with_comments(
                run(
                    [self.processor_name, '--dump-json'],
                    stdout=PIPE,
                    check=True,
                    universal_newlines=True
                ).stdout
            )
        else:
            ocrd_tool = get_ocrd_tool_json(self.processor_name)
        return ocrd_tool

    def get_version(self) -> str:
        if self.version:
            return self.version

        """ 
        if self.processor_class:
            # The way of accessing the version like in the line below may be problematic
            # version_str = self.processor_class(workspace=None, version=True).version
            return version_str
        """
        version_str = run(
            [self.processor_name, '--version'],
            stdout=PIPE,
            check=True,
            universal_newlines=True
        ).stdout
        return version_str

    def run_server(self, host, port):
        uvicorn.run(self, host=host, port=port)

    async def get_processor_job(self, processor_name: str, job_id: str) -> PYJobOutput:
        return await _get_processor_job(self.log, processor_name, job_id)
