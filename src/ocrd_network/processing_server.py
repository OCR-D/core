from datetime import datetime
from httpx import AsyncClient, Timeout
from json import dumps, loads
from logging import FileHandler, Formatter
from os import getpid
from requests import get as requests_get
from typing import Dict, List, Union
from urllib.parse import urljoin
import uvicorn

from fastapi import FastAPI, File, HTTPException, Request, status, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pika.exceptions import ChannelClosedByBroker

from ocrd.task_sequence import ProcessorTask
from ocrd_utils import initLogging, getLogger, LOG_FORMAT
from .constants import (
    AgentType,
    JobState,
    NETWORK_API_TAG_DISCOVERY,
    NETWORK_API_TAG_PROCESSING,
    NETWORK_API_TAG_TOOLS,
    NETWORK_API_TAG_WORKFLOW,
    OCRD_ALL_JSON_TOOLS_URL
)
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
from .logging_utils import get_processing_server_logging_file_path
from .models import (
    DBProcessorJob,
    DBWorkflowJob,
    DBWorkflowScript,
    PYJobInput,
    PYJobOutput,
    PYResultMessage,
    PYWorkflowJobOutput
)
from .rabbitmq_utils import RMQPublisher, OcrdProcessingMessage
from .server_cache import CacheLockedPages, CacheProcessingRequests
from .server_utils import (
    create_processing_message,
    create_workspace_if_not_exists,
    _get_processor_job,
    _get_processor_job_log,
    get_page_ids_list,
    get_workflow_content,
    get_from_database_workspace,
    get_from_database_workflow_job,
    parse_workflow_tasks,
    raise_http_exception,
    validate_and_return_mets_path,
    validate_first_task_input_file_groups_existence,
    validate_job_input,
    validate_workflow
)
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
        super().__init__(
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            title="OCR-D Processing Server",
            description="OCR-D Processing Server"
        )
        self.log = getLogger("ocrd_network.processing_server")
        log_file = get_processing_server_logging_file_path(pid=getpid())
        file_handler = FileHandler(filename=log_file, mode='a')
        file_handler.setFormatter(Formatter(LOG_FORMAT))
        self.log.addHandler(file_handler)

        self.log.info(f"Downloading ocrd all tool json")
        self.ocrd_all_tool_json = download_ocrd_all_tool_json(ocrd_all_url=OCRD_ALL_JSON_TOOLS_URL)
        self.hostname = host
        self.port = port
        # The deployer is used for:
        # - deploying agents when the Processing Server is started
        # - retrieving runtime data of agents
        self.deployer = Deployer(config_path)
        # Used by processing workers and/or processor servers to report back the results
        if self.deployer.internal_callback_url:
            host = self.deployer.internal_callback_url
            self.internal_job_callback_url = f"{host.rstrip('/')}/result_callback"
        else:
            self.internal_job_callback_url = f"http://{host}:{port}/result_callback"

        self.mongodb_url = None
        self.rabbitmq_url = None
        # TODO: Combine these under a single URL, rabbitmq_utils needs an update
        self.rmq_host = self.deployer.data_queue.host
        self.rmq_port = self.deployer.data_queue.port
        self.rmq_vhost = "/"
        self.rmq_username = self.deployer.data_queue.cred_username
        self.rmq_password = self.deployer.data_queue.cred_password

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
            self.connect_rabbitmq_publisher()
            self.log.debug(f"Creating message queues on RabbitMQ instance url: {self.rabbitmq_url}")
            self.create_message_queues()

            self.deployer.deploy_network_agents(mongodb_url=self.mongodb_url, rabbitmq_url=self.rabbitmq_url)
        except Exception as error:
            self.log.exception(f"Failed to start the Processing Server, error: {error}")
            self.log.warning("Trying to stop previously deployed services and network agents.")
            self.deployer.stop_all()
            raise
        uvicorn.run(self, host=self.hostname, port=int(self.port))

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
        self.router.add_api_route(
            path="/",
            endpoint=self.home_page,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary="Get information about the processing server"
        )

        # Create routes
        self.router.add_api_route(
            path="/stop",
            endpoint=self.stop_deployed_agents,
            methods=["POST"],
            tags=[NETWORK_API_TAG_TOOLS],
            summary="Stop database, queue and processing-workers"
        )

    def add_api_routes_processing(self):
        self.router.add_api_route(
            path="/processor",
            endpoint=self.list_processors,
            methods=["GET"],
            tags=[NETWORK_API_TAG_PROCESSING, NETWORK_API_TAG_DISCOVERY],
            status_code=status.HTTP_200_OK,
            summary="Get a list of all available processors"
        )

        self.router.add_api_route(
            path="/processor/info/{processor_name}",
            endpoint=self.get_network_agent_ocrd_tool,
            methods=["GET"],
            tags=[NETWORK_API_TAG_PROCESSING, NETWORK_API_TAG_DISCOVERY],
            status_code=status.HTTP_200_OK,
            summary="Get information about this processor"
        )

        self.router.add_api_route(
            path="/processor/run/{processor_name}",
            endpoint=self.validate_and_forward_job_to_network_agent,
            methods=["POST"],
            tags=[NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Submit a job to this processor",
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path="/processor/job/{job_id}",
            endpoint=self.get_processor_job,
            methods=["GET"],
            tags=[NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get information about a job based on its ID",
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path="/processor/log/{job_id}",
            endpoint=self.get_processor_job_log,
            methods=["GET"],
            tags=[NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get the log file of a job id"
        )

        self.router.add_api_route(
            path="/result_callback",
            endpoint=self.remove_job_from_request_cache,
            methods=["POST"],
            tags=[NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Callback used by a worker or processor server for reporting result of a processing request"
        )

    def add_api_routes_workflow(self):
        self.router.add_api_route(
            path="/workflow",
            endpoint=self.upload_workflow,
            methods=["POST"],
            tags=[NETWORK_API_TAG_WORKFLOW],
            status_code=status.HTTP_201_CREATED,
            summary="Upload/Register a new workflow script"
        )

        self.router.add_api_route(
            path="/workflow/{workflow_id}",
            endpoint=self.download_workflow,
            methods=["GET"],
            tags=[NETWORK_API_TAG_WORKFLOW],
            status_code=status.HTTP_200_OK,
            summary="Download a workflow script"
        )

        self.router.add_api_route(
            path="/workflow/{workflow_id}",
            endpoint=self.replace_workflow,
            methods=["PUT"],
            tags=[NETWORK_API_TAG_WORKFLOW],
            status_code=status.HTTP_200_OK,
            summary="Update/Replace a workflow script"
        )

        self.router.add_api_route(
            path="/workflow/run",
            endpoint=self.run_workflow,
            methods=["POST"],
            tags=[NETWORK_API_TAG_WORKFLOW, NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Run a workflow",
            response_model=PYWorkflowJobOutput,
            response_model_exclude=["processing_job_ids"],
            response_model_exclude_defaults=True,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path="/workflow/job-simple/{workflow_job_id}",
            endpoint=self.get_workflow_info_simple,
            methods=["GET"],
            tags=[NETWORK_API_TAG_WORKFLOW, NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get simplified overall job status"
        )

        self.router.add_api_route(
            path="/workflow/job/{workflow_job_id}",
            endpoint=self.get_workflow_info,
            methods=["GET"],
            tags=[NETWORK_API_TAG_WORKFLOW, NETWORK_API_TAG_PROCESSING],
            status_code=status.HTTP_200_OK,
            summary="Get information about a workflow run"
        )

    async def home_page(self):
        message = f"The home page of the {self.title}"
        json_message = {
            "message": message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return json_message

    async def stop_deployed_agents(self) -> None:
        self.deployer.stop_all()

    def connect_rabbitmq_publisher(self, enable_acks: bool = True) -> None:
        self.log.info(f'Connecting RMQPublisher to RabbitMQ server: '
                      f'{self.rmq_host}:{self.rmq_port}{self.rmq_vhost}')
        self.rmq_publisher = RMQPublisher(
            host=self.rmq_host,
            port=self.rmq_port,
            vhost=self.rmq_vhost
        )
        self.log.debug(f'RMQPublisher authenticates with username: '
                       f'{self.rmq_username}, password: {self.rmq_password}')
        self.rmq_publisher.authenticate_and_connect(
            username=self.rmq_username,
            password=self.rmq_password
        )
        if enable_acks:
            self.rmq_publisher.enable_delivery_confirmations()
            self.log.info('Delivery confirmations are enabled')
        self.log.info('Successfully connected RMQPublisher.')

    def create_message_queues(self) -> None:
        """ Create the message queues based on the occurrence of
        `workers.name` in the config file.
        """

        # The abstract version of the above lines
        queue_names = self.deployer.find_matching_processors(
            worker_only=True,
            str_names_only=True,
            unique_only=True
        )

        # TODO: Reconsider and refactor this.
        #  Added ocrd-dummy by default if not available for the integration tests.
        #  A proper Processing Worker / Processor Server registration endpoint is needed on the Processing Server side
        if 'ocrd-dummy' not in queue_names:
            queue_names.append('ocrd-dummy')

        for queue_name in queue_names:
            # The existence/validity of the worker.name is not tested.
            # Even if an ocr-d processor does not exist, the queue is created
            self.log.info(f'Creating a message queue with id: {queue_name}')
            self.rmq_publisher.create_queue(queue_name=queue_name)

    def check_if_queue_exists(self, processor_name: str) -> bool:
        try:
            # Only checks if the process queue exists, if not raises ChannelClosedByBroker
            self.rmq_publisher.create_queue(processor_name, passive=True)
            return True
        except ChannelClosedByBroker as error:
            self.log.warning(f"Process queue with id '{processor_name}' not existing: {error}")
            # TODO: Revisit when reconnection strategy is implemented
            # Reconnect publisher, i.e., restore the connection - not efficient, but works
            self.connect_rabbitmq_publisher(enable_acks=True)
            return False

    def query_ocrd_tool_json_from_server(self, processor_server_url: str):
        # Request the ocrd tool json from the Processor Server
        try:
            response = requests_get(
                urljoin(base=processor_server_url, url="info"),
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                message = f"Failed to retrieve tool json from: {processor_server_url}, code: {response.status_code}"
                raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message)
            return response.json()
        except Exception as error:
            message = f"Failed to retrieve ocrd tool json from: {processor_server_url}"
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)

    async def get_network_agent_ocrd_tool(
        self, processor_name: str, agent_type: AgentType = AgentType.PROCESSING_WORKER
    ) -> Dict:
        ocrd_tool = {}
        error_message = f"Network agent of type '{agent_type}' for processor '{processor_name}' not found."
        if agent_type == AgentType.PROCESSING_WORKER:
            ocrd_tool = self.ocrd_all_tool_json.get(processor_name, None)
        elif agent_type == AgentType.PROCESSOR_SERVER:
            processor_server_url = self.deployer.resolve_processor_server_url(processor_name)
            if processor_server_url == '':
                raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, error_message)
            ocrd_tool = self.query_ocrd_tool_json_from_server(processor_server_url)
        else:
            message = f"Unknown agent type: {agent_type}, {type(agent_type)}"
            raise_http_exception(self.log, status_code=status.HTTP_501_NOT_IMPLEMENTED, message=message)
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
        return bool(self.check_if_queue_exists(processor_name=processor_name))

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

        # Start a Mets Server with the current workspace
        mets_server_url = self.deployer.start_unix_mets_server(mets_path=request_mets_path)

        # Assign the mets server url in the database
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
        if data.agent_type == AgentType.PROCESSING_WORKER:
            processing_message = create_processing_message(self.log, db_job)
            self.log.debug(f"Pushing to processing worker: {data.processor_name}, {data.page_id}, {data.job_id}")
            await self.push_job_to_processing_queue(data.processor_name, processing_message)
            job_output = db_job.to_job_output()
        elif data.agent_type == AgentType.PROCESSOR_SERVER:
            self.log.debug(f"Pushing to processor server: {data.processor_name}, {data.page_id}, {data.job_id}")
            job_output = await self.push_job_to_processor_server(data.processor_name, data)
        else:
            message = f"Unknown agent type: {data.agent_type}, {type(data.agent_type)}"
            raise_http_exception(self.log, status_code=status.HTTP_501_NOT_IMPLEMENTED, message=message)
        if not job_output:
            message = f"Failed to create job output for job input: {data}"
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
        return job_output

    async def push_job_to_processing_queue(self, processor_name: str, processing_message: OcrdProcessingMessage):
        if not self.rmq_publisher:
            message = "The Processing Server has no connection to RabbitMQ Server. RMQPublisher is not connected."
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
        try:
            encoded_message = OcrdProcessingMessage.encode_yml(processing_message)
            self.rmq_publisher.publish_to_queue(queue_name=processor_name, message=encoded_message)
        except Exception as error:
            message = (
                f"Processing server has failed to push processing message to queue: {processor_name}, "
                f"Processing message: {processing_message.__dict__}"
            )
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message, error)

    async def push_job_to_processor_server(self, processor_name: str, job_input: PYJobInput) -> PYJobOutput:
        try:
            json_data = dumps(job_input.dict(exclude_unset=True, exclude_none=True))
        except Exception as error:
            message = f"Failed to json dump the PYJobInput: {job_input}"
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message, error)

        processor_server_url = self.deployer.resolve_processor_server_url(processor_name)

        # TODO: The amount of pages should come as a request input
        # TODO: cf https://github.com/OCR-D/core/pull/1030/files#r1152551161
        #  currently, use 200 as a default
        amount_of_pages = 200
        request_timeout = 20.0 * amount_of_pages  # 20 sec timeout per page
        # Post a processing job to the Processor Server asynchronously
        async with AsyncClient(timeout=Timeout(timeout=request_timeout, connect=30.0)) as client:
            response = await client.post(
                urljoin(base=processor_server_url, url="run"),
                headers={"Content-Type": "application/json"},
                json=loads(json_data)
            )

        if response.status_code != 202:
            message = f"Failed to post '{processor_name}' job to: {processor_server_url}"
            raise_http_exception(self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
        job_output = response.json()
        return job_output

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
                self.deployer.stop_unix_mets_server(mets_server_url=mets_server_url)
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
        except ValueError as error:
            message = f"Processing result job with id '{result_job_id}' not found in the DB."
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)

        # Unlock the output file group pages for the result processing request
        await self._unlock_pages_of_workspace(
            workspace_key=workspace_key,
            output_file_grps=db_result_job.output_file_grps,
            page_ids=expand_page_ids(db_result_job.page_id)
        )

        consumed_cached_jobs = await self._consume_cached_jobs_of_workspace(
            workspace_key=workspace_key, mets_server_url=mets_server_url
        )
        await self.push_cached_jobs_to_agents(processing_jobs=consumed_cached_jobs)

    async def list_processors(self) -> List[str]:
        # There is no caching on the Processing Server side
        processor_names_list = self.deployer.find_matching_processors(
            docker_only=False,
            native_only=False,
            worker_only=False,
            server_only=False,
            str_names_only=True,
            unique_only=True
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
            except HTTPException as error:
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

    async def get_workflow_info(self, workflow_job_id) -> Dict:
        """ Return list of a workflow's processor jobs
        """
        workflow_job = await get_from_database_workflow_job(self.log, workflow_job_id)
        job_ids: List[str] = [job_id for lst in workflow_job.processing_job_ids.values() for job_id in lst]
        jobs = await db_get_processing_jobs(job_ids)
        res = {}
        failed_tasks = {}
        failed_tasks_key = "failed-processor-tasks"
        for job in jobs:
            res.setdefault(job.processor_name, {})
            res[job.processor_name].setdefault(job.state.value, 0)
            res[job.processor_name][job.state.value] += 1
            if job.state == JobState.failed:
                if failed_tasks_key not in res:
                    res[failed_tasks_key] = failed_tasks
                failed_tasks.setdefault(job.processor_name, [])
                failed_tasks[job.processor_name].append({
                    "job_id": job.job_id,
                    "page_id": job.page_id,
                })
        return res

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
        workflow_job_state = JobState.unset
        success_jobs = 0
        for job in jobs:
            if job.state == JobState.cached or job.state == JobState.queued:
                continue
            if job.state == JobState.failed or job.state == JobState.cancelled:
                workflow_job_state = JobState.failed
                break
            if job.state == JobState.running:
                workflow_job_state = JobState.running
            if job.state == JobState.success:
                success_jobs += 1
        # if all jobs succeeded
        if len(job_ids) == success_jobs:
            workflow_job_state = JobState.success
        return {"state": workflow_job_state}

    async def upload_workflow(self, workflow: UploadFile) -> Dict:
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

    async def replace_workflow(self, workflow_id, workflow: UploadFile) -> str:
        """ Update a workflow script file in the database
        """
        try:
            db_workflow_script = await db_get_workflow_script(workflow_id)
        except ValueError as error:
            message = f"Workflow script not existing for id '{workflow_id}'."
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)
        workflow_content = await generate_workflow_content(workflow)
        validate_workflow(self.log, workflow_content)
        db_workflow_script.content = workflow_content
        content_hash = generate_workflow_content_hash(workflow_content)
        db_workflow_script.content_hash = content_hash
        await db_workflow_script.save()
        return db_workflow_script.workflow_id

    async def download_workflow(self, workflow_id) -> PlainTextResponse:
        """ Load workflow-script from the database
        """
        try:
            workflow = await db_get_workflow_script(workflow_id)
            return PlainTextResponse(workflow.content)
        except ValueError as error:
            message = f"Workflow script not existing for id '{workflow_id}'."
            raise_http_exception(self.log, status.HTTP_404_NOT_FOUND, message, error)
