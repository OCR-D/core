from os import getpid
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ocrd_utils import initLogging, getLogger
from uvicorn import run as uvicorn_run

from ..database import initiate_database
from ..logging_utils import configure_file_handler_with_formatter, get_processing_server_logging_file_path
from ..rabbitmq_utils import connect_rabbitmq_publisher
from ..runtime_data import Deployer
from ..tcp_to_uds_mets_proxy import MetsServerProxy
from ..utils import load_ocrd_all_tool_json

from .routers.others import create_others_router
from .routers.processing import create_processing_router
from .routers.workflow import create_workflow_router
from .services.coordinator import ProcessingCoordinator
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
            description="OCR-D Processing Server"
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
            "password": self.deployer.data_queue.cred_password
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
            multiplexing_endpoint=self.multiplexing_endpoint
        )
        self.processing_coordinator = ProcessingCoordinator(
            log=self.log,
            deployer=self.deployer,
            processing_service=self.processing_service,
            workspace_service=self.workspace_service,
            internal_job_callback_url=self.internal_job_callback_url,
            use_tcp_mets=self.use_tcp_mets,
            multiplexing_endpoint=self.multiplexing_endpoint
        )
        self.workflow_service = WorkflowService(
            log=self.log,
            processing_job_callback=self.processing_coordinator.validate_and_forward_job_to_worker,
            worker_validation_callback=self.processing_service.validate_worker_existence,
            stop_mets_server_callback=self.workspace_service.maybe_stop_mets_server
        )

        self.workspace_service.set_cached_jobs_callback(self.processing_coordinator.push_cached_jobs_to_workers)
        self.workspace_service.set_workflow_completion_callback(self.workflow_service.maybe_finish_workflow)

        self.include_router(create_others_router(self, self.log))
        self.include_router(
            create_processing_router(
                processing_service=self.processing_service,
                processing_coordinator=self.processing_coordinator,
                workspace_service=self.workspace_service
            )
        )
        self.include_router(create_workflow_router(self.workflow_service))

        @self.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
            exc_str = str(exc).replace("\n", " ").replace("   ", " ")
            self.log.error(f"{request}: {exc_str}")
            content = {"status_code": 10422, "message": exc_str, "data": None}
            return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Application lifecycle

    def start(self) -> None:
        try:
            self.rabbitmq_url = self.deployer.deploy_rabbitmq()
            self.mongodb_url = self.deployer.deploy_mongodb()
            self.rmq_publisher = connect_rabbitmq_publisher(self.log, self.rmq_data, enable_acks=True)
            self.processing_service.rmq_publisher = self.rmq_publisher
            self.deployer.deploy_workers(mongodb_url=self.mongodb_url, rabbitmq_url=self.rabbitmq_url)
        except Exception as error:
            self.log.exception(f"Failed to start the Processing Server, error: {error}")
            self.log.warning("Trying to stop previously deployed services and workers.")
            self.deployer.stop_all()
            raise
        uvicorn_run(self, host=self.hostname, port=int(self.port))

    async def on_startup(self) -> None:
        self.log.info(f"Initializing the Database on: {self.mongodb_url}")
        await initiate_database(db_url=self.mongodb_url)

    async def on_shutdown(self) -> None:
        self.deployer.stop_all()

    async def forward_tcp_request_to_uds_mets_server(self, request: Request) -> Dict[str, Any]:
        request_body = await request.json()
        ws_dir_path = request_body["workspace_path"]
        self.deployer.start_uds_mets_server(ws_dir_path=ws_dir_path)
        return self.mets_server_proxy.forward_tcp_request(request_body=request_body)
