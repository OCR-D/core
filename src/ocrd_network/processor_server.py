from datetime import datetime
from os import getpid
from subprocess import run as subprocess_run, PIPE
from uvicorn import run

from fastapi import APIRouter, BackgroundTasks, FastAPI, status
from fastapi.responses import FileResponse

from ocrd_utils import (
    initLogging,
    get_ocrd_tool_json,
    getLogger,
    parse_json_string_with_comments
)
from .constants import JobState, ServerApiTags
from .database import (
    DBProcessorJob,
    db_get_workspace,
    db_update_processing_job,
    db_get_processing_job,
    initiate_database
)
from .logging_utils import (
    configure_file_handler_with_formatter,
    get_processor_server_logging_file_path,
    get_processing_job_logging_file_path
)
from .models import PYJobInput, PYJobOutput, PYOcrdTool
from .process_helpers import invoke_processor
from .rabbitmq_utils import OcrdResultMessage
from .server_utils import (
    _get_processor_job,
    _get_processor_job_log,
    raise_http_exception,
    validate_and_return_mets_path,
    validate_job_input
)
from .utils import calculate_execution_time, post_to_callback_url, generate_id


class ProcessorServer(FastAPI):
    def __init__(self, mongodb_addr: str, processor_name: str = "", processor_class=None):
        if not (processor_name or processor_class):
            raise ValueError("Either 'processor_name' or 'processor_class' must be provided")
        initLogging()
        super().__init__(
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            title=f"Network agent - Processor Server",
            description="Network agent - Processor Server"
        )
        self.log = getLogger("ocrd_network.processor_server")
        log_file = get_processor_server_logging_file_path(processor_name=processor_name, pid=getpid())
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

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
            self.processor_name = self.ocrd_tool["executable"]

        self.add_api_routes_processing()

    async def on_startup(self):
        await initiate_database(db_url=self.db_url)

    async def on_shutdown(self) -> None:
        """
        TODO: Perform graceful shutdown operations here
        """
        pass

    def add_api_routes_processing(self):
        processing_router = APIRouter()
        processing_router.add_api_route(
            path="/info",
            endpoint=self.get_processor_info,
            methods=["GET"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get information about this processor.",
            response_model=PYOcrdTool,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )
        processing_router.add_api_route(
            path="/run",
            endpoint=self.create_processor_task,
            methods=["POST"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_202_ACCEPTED,
            summary="Submit a job to this processor.",
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )
        processing_router.add_api_route(
            path="/job/{job_id}",
            endpoint=self.get_processor_job,
            methods=["GET"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get information about a job based on its ID",
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )
        processing_router.add_api_route(
            path="/log/{job_id}",
            endpoint=self.get_processor_job_log,
            methods=["GET"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get the log file of a job id"
        )

    async def get_processor_info(self):
        if not self.ocrd_tool:
            message = "Empty or missing ocrd tool json."
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
        return self.ocrd_tool

    # Note: The Processing server pushes to a queue, while
    #  the Processor Server creates (pushes to) a background task
    async def create_processor_task(self, job_input: PYJobInput, background_tasks: BackgroundTasks):
        validate_job_input(self.log, self.processor_name, self.ocrd_tool, job_input)
        job_input.path_to_mets = await validate_and_return_mets_path(self.log, job_input)

        # The request is not forwarded from the Processing Server, assign a job_id
        if not job_input.job_id:
            job_id = generate_id()
            # Create a DB entry
            job = DBProcessorJob(
                **job_input.dict(exclude_unset=True, exclude_none=True),
                job_id=job_id,
                processor_name=self.processor_name,
                state=JobState.queued
            )
            await job.insert()
        else:
            job = await db_get_processing_job(job_input.job_id)
        # await self.run_processor_task(job=job)
        background_tasks.add_task(self.run_processor_task, job)
        return job.to_job_output()

    async def run_processor_task(self, job: DBProcessorJob):
        execution_failed = False
        start_time = datetime.now()
        job_log_file = get_processing_job_logging_file_path(job_id=job.job_id)
        await db_update_processing_job(
            job_id=job.job_id,
            state=JobState.running,
            start_time=start_time,
            log_file_path=job_log_file
        )

        mets_server_url = (await db_get_workspace(workspace_mets_path=job.path_to_mets)).mets_server_url
        try:
            invoke_processor(
                processor_class=self.processor_class,
                executable=self.processor_name,
                abs_path_to_mets=job.path_to_mets,
                input_file_grps=job.input_file_grps,
                output_file_grps=job.output_file_grps,
                page_id=job.page_id,
                parameters=job.parameters,
                mets_server_url=mets_server_url,
                log_filename=job_log_file,
            )
        except Exception as error:
            self.log.debug(f"processor_name: {self.processor_name}, path_to_mets: {job.path_to_mets}, "
                           f"input_grps: {job.input_file_grps}, output_file_grps: {job.output_file_grps}, "
                           f"page_id: {job.page_id}, parameters: {job.parameters}")
            self.log.exception(error)
            execution_failed = True
        end_time = datetime.now()
        exec_duration = calculate_execution_time(start_time, end_time)
        job_state = JobState.success if not execution_failed else JobState.failed
        await db_update_processing_job(
            job_id=job.job_id,
            state=job_state,
            end_time=end_time,
            exec_time=f"{exec_duration} ms"
        )
        result_message = OcrdResultMessage(
            job_id=job.job_id,
            state=job_state.value,
            path_to_mets=job.path_to_mets,
            # May not be always available
            workspace_id=job.workspace_id if job.workspace_id else ''
        )
        self.log.info(f"Result message: {result_message}")
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
                subprocess_run(
                    [self.processor_name, "--dump-json"],
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
        version_str = subprocess_run(
            [self.processor_name, "--version"],
            stdout=PIPE,
            check=True,
            universal_newlines=True
        ).stdout
        return version_str

    def run_server(self, host, port):
        run(self, host=host, port=port)

    async def get_processor_job(self, job_id: str) -> PYJobOutput:
        return await _get_processor_job(self.log, job_id)

    async def get_processor_job_log(self, job_id: str) -> FileResponse:
        return await _get_processor_job_log(self.log, job_id)
