from hashlib import md5
import httpx
import json
from logging import FileHandler, Formatter
from os import getpid
from pathlib import Path
import requests
from typing import Dict, List, Union
from urllib.parse import urljoin
import uvicorn

from fastapi import (
    FastAPI,
    status,
    Request,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pika.exceptions import ChannelClosedByBroker

from ocrd import Resolver, Workspace
from ocrd.task_sequence import ProcessorTask
from ocrd_utils import initLogging, getLogger, LOG_FORMAT

from .constants import NETWORK_AGENT_SERVER, NETWORK_AGENT_WORKER
from .database import (
    initiate_database,
    db_create_workspace,
    db_get_processing_job,
    db_get_processing_jobs,
    db_get_workflow_job,
    db_get_workspace,
    db_update_processing_job,
    db_update_workspace,
    db_get_workflow_script,
    db_find_first_workflow_script_by_content
)
from .deployer import Deployer
from .logging import get_processing_server_logging_file_path
from .models import (
    DBProcessorJob,
    DBWorkflowJob,
    DBWorkflowScript,
    PYJobInput,
    PYJobOutput,
    PYResultMessage,
    PYWorkflowJobOutput,
    StateEnum
)
from .rabbitmq_utils import RMQPublisher, OcrdProcessingMessage
from .server_cache import CacheLockedPages, CacheProcessingRequests
from .server_utils import (
    _get_processor_job,
    _get_processor_job_log,
    expand_page_ids,
    validate_and_return_mets_path,
    validate_job_input
)
from .utils import (
    download_ocrd_all_tool_json,
    generate_created_time,
    generate_id,
    get_ocrd_workspace_physical_pages,
    validate_workflow,
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
            title='OCR-D Processing Server',
            description='OCR-D Processing Server'
        )
        self.log = getLogger('ocrd_network.processing_server')
        log_file = get_processing_server_logging_file_path(pid=getpid())
        file_handler = FileHandler(filename=log_file, mode='a')
        file_handler.setFormatter(Formatter(LOG_FORMAT))
        self.log.addHandler(file_handler)

        self.log.info(f"Downloading ocrd all tool json")
        self.ocrd_all_tool_json = download_ocrd_all_tool_json(
            ocrd_all_url="https://ocr-d.de/js/ocrd-all-tool.json"
        )
        self.hostname = host
        self.port = port
        # The deployer is used for:
        # - deploying agents when the Processing Server is started
        # - retrieving runtime data of agents
        self.deployer = Deployer(config_path)
        self.mongodb_url = None
        # TODO: Combine these under a single URL, rabbitmq_utils needs an update
        self.rmq_host = self.deployer.data_queue.address
        self.rmq_port = self.deployer.data_queue.port
        self.rmq_vhost = '/'
        self.rmq_username = self.deployer.data_queue.username
        self.rmq_password = self.deployer.data_queue.password

        # Gets assigned when `connect_publisher` is called on the working object
        self.rmq_publisher = None

        # Used for keeping track of cached processing requests
        self.cache_processing_requests = CacheProcessingRequests()

        # Used for keeping track of locked/unlocked pages of a workspace
        self.cache_locked_pages = CacheLockedPages()

        # Used by processing workers and/or processor servers to report back the results
        if self.deployer.internal_callback_url:
            host = self.deployer.internal_callback_url
            self.internal_job_callback_url = f'{host.rstrip("/")}/result_callback'
        else:
            self.internal_job_callback_url = f'http://{host}:{port}/result_callback'

        # Create routes
        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_deployed_agents,
            methods=['POST'],
            tags=['tools'],
            summary='Stop database, queue and processing-workers',
        )

        self.router.add_api_route(
            path='/processor/run/{processor_name}',
            endpoint=self.push_processor_job,
            methods=['POST'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Submit a job to this processor',
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/processor/job/{job_id}',
            endpoint=self.get_processor_job,
            methods=['GET'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about a job based on its ID',
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/processor/log/{job_id}',
            endpoint=self.get_processor_job_log,
            methods=['GET'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Get the log file of a job id'
        )

        self.router.add_api_route(
            path='/result_callback',
            endpoint=self.remove_from_request_cache,
            methods=['POST'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Callback used by a worker or processor server for reporting result of a processing request',
        )

        self.router.add_api_route(
            path='/processor/info/{processor_name}',
            endpoint=self.get_processor_info,
            methods=['GET'],
            tags=['processing', 'discovery'],
            status_code=status.HTTP_200_OK,
            summary='Get information about this processor',
        )

        self.router.add_api_route(
            path='/processor',
            endpoint=self.list_processors,
            methods=['GET'],
            tags=['processing', 'discovery'],
            status_code=status.HTTP_200_OK,
            summary='Get a list of all available processors',
        )

        self.router.add_api_route(
            path='/workflow/run',
            endpoint=self.run_workflow,
            methods=['POST'],
            tags=['workflow', 'processing'],
            status_code=status.HTTP_200_OK,
            summary='Run a workflow',
            response_model=PYWorkflowJobOutput,
            response_model_exclude=["processing_job_ids"],
            response_model_exclude_defaults=True,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/workflow/job/{workflow_job_id}',
            endpoint=self.get_workflow_info,
            methods=['GET'],
            tags=['workflow', 'processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about a workflow run',
        )

        self.router.add_api_route(
            path='/workflow',
            endpoint=self.upload_workflow,
            methods=['POST'],
            tags=['workflow'],
            status_code=status.HTTP_201_CREATED,
            summary='Upload/Register a new workflow script',
        )
        self.router.add_api_route(
            path='/workflow/{workflow_id}',
            endpoint=self.replace_workflow,
            methods=['PUT'],
            tags=['workflow'],
            status_code=status.HTTP_200_OK,
            summary='Update/Replace a workflow script',
        )
        self.router.add_api_route(
            path='/workflow/{workflow_id}',
            endpoint=self.download_workflow,
            methods=['GET'],
            tags=['workflow'],
            status_code=status.HTTP_200_OK,
            summary='Download a workflow script',
        )

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
            self.deployer.deploy_rabbitmq(image='rabbitmq:3-management', detach=True, remove=True)
            rabbitmq_url = self.deployer.data_queue.url

            self.deployer.deploy_mongodb(image='mongo', detach=True, remove=True)
            self.mongodb_url = self.deployer.data_mongo.url

            # The RMQPublisher is initialized and a connection to the RabbitMQ is performed
            self.connect_publisher()
            self.log.debug(f'Creating message queues on RabbitMQ instance url: {rabbitmq_url}')
            self.create_message_queues()

            self.deployer.deploy_hosts(
                mongodb_url=self.mongodb_url,
                rabbitmq_url=rabbitmq_url
            )
        except Exception:
            self.log.error('Error during startup of processing server. '
                           'Trying to kill parts of incompletely deployed service')
            self.deployer.kill_all()
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

    async def stop_deployed_agents(self) -> None:
        self.deployer.kill_all()

    def connect_publisher(self, enable_acks: bool = True) -> None:
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

        for queue_name in queue_names:
            # The existence/validity of the worker.name is not tested.
            # Even if an ocr-d processor does not exist, the queue is created
            self.log.info(f'Creating a message queue with id: {queue_name}')
            self.rmq_publisher.create_queue(queue_name=queue_name)

    @staticmethod
    def create_processing_message(job: DBProcessorJob) -> OcrdProcessingMessage:
        processing_message = OcrdProcessingMessage(
            job_id=job.job_id,
            processor_name=job.processor_name,
            created_time=generate_created_time(),
            path_to_mets=job.path_to_mets,
            workspace_id=job.workspace_id,
            input_file_grps=job.input_file_grps,
            output_file_grps=job.output_file_grps,
            page_id=job.page_id,
            parameters=job.parameters,
            result_queue_name=job.result_queue_name,
            callback_url=job.callback_url,
            internal_callback_url=job.internal_callback_url
        )
        return processing_message

    def check_if_queue_exists(self, processor_name) -> bool:
        try:
            # Only checks if the process queue exists, if not raises ChannelClosedByBroker
            self.rmq_publisher.create_queue(processor_name, passive=True)
            return True
        except ChannelClosedByBroker as error:
            self.log.warning(f"Process queue with id '{processor_name}' not existing: {error}")
            # TODO: Revisit when reconnection strategy is implemented
            # Reconnect publisher, i.e., restore the connection - not efficient, but works
            self.connect_publisher(enable_acks=True)
            return False

    def query_ocrd_tool_json_from_server(self, processor_server_url: str):
        # Request the tool json from the Processor Server
        response = requests.get(
            urljoin(processor_server_url, 'info'),
            headers={"Content-Type": "application/json"}
        )
        if not response.status_code == 200:
            msg = f"Failed to retrieve ocrd tool json from: {processor_server_url}, status code: {response.status_code}"
            self.log.exception(msg)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg
            )
        ocrd_tool = response.json()
        return ocrd_tool

    def processing_agent_exists(self, processor_name: str, agent_type: str) -> bool:
        if agent_type not in [NETWORK_AGENT_SERVER, NETWORK_AGENT_WORKER]:
            return False
        if agent_type == NETWORK_AGENT_WORKER:
            if not self.check_if_queue_exists(processor_name):
                return False
        if agent_type == NETWORK_AGENT_SERVER:
            processor_server_url = self.deployer.resolve_processor_server_url(processor_name)
            if not processor_server_url:
                return False
        return True

    async def get_processing_agent_ocrd_tool(self, processor_name: str, agent_type: str) -> dict:
        ocrd_tool = {}
        if agent_type == NETWORK_AGENT_WORKER:
            ocrd_tool = await self.get_processor_info(processor_name)
        if agent_type == NETWORK_AGENT_SERVER:
            processor_server_url = self.deployer.resolve_processor_server_url(processor_name)
            ocrd_tool = self.query_ocrd_tool_json_from_server(processor_server_url)
        return ocrd_tool

    async def push_processor_job(self, processor_name: str, data: PYJobInput) -> PYJobOutput:
        if data.job_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Job id field is set but must not be: {data.job_id}"
            )
        if not data.workspace_id and not data.path_to_mets:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="either 'path_to_mets' or 'workspace_id' must be provided"
            )
        # Generate processing job id
        data.job_id = generate_id()
        # Append the processor name to the request itself
        data.processor_name = processor_name

        # Check if the processing agent (worker/server) exists (is deployed)
        if not self.processing_agent_exists(data.processor_name, data.agent_type):
            msg = f"Agent of type '{data.agent_type}' does not exist for '{data.processor_name}'"
            self.log.exception(msg)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg
            )

        ocrd_tool = await self.get_processing_agent_ocrd_tool(
            processor_name=data.processor_name,
            agent_type=data.agent_type
        )
        if not ocrd_tool:
            msg = f"Agent of type '{data.agent_type}' does not exist for '{data.processor_name}'"
            self.log.exception(msg)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg
            )

        validate_job_input(self.log, data.processor_name, ocrd_tool, data)

        db_workspace = await db_get_workspace(
            workspace_id=data.workspace_id,
            workspace_mets_path=data.path_to_mets
        )
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Workspace with id: {data.workspace_id} or path: {data.path_to_mets} not found"
            )
        workspace_key = data.path_to_mets if data.path_to_mets else data.workspace_id
        # initialize the request counter for the workspace_key
        self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=0)

        # Since the path is not resolved yet,
        # the return value is not important for the Processing Server
        request_mets_path = await validate_and_return_mets_path(self.log, data)

        page_ids = expand_page_ids(data.page_id)

        # A flag whether the current request must be cached
        # This is set to true if for any output fileGrp there
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
                state=StateEnum.cached
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
            state=StateEnum.queued
        )
        await db_queued_job.insert()
        self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=1)
        job_output = await self.push_to_processing_agent(data=data, db_job=db_queued_job)
        return job_output

    async def push_to_processing_agent(self, data: PYJobInput, db_job: DBProcessorJob) -> PYJobOutput:
        if data.agent_type == NETWORK_AGENT_WORKER:
            processing_message = self.create_processing_message(db_job)
            self.log.debug(f"Pushing to processing worker: {data.processor_name}, {data.page_id}, {data.job_id}")
            await self.push_to_processing_queue(data.processor_name, processing_message)
            job_output = db_job.to_job_output()
        else:  # data.agent_type == NETWORK_AGENT_SERVER
            self.log.debug(f"Pushing to processor server: {data.processor_name}, {data.page_id}, {data.job_id}")
            job_output = await self.push_to_processor_server(data.processor_name, data)
        if not job_output:
            self.log.exception('Failed to create job output')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to create job output'
            )
        return job_output

    async def push_to_processing_queue(self, processor_name: str, processing_message: OcrdProcessingMessage):
        if not self.rmq_publisher:
            raise Exception('RMQPublisher is not connected')
        try:
            self.rmq_publisher.publish_to_queue(
                queue_name=processor_name,
                message=OcrdProcessingMessage.encode_yml(processing_message)
            )
        except Exception as error:
            self.log.exception(f'RMQPublisher has failed: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'RMQPublisher has failed: {error}'
            )

    async def push_to_processor_server(
            self,
            processor_name: str,
            job_input: PYJobInput
    ) -> PYJobOutput:
        try:
            json_data = json.dumps(job_input.dict(exclude_unset=True, exclude_none=True))
        except Exception as e:
            msg = f"Failed to json dump the PYJobInput, error: {e}"
            self.log.exception(msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=msg
            )

        processor_server_url = self.deployer.resolve_processor_server_url(processor_name)

        # TODO: The amount of pages should come as a request input
        # TODO: cf https://github.com/OCR-D/core/pull/1030/files#r1152551161
        #  currently, use 200 as a default
        amount_of_pages = 200
        request_timeout = 20.0 * amount_of_pages  # 20 sec timeout per page
        # Post a processing job to the Processor Server asynchronously
        timeout = httpx.Timeout(timeout=request_timeout, connect=30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                urljoin(processor_server_url, 'run'),
                headers={'Content-Type': 'application/json'},
                json=json.loads(json_data)
            )

        if not response.status_code == 202:
            self.log.exception(f"Failed to post '{processor_name}' job to: {processor_server_url}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to post '{processor_name}' job to: {processor_server_url}"
            )
        job_output = response.json()
        return job_output

    async def get_processor_job(self, job_id: str) -> PYJobOutput:
        return await _get_processor_job(self.log, job_id)

    async def get_processor_job_log(self, job_id: str) -> FileResponse:
        return await _get_processor_job_log(self.log, job_id)

    async def remove_from_request_cache(self, result_message: PYResultMessage):
        result_job_id = result_message.job_id
        result_job_state = result_message.state
        path_to_mets = result_message.path_to_mets
        workspace_id = result_message.workspace_id
        self.log.debug(f"Result job_id: {result_job_id}, state: {result_job_state}")

        # Read DB workspace entry
        db_workspace = await db_get_workspace(workspace_id=workspace_id, workspace_mets_path=path_to_mets)
        if not db_workspace:
            self.log.exception(f"Workspace with id: {workspace_id} or path: {path_to_mets} not found in DB")
        mets_server_url = db_workspace.mets_server_url
        workspace_key = path_to_mets if path_to_mets else workspace_id

        if result_job_state == StateEnum.failed:
            await self.cache_processing_requests.cancel_dependent_jobs(
                workspace_key=workspace_key,
                processing_job_id=result_job_id
            )

        if result_job_state != StateEnum.success:
            # TODO: Handle other potential error cases
            pass

        db_result_job = await db_get_processing_job(result_job_id)
        if not db_result_job:
            self.log.exception(f"Processing job with id: {result_job_id} not found in DB")

        # Unlock the output file group pages for the result processing request
        self.cache_locked_pages.unlock_pages(
            workspace_key=workspace_key,
            output_file_grps=db_result_job.output_file_grps,
            page_ids=expand_page_ids(db_result_job.page_id)
        )

        # Take the next request from the cache (if any available)
        if workspace_key not in self.cache_processing_requests.processing_requests:
            self.log.debug(f"No internal queue available for workspace with key: {workspace_key}")
            return

        # decrease the internal counter by 1
        request_counter = self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=-1)
        self.log.debug(f"Internal processing counter value: {request_counter}")
        if not len(self.cache_processing_requests.processing_requests[workspace_key]):
            if request_counter <= 0:
                # Shut down the Mets Server for the workspace_key since no
                # more internal callbacks are expected for that workspace
                self.log.debug(f"Stopping the mets server: {mets_server_url}")
                self.deployer.stop_unix_mets_server(mets_server_url=mets_server_url)
                # The queue is empty - delete it
                try:
                    del self.cache_processing_requests.processing_requests[workspace_key]
                except KeyError:
                    self.log.warning(f"Trying to delete non-existing internal queue with key: {workspace_key}")

                # For debugging purposes it is good to see if any locked pages are left
                self.log.debug(f"Contents of the locked pages cache for: {workspace_key}")
                locked_pages = self.cache_locked_pages.get_locked_pages(workspace_key=workspace_key)
                for output_fileGrp in locked_pages:
                    self.log.debug(f"{output_fileGrp}: {locked_pages[output_fileGrp]}")
            else:
                self.log.debug(f"Internal request cache is empty but waiting for {request_counter} result callbacks.")
            return

        consumed_requests = await self.cache_processing_requests.consume_cached_requests(workspace_key=workspace_key)

        if not len(consumed_requests):
            self.log.debug("No processing jobs were consumed from the requests cache")
            return

        for data in consumed_requests:
            self.log.debug(f"Changing the job status of: {data.job_id} from {StateEnum.cached} to {StateEnum.queued}")
            db_consumed_job = await db_update_processing_job(job_id=data.job_id, state=StateEnum.queued)
            workspace_key = data.path_to_mets if data.path_to_mets else data.workspace_id

            # Lock the output file group pages for the current request
            self.cache_locked_pages.lock_pages(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=expand_page_ids(data.page_id)
            )
            self.cache_processing_requests.update_request_counter(workspace_key=workspace_key, by_value=1)
            job_output = await self.push_to_processing_agent(data=data, db_job=db_consumed_job)
            if not job_output:
                self.log.exception(f'Failed to create job output for job input data: {data}')

    async def get_processor_info(self, processor_name) -> Dict:
        """ Return a processor's ocrd-tool.json
        """
        ocrd_tool = self.ocrd_all_tool_json.get(processor_name, None)
        if not ocrd_tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ocrd tool JSON of '{processor_name}' not available!"
            )

        # TODO: Returns the ocrd tool json even of processors
        #  that are not deployed. This may or may not be desired.
        return ocrd_tool

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
            agent_type: NETWORK_AGENT_WORKER,
    ) -> List[PYJobOutput]:
        file_group_cache = {}
        responses = []
        for task in tasks:
            # Find dependent jobs of the current task
            dependent_jobs = []
            for input_file_grp in task.input_file_grps:
                if input_file_grp in file_group_cache:
                    dependent_jobs.append(file_group_cache[input_file_grp])
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
            response = await self.push_processor_job(
                processor_name=job_input_data.processor_name,
                data=job_input_data
            )
            for file_group in task.output_file_grps:
                file_group_cache[file_group] = response.job_id
            responses.append(response)
        return responses

    async def run_workflow(
            self,
            mets_path: str,
            workflow: Union[UploadFile, None] = File(None),
            workflow_id: str = None,
            agent_type: str = NETWORK_AGENT_WORKER,
            page_id: str = None,
            page_wise: bool = False,
            workflow_callback_url: str = None
    ) -> PYWorkflowJobOutput:
        try:
            # core cannot create workspaces by api, but processing-server needs the workspace in the
            # database. Here the workspace is created if the path available and not existing in db:
            await db_create_workspace(mets_path)
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Mets file not existing: {mets_path}")

        if not workflow:
            if not workflow_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Either workflow or workflow_id must be provided")
            try:
                workflow = await db_get_workflow_script(workflow_id)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Workflow with id '{workflow_id}' not found")
            workflow = workflow.content
        else:
            workflow = (await workflow.read()).decode("utf-8")

        try:
            tasks_list = workflow.splitlines()
            tasks = [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Error parsing tasks: {e}")

        # Validate the input file groups of the first task in the workflow
        available_groups = Workspace(Resolver(), Path(mets_path).parents[0]).mets.file_groups
        for grp in tasks[0].input_file_grps:
            if grp not in available_groups:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Input file grps of 1st processor not found: {tasks[0].input_file_grps}"
                )

        # Validate existence of agents (processing workers/processor servers)
        # for the ocr-d processors referenced inside tasks
        missing_agents = []
        for task in tasks:
            if not self.processing_agent_exists(processor_name=task.executable, agent_type=agent_type):
                missing_agents.append({task.executable, agent_type})
        if missing_agents:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Workflow validation has failed. Processing agents not found: {missing_agents}. "
                       f"Make sure the desired processors are deployed either as a processing "
                       f"worker or processor server"
            )

        try:
            if page_id:
                page_range = expand_page_ids(page_id)
            else:
                # If no page_id is specified, all physical pages are assigned as page range
                page_range = get_ocrd_workspace_physical_pages(mets_path=mets_path)
            compact_page_range = f'{page_range[0]}..{page_range[-1]}'
        except BaseException as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Error determining page-range: {e}")

        if not page_wise:
            responses = await self.task_sequence_to_processing_jobs(
                tasks=tasks,
                mets_path=mets_path,
                page_id=compact_page_range,
                agent_type=agent_type
            )
            processing_job_ids = []
            for response in responses:
                processing_job_ids.append(response.job_id)
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
        for current_page in page_range:
            responses = await self.task_sequence_to_processing_jobs(
                tasks=tasks,
                mets_path=mets_path,
                page_id=current_page,
                agent_type=agent_type
            )
            processing_job_ids = []
            for response in responses:
                processing_job_ids.append(response.job_id)
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
        try:
            workflow_job = await db_get_workflow_job(workflow_job_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Workflow-Job with id: {workflow_job_id} not found")
        job_ids: List[str] = [id for lst in workflow_job.processing_job_ids.values() for id in lst]
        jobs = await db_get_processing_jobs(job_ids)
        res = {}
        failed_tasks = {}
        failed_tasks_key = "failed-processor-tasks"
        for job in jobs:
            res.setdefault(job.processor_name, {})
            res[job.processor_name].setdefault(job.state.value, 0)
            res[job.processor_name][job.state.value] += 1
            if job.state == "FAILED":
                if failed_tasks_key not in res:
                    res[failed_tasks_key] = failed_tasks
                failed_tasks.setdefault(job.processor_name, [])
                failed_tasks[job.processor_name].append({
                    "job_id": job.job_id,
                    "page_id": job.page_id,
                })
        return res

    async def upload_workflow(self, workflow: UploadFile) -> Dict:
        """ Store a script for a workflow in the database
        """
        workflow_id = generate_id()
        content = (await workflow.read()).decode("utf-8")
        if not validate_workflow(content):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Provided workflow script is invalid")

        content_hash = md5(content.encode("utf-8")).hexdigest()
        try:
            db_workflow_script = await db_find_first_workflow_script_by_content(content_hash)
            if db_workflow_script:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The same workflow"
                                    f"-script exists with id '{db_workflow_script.workflow_id}'")
        except ValueError:
            pass

        db_workflow_script = DBWorkflowScript(
            workflow_id=workflow_id,
            content=content,
            content_hash=content_hash,
        )
        await db_workflow_script.insert()
        return {"workflow_id": workflow_id}

    async def replace_workflow(self, workflow_id, workflow: UploadFile) -> str:
        """ Update a workflow script file in the database
        """
        content = (await workflow.read()).decode("utf-8")
        if not validate_workflow(content):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Provided workflow script is invalid")
        try:
            db_workflow_script = await db_get_workflow_script(workflow_id)
            db_workflow_script.content = content
            content_hash = md5(content.encode("utf-8")).hexdigest()
            db_workflow_script.content_hash = content_hash
        except ValueError as e:
            self.log.exception(f"Workflow with id '{workflow_id}' not existing, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow-script with id '{workflow_id}' not existing"
            )
        await db_workflow_script.save()
        return db_workflow_script.workflow_id

    async def download_workflow(self, workflow_id) -> PlainTextResponse:
        """ Load workflow-script from the database
        """
        try:
            workflow = await db_get_workflow_script(workflow_id)
            return PlainTextResponse(workflow.content)
        except ValueError as e:
            self.log.exception(f"Workflow with id '{workflow_id}' not existing, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow-script with id '{workflow_id}' not existing"
            )
