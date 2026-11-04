from datetime import datetime
from os import getpid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ocrd_utils import initLogging, getLogger
from uvicorn import run as uvicorn_run

from ..constants import JobState
from ..database import db_update_processing_job, db_update_workspace, initiate_database
from ..logging_utils import (
    configure_file_handler_with_formatter,
    get_processing_server_logging_file_path,
)
from ..models import DBProcessorJob, PYJobInput, PYJobOutput, PYResultMessage
from ..rabbitmq_utils import connect_rabbitmq_publisher
from ..runtime_data import Deployer
from ..server_utils import (
    create_workspace_if_not_exists,
    get_from_database_workspace,
    kill_mets_server_zombies,
    raise_http_exception,
    validate_and_return_mets_path,
    validate_job_input,
)
from ..tcp_to_uds_mets_proxy import MetsServerProxy
from ..utils import expand_page_ids, generate_id, load_ocrd_all_tool_json

from .routers.others import create_others_router
from .routers.processing import create_processing_router
from .routers.workflow import create_workflow_router
from .services.processing import ProcessingService
from .services.workflow import WorkflowService
from .services.workspace import WorkspaceService


class ProcessingServer(FastAPI):
    """FastAPI application for OCR-D processing requests."""

    def __init__(self, config_path: str, host: str, port: int) -> None:
        self.title = "OCR-D Processing Server"
        super().__init__(
            title=self.title,
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            description="OCR-D Processing Server",
        )

        initLogging()
        self.log = getLogger("ocrd_network.processing_server")
        log_file = get_processing_server_logging_file_path(pid=getpid())
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        self.log.info("Loading ocrd-all-tool.json")
        self.ocrd_all_tool_json = load_ocrd_all_tool_json()
        self.hostname = host
        self.port = port
        self.deployer = Deployer(config_path)
        self.mets_server_proxy = MetsServerProxy()
        self.use_tcp_mets = self.deployer.use_tcp_mets

        if self.deployer.internal_callback_url:
            callback_host = self.deployer.internal_callback_url
            self.internal_job_callback_url = f"{callback_host.rstrip('/')}/result_callback"
            self.multiplexing_endpoint = f"{callback_host.rstrip('/')}/tcp_mets"
        else:
            self.internal_job_callback_url = f"http://{host}:{port}/result_callback"
            self.multiplexing_endpoint = f"http://{host}:{port}/tcp_mets"

        self.mongodb_url = None
        self.rabbitmq_url = None
        self.rmq_data = {
            "host": self.deployer.data_queue.host,
            "port": self.deployer.data_queue.port,
            "vhost": "/",
            "username": self.deployer.data_queue.cred_username,
            "password": self.deployer.data_queue.cred_password,
        }
        self.rmq_publisher = None

        self.workspace_service = WorkspaceService(self.log, self.deployer)
        self.processing_service = ProcessingService(
            log=self.log,
            ocrd_all_tool_json=self.ocrd_all_tool_json,
            rmq_data=self.rmq_data,
            internal_job_callback_url=self.internal_job_callback_url,
            deployer=self.deployer,
            use_tcp_mets=self.use_tcp_mets,
            multiplexing_endpoint=self.multiplexing_endpoint,
        )
        self.workflow_service = WorkflowService(
            log=self.log,
            processing_job_callback=self.validate_and_forward_job_to_worker,
            worker_validation_callback=self.processing_service.validate_worker_existence,
            stop_mets_server_callback=self.workspace_service.maybe_stop_mets_server,
        )
        self.workspace_service.set_cached_jobs_callback(self.push_cached_jobs_to_workers)
        self.workspace_service.set_workflow_completion_callback(self.workflow_service.maybe_finish_workflow)

        self.cache_processing_requests = self.workspace_service.cache_processing_requests
        self.cache_locked_pages = self.workspace_service.cache_locked_pages
        self.workspace_locks = self.workspace_service.workspace_locks

        self.include_router(create_others_router(self))
        self.include_router(create_processing_router(self))
        self.include_router(create_workflow_router(self))

        @self.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            exc_str = str(exc).replace("\n", " ").replace("   ", " ")
            self.log.error(f"{request}: {exc_str}")
            content = {"status_code": 10422, "message": exc_str, "data": None}
            return JSONResponse(
                content=content,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    # Application lifecycle

    def start(self) -> None:
        try:
            self.rabbitmq_url = self.deployer.deploy_rabbitmq()
            self.mongodb_url = self.deployer.deploy_mongodb()
            self.rmq_publisher = connect_rabbitmq_publisher(
                self.log, self.rmq_data, enable_acks=True
            )
            self.processing_service.rmq_publisher = self.rmq_publisher
            self.deployer.deploy_workers(
                mongodb_url=self.mongodb_url,
                rabbitmq_url=self.rabbitmq_url,
            )
        except Exception as error:
            self.log.exception(f"Failed to start the Processing Server, error: {error}")
            self.log.warning("Trying to stop previously deployed services and workers.")
            self.deployer.stop_all()
            raise

        uvicorn_run(self, host=self.hostname, port=int(self.port))

    async def on_startup(self):
        self.log.info(f"Initializing the Database on: {self.mongodb_url}")
        await initiate_database(db_url=self.mongodb_url)

    async def on_shutdown(self) -> None:
        await self.stop_deployed_agents()

    async def stop_deployed_agents(self) -> None:
        self.deployer.stop_all()

    # Other endpoints

    async def forward_tcp_request_to_uds_mets_server(self, request: Request) -> Dict:
        request_body = await request.json()
        ws_dir_path = request_body["workspace_path"]
        self.deployer.start_uds_mets_server(ws_dir_path=ws_dir_path)
        return self.mets_server_proxy.forward_tcp_request(request_body=request_body)

    async def home_page(self):
        return {
            "message": f"The home page of the {self.title}",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    async def user_workflow_callback_test(self, request: Request):
        payload = await request.json()
        job_id = payload.get("job_id")
        state = payload.get("state")
        self.log.info(
            f"Received test workflow callback: job_id={job_id}, state={state}"
        )
        return JSONResponse(
            status_code=200,
            content={"received": True, "job_id": job_id, "state": state},
        )

    async def kill_mets_server_zombies(
        self, minutes_ago: Optional[int] = None, dry_run: Optional[bool] = None
    ) -> List[int]:
        return kill_mets_server_zombies(minutes_ago=minutes_ago, dry_run=dry_run)

    # Processing service delegation

    async def get_worker_ocrd_tool(self, processor_name: Optional[str]) -> Dict:
        return await self.processing_service.get_worker_ocrd_tool(processor_name)

    async def _is_request_caching_required(
        self, workspace_key: str, output_file_grps: list[str],
        page_ids: list[str], depends_on: list[str]
    ) -> bool:
        cache = self.workspace_service.cache_processing_requests
        cache_current_request = False

        if depends_on:
            cache_current_request = await cache.is_caching_required(depends_on)

        if not cache_current_request:
            cache_current_request = (
                self.workspace_service.cache_locked_pages
                .check_if_locked_pages_for_output_file_grps(
                    workspace_key=workspace_key,
                    output_file_grps=output_file_grps,
                    page_ids=page_ids,
                )
            )
        return cache_current_request

    async def _cache_processing_job_to_db(
        self, workspace_key: str, data: PYJobInput
    ) -> PYJobOutput:
        self.workspace_service.cache_processing_requests.cache_request(
            workspace_key, data
        )
        return await self.processing_service.cache_processing_job_to_db(data)

    async def validate_and_forward_job_to_worker(
        self, processor_name: str, data: PYJobInput
    ) -> PYJobOutput:
        data.processor_name = processor_name
        self.processing_service.validate_worker_existence(data.processor_name)

        if data.job_id:
            raise_http_exception(
                self.log, status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Processing request job id field is set but must not be: {data.job_id}"
            )

        data.job_id = generate_id()
        ocrd_tool = await self.processing_service.get_worker_ocrd_tool(data.processor_name)
        validate_job_input(self.log, data.processor_name, ocrd_tool, data)

        if data.workspace_id:
            await get_from_database_workspace(self.log, data.workspace_id)
            workspace_key = data.workspace_id
        elif data.path_to_mets:
            await create_workspace_if_not_exists(self.log, mets_path=data.path_to_mets)
            workspace_key = data.path_to_mets
        else:
            raise_http_exception(
                self.log, status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Either 'path_to_mets' or 'workspace_id' must be set for the provided workspace."
            )

        self.workspace_service.cache_processing_requests.update_request_counter(
            workspace_key=workspace_key, by_value=0
        )

        request_mets_path = await validate_and_return_mets_path(self.log, data)
        page_ids = expand_page_ids(data.page_id)
        cache_current_request = await self._is_request_caching_required(
            workspace_key, data.output_file_grps, page_ids, data.depends_on
        )

        if cache_current_request:
            return await self._cache_processing_job_to_db(workspace_key, data)

        return await self._dispatch_processing_job(
            data=data,
            workspace_key=workspace_key,
            page_ids=page_ids,
            request_mets_path=request_mets_path,
        )

    async def _dispatch_processing_job(
        self, data: PYJobInput, workspace_key: str,
        page_ids: List[str], request_mets_path: str
    ) -> PYJobOutput:
        async with self.workspace_service.get_workspace_lock(workspace_key):
            self.workspace_service.lock_pages(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=page_ids,
            )
            ws_dir_path = str(Path(request_mets_path).parent)
            mets_server_url = self.deployer.start_uds_mets_server(
                ws_dir_path=ws_dir_path
            )

            if self.use_tcp_mets:
                mets_server_url = self.multiplexing_endpoint

            await db_update_workspace(
                workspace_id=data.workspace_id,
                workspace_mets_path=data.path_to_mets,
                mets_server_url=mets_server_url,
            )

            db_queued_job = DBProcessorJob(
                **data.dict(exclude_unset=True, exclude_none=True),
                internal_callback_url=self.internal_job_callback_url,
                state=JobState.queued,
            )
            await db_queued_job.insert()
            self.workspace_service.cache_processing_requests.update_request_counter(
                workspace_key=workspace_key, by_value=1
            )
            return await self.processing_service.push_job_to_worker(
                data=data, db_job=db_queued_job
            )

    async def get_processor_job(self, job_id: str):
        return await self.processing_service.get_processor_job(job_id)

    async def get_processor_job_log(self, job_id: str):
        return await self.processing_service.get_processor_job_log(job_id)

    async def list_processors(self) -> List[str]:
        return await self.processing_service.list_processors()

    # Workspace service delegation

    async def push_cached_jobs_to_workers(
            self, processing_jobs: List[PYJobInput]
    ) -> None:
        if not processing_jobs:
            self.log.debug("No processing jobs were consumed from the requests cache")
            return

        for data in processing_jobs:
            self.log.info(
                f"Changing the job status of: {data.job_id} "
                f"from {JobState.cached} to {JobState.queued}"
            )
            db_consumed_job = await db_update_processing_job(
                job_id=data.job_id, state=JobState.queued
            )
            workspace_key = data.path_to_mets if data.path_to_mets else data.workspace_id

            await self.workspace_service._lock_pages_of_workspace(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=expand_page_ids(data.page_id),
            )
            job_output = await self.processing_service.push_job_to_worker(
                data=data, db_job=db_consumed_job
            )
            if not job_output:
                self.log.exception(
                    f"Failed to create job output for job input data: {data}"
                )

    async def remove_job_from_request_cache(self, result_message: PYResultMessage) -> None:
        await self.workspace_service.remove_job_from_request_cache(result_message)

    # Workflow service delegation

    async def _maybe_finish_workflow(self, workflow_job_id: str) -> None:
        await self.workflow_service.maybe_finish_workflow(workflow_job_id)

    async def task_sequence_to_processing_jobs(self, tasks, mets_path: str, page_id: str):
        return await self.workflow_service.task_sequence_to_processing_jobs(
            tasks, mets_path, page_id
        )

    def validate_tasks_worker_existence(self, tasks) -> None:
        self.workflow_service.validate_tasks_worker_existence(tasks)

    async def run_workflow(
        self,
        mets_path: str,
        workflow: UploadFile = File(None),
        workflow_id: str = None,
        page_id: str = None,
        page_wise: bool = False,
        workflow_callback_url: str = None
    ):
        return await self.workflow_service.run_workflow(
            mets_path=mets_path,
            workflow=workflow,
            workflow_id=workflow_id,
            page_id=page_id,
            page_wise=page_wise,
            workflow_callback_url=workflow_callback_url
        )

    @staticmethod
    def _produce_workflow_status_response(processing_jobs):
        return WorkflowService.produce_workflow_status_response(processing_jobs)

    @staticmethod
    def _produce_workflow_status_simple_response(processing_jobs):
        return WorkflowService.produce_workflow_status_simple_response(processing_jobs)

    async def get_workflow_info(self, workflow_job_id):
        return await self.workflow_service.get_workflow_info(workflow_job_id)

    async def get_workflow_info_simple(self, workflow_job_id):
        return await self.workflow_service.get_workflow_info_simple(workflow_job_id)

    async def upload_workflow(self, workflow):
        return await self.workflow_service.upload_workflow(workflow)

    async def replace_workflow(self, workflow_id, workflow):
        return await self.workflow_service.replace_workflow(workflow_id, workflow)

    async def download_workflow(self, workflow_id):
        return await self.workflow_service.download_workflow(workflow_id)