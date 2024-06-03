from datetime import datetime
from os import getpid
from pathlib import Path
from typing import Dict, List, Union
from uvicorn import run as uvicorn_run

from fastapi import APIRouter, FastAPI, File, HTTPException, Request, status, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from ocrd.task_sequence import ProcessorTask
from ocrd_utils import initLogging, getLogger
from .constants import AgentType, JobState, OCRD_ALL_JSON_TOOLS_URL, ServerApiTags
from .database import (
    initiate_database,
    db_get_processing_job,
    db_get_processing_jobs,
    db_update_processing_job,
    db_update_workspace,
    db_get_workflow_script,
    db_find_first_workflow_script_by_content
)
from .runtime_data import Deployer
from .logging_utils import configure_file_handler_with_formatter, get_processing_server_logging_file_path
from .models import (
    DBProcessorJob,
    DBWorkflowJob,
    DBWorkflowScript,
    PYJobInput,
    PYJobOutput,
    PYResultMessage,
    PYWorkflowJobOutput
)
from .rabbitmq_utils import (
    check_if_queue_exists,
    connect_rabbitmq_publisher,
    create_message_queues,
    OcrdProcessingMessage
)
from .server_cache import CacheLockedPages, CacheProcessingRequests
from .server_utils import (
    create_processing_message,
    create_workspace_if_not_exists,
    forward_job_to_processor_server,
    _get_processor_job,
    _get_processor_job_log,
    get_page_ids_list,
    get_workflow_content,
    get_from_database_workspace,
    get_from_database_workflow_job,
    parse_workflow_tasks,
    raise_http_exception,
    request_processor_server_tool_json,
    validate_and_return_mets_path,
    validate_first_task_input_file_groups_existence,
    validate_job_input,
    validate_workflow
)
from .tcp_to_uds_mets_proxy import MetsServerProxy
from .utils import (
    download_ocrd_all_tool_json,
    expand_page_ids,
    generate_id,
    generate_workflow_content,
    generate_workflow_content_hash
)


class ProcessingServer(FastAPI):
    """FastAPI app to make ocr-d processor calls

    The Processing-Server receives calls conforming to the ocr-d webapi regarding the processing
    part. It can run ocrd-processors and provides endpoints to discover processors and watch the job
    status.
    The Processing-Server does not execute the processors itself but starts up a queue and a
    database to delegate the calls to processing workers. They are started by the Processing-Server
    and the communication goes through the queue.
    """

    def __init__(self, config_path: str, host: str, port: int) -> None:
        initLogging()
        self.title = "OCR-D Processing Server"
        super().__init__(
            title=self.title,
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            description="OCR-D Processing Server"
        )
        self.log = getLogger("ocrd_network.processing_server")
        log_file = get_processing_server_logging_file_path(pid=getpid())
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        self.log.info(f"Downloading ocrd all tool json")
        self.ocrd_all_tool_json = download_ocrd_all_tool_json(ocrd_all_url=OCRD_ALL_JSON_TOOLS_URL)
        self.hostname = host
        self.port = port

        # The deployer is used for:
        # - deploying agents when the Processing Server is started
        # - retrieving runtime data of agents
        self.deployer = Deployer(config_path)
        # Used for forwarding Mets Server TCP requests to UDS requests
        self.mets_server_proxy = MetsServerProxy()
        self.use_tcp_mets = self.deployer.use_tcp_mets
        # If set, all Mets Server UDS requests are multiplexed over TCP
        # Used by processing workers and/or processor servers to report back the results
        if self.deployer.internal_callback_url:
            host = self.deployer.internal_callback_url
            self.internal_job_callback_url = f"{host.rstrip('/')}/result_callback"
            self.multiplexing_endpoint = f"{host.rstrip('/')}/tcp_mets"
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

        # Gets assigned when `connect_rabbitmq_publisher()` is called on the working object
        self.rmq_publisher = None

        # Used for keeping track of cached processing requests
        self.cache_processing_requests = CacheProcessingRequests()

        # Used for keeping track of locked/unlocked pages of a workspace
        self.cache_locked_pages = CacheLockedPages()

        self.add_api_routes_others()
        self.add_api_routes_processing()
        self.add_api_routes_workflow()

        @self.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
            self.log.error(f'{request}: {exc_str}')
            content = {'status_code': 10422, 'message': exc_str, 'data': None}
            return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def start(self) -> None:
        """ deploy agents (db, queue, workers) and start the processing server with uvicorn
        """
        try:
            self.rabbitmq_url = self.deployer.deploy_rabbitmq()
            self.mongodb_url = self.deployer.deploy_mongodb()

            # The RMQPublisher is initialized and a connection to the RabbitMQ is performed
            self.rmq_publisher = connect_rabbitmq_publisher(self.log, self.rmq_data, enable_acks=True)

            queue_names = self.deployer.find_matching_network_agents(
                worker_only=True, str_names_only=True, unique_only=True
            )
            self.log.debug(f"Creating message queues on RabbitMQ instance url: {self.rabbitmq_url}")
            create_message_queues(logger=self.log, rmq_publisher=self.rmq_publisher, queue_names=queue_names)

            self.deployer.deploy_network_agents(mongodb_url=self.mongodb_url, rabbitmq_url=self.rabbitmq_url)
        except Exception as error:
            self.log.exception(f"Failed to start the Processing Server, error: {error}")
            self.log.warning("Trying to stop previously deployed services and network agents.")
            self.deployer.stop_all()
            raise
        uvicorn_run(self, host=self.hostname, port=int(self.port))

    async def on_startup(self):
        await initiate_database(db_url=self.mongodb_url)

    async def on_shutdown(self) -> None:
        """
        - hosts and pids should be stored somewhere
        - ensure queue is empty or processor is not currently running
        - connect to hosts and kill pids
        """
        await self.stop_deployed_agents()

    def add_api_routes_others(self):
        others_router = APIRouter()
        others_router.add_api_route(
            path="/",
            endpoint=self.home_page,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary="Get information about the processing server"
        )
        others_router.add_api_route(
            path="/stop",
            endpoint=self.stop_deployed_agents,
            methods=["POST"],
            tags=[ServerApiTags.TOOLS],
            summary="Stop database, queue and processing-workers"
        )
        others_router.add_api_route(
            path="/tcp_mets",
            methods=["POST"],
            endpoint=self.forward_tcp_request_to_uds_mets_server,
            tags=[ServerApiTags.WORKSPACE],
            summary="Forward a TCP request to UDS mets server"
        )
        self.include_router(others_router)

    def add_api_routes_processing(self):
        processing_router = APIRouter()
        processing_router.add_api_route(
            path="/processor",
            endpoint=self.list_processors,
            methods=["GET"],
            tags=[ServerApiTags.PROCESSING, ServerApiTags.DISCOVERY],
            status_code=status.HTTP_200_OK,
            summary="Get a list of all available processors"
        )
        processing_router.add_api_route(
            path="/processor/info/{processor_name}",
            endpoint=self.get_network_agent_ocrd_tool,
            methods=["GET"],
            tags=[ServerApiTags.PROCESSING, ServerApiTags.DISCOVERY],
            status_code=status.HTTP_200_OK,
            summary="Get information about this processor"
        )
        processing_router.add_api_route(
            path="/processor/run/{processor_name}",
            endpoint=self.validate_and_forward_job_to_network_agent,
            methods=["POST"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Submit a job to this processor",
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )
        processing_router.add_api_route(
            path="/processor/job/{job_id}",
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
            path="/processor/log/{job_id}",
            endpoint=self.get_processor_job_log,
            methods=["GET"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get the log file of a job id"
        )
        processing_router.add_api_route(
            path="/result_callback",
            endpoint=self.remove_job_from_request_cache,
            methods=["POST"],
            tags=[ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Callback used by a worker or processor server for reporting result of a processing request"
        )
        self.include_router(processing_router)

    def add_api_routes_workflow(self):
        workflow_router = APIRouter()
        workflow_router.add_api_route(
            path="/workflow",
            endpoint=self.upload_workflow,
            methods=["POST"],
            tags=[ServerApiTags.WORKFLOW],
            status_code=status.HTTP_201_CREATED,
            summary="Upload/Register a new workflow script"
        )
        workflow_router.add_api_route(
            path="/workflow/{workflow_id}",
            endpoint=self.download_workflow,
            methods=["GET"],
            tags=[ServerApiTags.WORKFLOW],
            status_code=status.HTTP_200_OK,
            summary="Download a workflow script"
        )
        workflow_router.add_api_route(
            path="/workflow/{workflow_id}",
            endpoint=self.replace_workflow,
            methods=["PUT"],
            tags=[ServerApiTags.WORKFLOW],
            status_code=status.HTTP_200_OK,
            summary="Update/Replace a workflow script"
        )
        workflow_router.add_api_route(
            path="/workflow/run",
            endpoint=self.run_workflow,
            methods=["POST"],
            tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Run a workflow",
            response_model=PYWorkflowJobOutput,
            response_model_exclude_defaults=True,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )
        workflow_router.add_api_route(
            path="/workflow/job-simple/{workflow_job_id}",
            endpoint=self.get_workflow_info_simple,
            methods=["GET"],
            tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get simplified overall job status"
        )
        workflow_router.add_api_route(
            path="/workflow/job/{workflow_job_id}",
            endpoint=self.get_workflow_info,
            methods=["GET"],
            tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get information about a workflow run"
        )
        self.include_router(workflow_router)

    async def forward_tcp_request_to_uds_mets_server(self, request: Request) -> Dict:
        """Forward mets-server-request

        A processor calls a mets related method like add_file with ClientSideOcrdMets. This sends
        a request to this endpoint. This request contains all infomation neccessary to make a call
        to the uds-mets-server. This information is used by `MetsServerProxy` to make a the call
        to the local (local for the processing-server) reachable the uds-mets-server.
        """
        request_body = await request.json()
        ws_dir_path = request_body["workspace_path"]
        self.deployer.start_uds_mets_server(ws_dir_path=ws_dir_path)
        return self.mets_server_proxy.forward_tcp_request(request_body=request_body)

    async def home_page(self):
        message = f"The home page of the {self.title}"
        json_message = {
            "message": message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return json_message

    async def stop_deployed_agents(self) -> None:
        self.deployer.stop_all()

    def query_ocrd_tool_json_from_server(self, processor_name: str) -> Dict:
        processor_server_base_url = self.deployer.resolve_processor_server_url(processor_name)
        if processor_server_base_url == '':
            message = f"Processor Server URL of '{processor_name}' not found"
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message=message)
        return request_processor_server_tool_json(self.log, processor_server_base_url=processor_server_base_url)

    async def get_network_agent_ocrd_tool(
        self, processor_name: str, agent_type: AgentType = AgentType.PROCESSING_WORKER
    ) -> Dict:
        ocrd_tool = {}
        error_message = f"Network agent of type '{agent_type}' for processor '{processor_name}' not found."
        if agent_type != AgentType.PROCESSING_WORKER and agent_type != AgentType.PROCESSOR_SERVER:
            message = f"Unknown agent type: {agent_type}, {type(agent_type)}"
            raise_http_exception(self.log, status_code=status.HTTP_501_NOT_IMPLEMENTED, message=message)
        if agent_type == AgentType.PROCESSING_WORKER:
            ocrd_tool = self.ocrd_all_tool_json.get(processor_name, None)
        if agent_type == AgentType.PROCESSOR_SERVER:
            ocrd_tool = self.query_ocrd_tool_json_from_server(processor_name)
        if not ocrd_tool:
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, error_message)
        return ocrd_tool

    def network_agent_exists_server(self, processor_name: str) -> bool:
        processor_server_url = self.deployer.resolve_processor_server_url(processor_name)
        return bool(processor_server_url)

    def network_agent_exists_worker(self, processor_name: str) -> bool:
        # TODO: Reconsider and refactor this.
        #  Added ocrd-dummy by default if not available for the integration tests.
        #  A proper Processing Worker / Processor Server registration endpoint
        #  is needed on the Processing Server side
        if processor_name == 'ocrd-dummy':
            return True
        return bool(check_if_queue_exists(self.log, self.rmq_data, processor_name=processor_name))

    def validate_agent_type_and_existence(self, processor_name: str, agent_type: AgentType) -> None:
        agent_exists = False
        if agent_type == AgentType.PROCESSOR_SERVER:
            agent_exists = self.network_agent_exists_server(processor_name=processor_name)
        elif agent_type == AgentType.PROCESSING_WORKER:
            agent_exists = self.network_agent_exists_worker(processor_name=processor_name)
        else:
            message = f"Unknown agent type: {agent_type}, {type(agent_type)}"
            raise_http_exception(self.log, status_code=status.HTTP_501_NOT_IMPLEMENTED, message=message)
        if not agent_exists:
            message = f"Network agent of type '{agent_type}' for processor '{processor_name}' not found."
            raise_http_exception(self.log, status.HTTP_422_UNPROCESSABLE_ENTITY, message)

    async def validate_and_forward_job_to_network_agent(self, processor_name: str, data: PYJobInput) -> PYJobOutput:
        # Append the processor name to the request itself
        data.processor_name = processor_name
        self.validate_agent_type_and_existence(processor_name=data.processor_name, agent_type=data.agent_type)
        if data.job_id:
            message = f"Processing request job id field is set but must not be: {data.job_id}"
            raise_http_exception(self.log, status.HTTP_422_UNPROCESSABLE_ENTITY, message)
        # Generate processing job id
        data.job_id = generate_id()
        ocrd_tool = await self.get_network_agent_ocrd_tool(
            processor_name=data.processor_name,
            agent_type=data.agent_type
        )
        validate_job_input(self.log, data.processor_name, ocrd_tool, data)

        if data.workspace_id:
            # just a check whether the workspace exists in the database or not
            await get_from_database_workspace(self.log, data.workspace_id)
        else:  # data.path_to_mets provided instead
            await create_workspace_if_not_exists(self.log, mets_path=data.path_to_mets)

        workspace_key = data.path_to_mets if data.path_to_mets else data.workspace_id
        # initialize the request counter for the workspace_key
        self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=0)

        # This check is done to return early in case a workspace_id is provided
        # but the abs mets path cannot be queried from the DB
        request_mets_path = await validate_and_return_mets_path(self.log, data)

        page_ids = expand_page_ids(data.page_id)

        # A flag whether the current request must be cached
        # This is set to true if for any output file group there
        # is a page_id value that has been previously locked
        cache_current_request = False

        # Check if there are any dependencies of the current request
        if data.depends_on:
            cache_current_request = await self.cache_processing_requests.is_caching_required(data.depends_on)

        # No need for further check of locked pages dependency
        # if the request should be already cached
        if not cache_current_request:
            # Check if there are any locked pages for the current request
            cache_current_request = self.cache_locked_pages.check_if_locked_pages_for_output_file_grps(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=page_ids
            )

        if cache_current_request:
            # Cache the received request
            self.cache_processing_requests.cache_request(workspace_key, data)

            # Create a cached job DB entry
            db_cached_job = DBProcessorJob(
                **data.dict(exclude_unset=True, exclude_none=True),
                internal_callback_url=self.internal_job_callback_url,
                state=JobState.cached
            )
            await db_cached_job.insert()
            return db_cached_job.to_job_output()

        # Lock the pages in the request
        self.cache_locked_pages.lock_pages(
            workspace_key=workspace_key,
            output_file_grps=data.output_file_grps,
            page_ids=page_ids
        )

        # Start a UDS Mets Server with the current workspace
        ws_dir_path = str(Path(request_mets_path).parent)
        mets_server_url = self.deployer.start_uds_mets_server(ws_dir_path=ws_dir_path)
        if self.use_tcp_mets:
            # let workers talk to mets server via tcp instead of using unix-socket
            mets_server_url = self.multiplexing_endpoint

        # Assign the mets server url in the database (workers read mets_server_url from db)
        await db_update_workspace(
            workspace_id=data.workspace_id,
            workspace_mets_path=data.path_to_mets,
            mets_server_url=mets_server_url
        )

        # Create a queued job DB entry
        db_queued_job = DBProcessorJob(
            **data.dict(exclude_unset=True, exclude_none=True),
            internal_callback_url=self.internal_job_callback_url,
            state=JobState.queued
        )
        await db_queued_job.insert()
        self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=1)
        job_output = await self.push_job_to_network_agent(data=data, db_job=db_queued_job)
        return job_output

    async def push_job_to_network_agent(self, data: PYJobInput, db_job: DBProcessorJob) -> PYJobOutput:
        if data.agent_type != AgentType.PROCESSING_WORKER and data.agent_type != AgentType.PROCESSOR_SERVER:
            message = f"Unknown agent type: {data.agent_type}, {type(data.agent_type)}"
            raise_http_exception(self.log, status_code=status.HTTP_501_NOT_IMPLEMENTED, message=message)
        job_output = None
        self.log.debug(f"Pushing to {data.agent_type}: {data.processor_name}, {data.page_id}, {data.job_id}")
        if data.agent_type == AgentType.PROCESSING_WORKER:
            job_output = await self.push_job_to_processing_queue(db_job=db_job)
        if data.agent_type == AgentType.PROCESSOR_SERVER:
            job_output = await self.push_job_to_processor_server(job_input=data)
        if not job_output:
            message = f"Failed to create job output for job input: {data}"
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
        return job_output

    async def push_job_to_processing_queue(self, db_job: DBProcessorJob) -> PYJobOutput:
        if not self.rmq_publisher:
            message = "The Processing Server has no connection to RabbitMQ Server. RMQPublisher is not connected."
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
        processing_message = create_processing_message(self.log, db_job)
        try:
            encoded_message = OcrdProcessingMessage.encode_yml(processing_message)
            self.rmq_publisher.publish_to_queue(queue_name=db_job.processor_name, message=encoded_message)
        except Exception as error:
            message = (
                f"Processing server has failed to push processing message to queue: {db_job.processor_name}, "
                f"Processing message: {processing_message.__dict__}"
            )
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message, error)
        return db_job.to_job_output()

    async def push_job_to_processor_server(self, job_input: PYJobInput) -> PYJobOutput:
        processor_server_base_url = self.deployer.resolve_processor_server_url(job_input.processor_name)
        return await forward_job_to_processor_server(
            self.log, job_input=job_input, processor_server_base_url=processor_server_base_url
        )

    async def get_processor_job(self, job_id: str) -> PYJobOutput:
        return await _get_processor_job(self.log, job_id)

    async def get_processor_job_log(self, job_id: str) -> FileResponse:
        return await _get_processor_job_log(self.log, job_id)

    async def _lock_pages_of_workspace(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> None:
        # Lock the output file group pages for the current request
        self.cache_locked_pages.lock_pages(
            workspace_key=workspace_key,
            output_file_grps=output_file_grps,
            page_ids=page_ids
        )

    async def _unlock_pages_of_workspace(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> None:
        self.cache_locked_pages.unlock_pages(
            workspace_key=workspace_key,
            output_file_grps=output_file_grps,
            page_ids=page_ids
        )

    async def push_cached_jobs_to_agents(self, processing_jobs: List[PYJobInput]) -> None:
        if not len(processing_jobs):
            self.log.debug("No processing jobs were consumed from the requests cache")
            return
        for data in processing_jobs:
            self.log.info(f"Changing the job status of: {data.job_id} from {JobState.cached} to {JobState.queued}")
            db_consumed_job = await db_update_processing_job(job_id=data.job_id, state=JobState.queued)
            workspace_key = data.path_to_mets if data.path_to_mets else data.workspace_id

            # Lock the output file group pages for the current request
            await self._lock_pages_of_workspace(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=expand_page_ids(data.page_id)
            )

            self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=1)
            job_output = await self.push_job_to_network_agent(data=data, db_job=db_consumed_job)
            if not job_output:
                self.log.exception(f"Failed to create job output for job input data: {data}")

    async def _cancel_cached_dependent_jobs(self, workspace_key: str, job_id: str) -> None:
        await self.cache_processing_requests.cancel_dependent_jobs(
            workspace_key=workspace_key,
            processing_job_id=job_id
        )

    async def _consume_cached_jobs_of_workspace(
        self, workspace_key: str, mets_server_url: str
    ) -> List[PYJobInput]:

        # Check whether the internal queue for the workspace key still exists
        if workspace_key not in self.cache_processing_requests.processing_requests:
            self.log.debug(f"No internal queue available for workspace with key: {workspace_key}")
            return []

        # decrease the internal cache counter by 1
        request_counter = self.cache_processing_requests.update_request_counter(
            workspace_key=workspace_key, by_value=-1
        )
        self.log.debug(f"Internal processing job cache counter value: {request_counter}")
        if not len(self.cache_processing_requests.processing_requests[workspace_key]):
            if request_counter <= 0:
                # Shut down the Mets Server for the workspace_key since no
                # more internal callbacks are expected for that workspace
                self.log.debug(f"Stopping the mets server: {mets_server_url}")

                self.deployer.stop_uds_mets_server(mets_server_url=mets_server_url)

                try:
                    # The queue is empty - delete it
                    del self.cache_processing_requests.processing_requests[workspace_key]
                except KeyError:
                    self.log.warning(f"Trying to delete non-existing internal queue with key: {workspace_key}")

                # For debugging purposes it is good to see if any locked pages are left
                self.log.debug(f"Contents of the locked pages cache for: {workspace_key}")
                locked_pages = self.cache_locked_pages.get_locked_pages(workspace_key=workspace_key)
                for output_file_grp in locked_pages:
                    self.log.debug(f"{output_file_grp}: {locked_pages[output_file_grp]}")
            else:
                self.log.debug(f"Internal request cache is empty but waiting for {request_counter} result callbacks.")
            return []
        consumed_requests = await self.cache_processing_requests.consume_cached_requests(workspace_key=workspace_key)
        return consumed_requests

    async def remove_job_from_request_cache(self, result_message: PYResultMessage):
        result_job_id = result_message.job_id
        result_job_state = result_message.state
        path_to_mets = result_message.path_to_mets
        workspace_id = result_message.workspace_id
        self.log.info(f"Result job_id: {result_job_id}, state: {result_job_state}")

        db_workspace = await get_from_database_workspace(self.log, workspace_id, path_to_mets)
        mets_server_url = db_workspace.mets_server_url
        workspace_key = path_to_mets if path_to_mets else workspace_id

        if result_job_state == JobState.failed:
            await self._cancel_cached_dependent_jobs(workspace_key, result_job_id)

        if result_job_state != JobState.success:
            # TODO: Handle other potential error cases
            pass

        try:
            db_result_job = await db_get_processing_job(result_job_id)
            # Unlock the output file group pages for the result processing request
            await self._unlock_pages_of_workspace(
                workspace_key=workspace_key,
                output_file_grps=db_result_job.output_file_grps,
                page_ids=expand_page_ids(db_result_job.page_id)
            )
        except ValueError as error:
            message = f"Processing result job with id '{result_job_id}' not found in the DB."
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)

        consumed_cached_jobs = await self._consume_cached_jobs_of_workspace(
            workspace_key=workspace_key, mets_server_url=mets_server_url
        )
        await self.push_cached_jobs_to_agents(processing_jobs=consumed_cached_jobs)

    async def list_processors(self) -> List[str]:
        # There is no caching on the Processing Server side
        processor_names_list = self.deployer.find_matching_network_agents(
            docker_only=False, native_only=False, worker_only=False, server_only=False,
            str_names_only=True, unique_only=True
        )
        return processor_names_list

    async def task_sequence_to_processing_jobs(
        self,
        tasks: List[ProcessorTask],
        mets_path: str,
        page_id: str,
        agent_type: AgentType = AgentType.PROCESSING_WORKER
    ) -> List[PYJobOutput]:
        temp_file_group_cache = {}
        responses = []
        for task in tasks:
            # Find dependent jobs of the current task
            dependent_jobs = []
            for input_file_grp in task.input_file_grps:
                if input_file_grp in temp_file_group_cache:
                    dependent_jobs.append(temp_file_group_cache[input_file_grp])
            # NOTE: The `task.mets_path` and `task.page_id` is not utilized in low level
            # Thus, setting these two flags in the ocrd process workflow file has no effect
            job_input_data = PYJobInput(
                processor_name=task.executable,
                path_to_mets=mets_path,
                input_file_grps=task.input_file_grps,
                output_file_grps=task.output_file_grps,
                page_id=page_id,
                parameters=task.parameters,
                agent_type=agent_type,
                depends_on=dependent_jobs,
            )
            response = await self.validate_and_forward_job_to_network_agent(
                processor_name=job_input_data.processor_name,
                data=job_input_data
            )
            for file_group in task.output_file_grps:
                temp_file_group_cache[file_group] = response.job_id
            responses.append(response)
        return responses

    def validate_tasks_agents_existence(self, tasks: List[ProcessorTask], agent_type: AgentType) -> None:
        missing_agents = []
        for task in tasks:
            try:
                self.validate_agent_type_and_existence(processor_name=task.executable, agent_type=agent_type)
            except HTTPException:
                # catching the error is not relevant here
                missing_agents.append({task.executable, agent_type})
        if missing_agents:
            message = (
                "Workflow validation has failed. The desired network agents not found. "
                f"Missing processing agents: {missing_agents}"
            )
            raise_http_exception(self.log, status.HTTP_406_NOT_ACCEPTABLE, message)

    async def run_workflow(
        self,
        mets_path: str,
        workflow: Union[UploadFile, None] = File(None),
        workflow_id: str = None,
        agent_type: AgentType = AgentType.PROCESSING_WORKER,
        page_id: str = None,
        page_wise: bool = False,
        workflow_callback_url: str = None
    ) -> PYWorkflowJobOutput:
        await create_workspace_if_not_exists(self.log, mets_path=mets_path)
        workflow_content = await get_workflow_content(self.log, workflow_id, workflow)
        processing_tasks = parse_workflow_tasks(self.log, workflow_content)

        # Validate the input file groups of the first task in the workflow
        validate_first_task_input_file_groups_existence(self.log, mets_path, processing_tasks[0].input_file_grps)

        # Validate existence of agents (processing workers/processor servers)
        # for the ocr-d processors referenced inside tasks
        self.validate_tasks_agents_existence(processing_tasks, agent_type)

        page_ids = get_page_ids_list(self.log, mets_path, page_id)

        # TODO: Reconsider this, the compact page range may not always work if the page_ids are hashes!
        compact_page_range = f"{page_ids[0]}..{page_ids[-1]}"

        if not page_wise:
            responses = await self.task_sequence_to_processing_jobs(
                tasks=processing_tasks,
                mets_path=mets_path,
                page_id=compact_page_range,
                agent_type=agent_type
            )
            processing_job_ids = [response.job_id for response in responses]
            db_workflow_job = DBWorkflowJob(
                job_id=generate_id(),
                page_id=compact_page_range,
                page_wise=page_wise,
                processing_job_ids={compact_page_range: processing_job_ids},
                path_to_mets=mets_path,
                workflow_callback_url=workflow_callback_url
            )
            await db_workflow_job.insert()
            return db_workflow_job.to_job_output()

        all_pages_job_ids = {}
        for current_page in page_ids:
            responses = await self.task_sequence_to_processing_jobs(
                tasks=processing_tasks,
                mets_path=mets_path,
                page_id=current_page,
                agent_type=agent_type
            )
            processing_job_ids = [response.job_id for response in responses]
            all_pages_job_ids[current_page] = processing_job_ids
        db_workflow_job = DBWorkflowJob(
            job_id=generate_id(),
            page_id=compact_page_range,
            page_wise=page_wise,
            processing_job_ids=all_pages_job_ids,
            path_to_mets=mets_path,
            workflow_callback_url=workflow_callback_url
        )
        await db_workflow_job.insert()
        return db_workflow_job.to_job_output()

    @staticmethod
    def _produce_workflow_status_response(processing_jobs: List[DBProcessorJob]) -> Dict:
        response = {}
        failed_tasks = {}
        failed_tasks_key = "failed-processor-tasks"
        for p_job in processing_jobs:
            response.setdefault(p_job.processor_name, {})
            response[p_job.processor_name].setdefault(p_job.state.value, 0)
            response[p_job.processor_name][p_job.state.value] += 1
            if p_job.state == JobState.failed:
                if failed_tasks_key not in response:
                    response[failed_tasks_key] = failed_tasks
                failed_tasks.setdefault(p_job.processor_name, [])
                failed_tasks[p_job.processor_name].append(
                    {"job_id": p_job.job_id, "page_id": p_job.page_id}
                )
        return response

    @staticmethod
    def _produce_workflow_status_simple_response(processing_jobs: List[DBProcessorJob]) -> JobState:
        workflow_job_state = JobState.unset
        success_jobs = 0
        for p_job in processing_jobs:
            if p_job.state == JobState.cached or p_job.state == JobState.queued:
                continue
            if p_job.state == JobState.failed or p_job.state == JobState.cancelled:
                workflow_job_state = JobState.failed
                break
            if p_job.state == JobState.running:
                workflow_job_state = JobState.running
            if p_job.state == JobState.success:
                success_jobs += 1
        if len(processing_jobs) == success_jobs:
            workflow_job_state = JobState.success
        return workflow_job_state

    async def get_workflow_info(self, workflow_job_id) -> Dict:
        """ Return list of a workflow's processor jobs
        """
        workflow_job = await get_from_database_workflow_job(self.log, workflow_job_id)
        job_ids: List[str] = [job_id for lst in workflow_job.processing_job_ids.values() for job_id in lst]
        jobs = await db_get_processing_jobs(job_ids)
        response = self._produce_workflow_status_response(processing_jobs=jobs)
        return response

    async def get_workflow_info_simple(self, workflow_job_id) -> Dict[str, JobState]:
        """
        Simplified version of the `get_workflow_info` that returns a single state for the entire workflow.
        - If a single processing job fails, the entire workflow job status is set to FAILED.
        - If there are any processing jobs running, regardless of other states, such as QUEUED and CACHED,
        the entire workflow job status is set to RUNNING.
        - If all processing jobs has finished successfully, only then the workflow job status is set to SUCCESS
        """
        workflow_job = await get_from_database_workflow_job(self.log, workflow_job_id)
        job_ids: List[str] = [job_id for lst in workflow_job.processing_job_ids.values() for job_id in lst]
        jobs = await db_get_processing_jobs(job_ids)
        workflow_job_state = self._produce_workflow_status_simple_response(processing_jobs=jobs)
        return {"state": workflow_job_state}

    async def upload_workflow(self, workflow: UploadFile) -> Dict[str, str]:
        """ Store a script for a workflow in the database
        """
        workflow_content = await generate_workflow_content(workflow)
        validate_workflow(self.log, workflow_content)
        content_hash = generate_workflow_content_hash(workflow_content)
        try:
            db_workflow_script = await db_find_first_workflow_script_by_content(content_hash)
            if db_workflow_script:
                message = f"The same workflow script already exists, workflow id: {db_workflow_script.workflow_id}"
                raise_http_exception(self.log, status.HTTP_409_CONFLICT, message)
        except ValueError:
            pass
        workflow_id = generate_id()
        db_workflow_script = DBWorkflowScript(
            workflow_id=workflow_id,
            content=workflow_content,
            content_hash=content_hash
        )
        await db_workflow_script.insert()
        return {"workflow_id": workflow_id}

    async def replace_workflow(self, workflow_id, workflow: UploadFile) -> Dict[str, str]:
        """ Update a workflow script file in the database
        """
        try:
            db_workflow_script = await db_get_workflow_script(workflow_id)
            workflow_content = await generate_workflow_content(workflow)
            validate_workflow(self.log, workflow_content)
            db_workflow_script.content = workflow_content
            content_hash = generate_workflow_content_hash(workflow_content)
            db_workflow_script.content_hash = content_hash
            await db_workflow_script.save()
            return {"workflow_id": db_workflow_script.workflow_id}
        except ValueError as error:
            message = f"Workflow script not existing for id '{workflow_id}'."
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)

    async def download_workflow(self, workflow_id) -> PlainTextResponse:
        """ Load workflow-script from the database
        """
        try:
            workflow = await db_get_workflow_script(workflow_id)
            return PlainTextResponse(workflow.content)
        except ValueError as error:
            message = f"Workflow script not existing for id '{workflow_id}'."
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)
