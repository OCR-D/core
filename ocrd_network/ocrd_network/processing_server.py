import json
import requests
import httpx
from typing import Dict, List, Optional
import uvicorn

from fastapi import FastAPI, status, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pika.exceptions import ChannelClosedByBroker
from ocrd_utils import getLogger
from .database import (
    initiate_database,
    db_get_processing_job,
    db_get_workspace,
    db_update_workspace,
)
from .deployer import Deployer
from .models import (
    DBProcessorJob,
    PYJobInput,
    PYJobOutput,
    PYResultMessage,
    StateEnum
)
from .rabbitmq_utils import (
    RMQPublisher,
    OcrdProcessingMessage
)
from .server_utils import (
    _get_processor_job,
    expand_page_ids,
    validate_and_return_mets_path,
    validate_job_input,
)
from .utils import (
    download_ocrd_all_tool_json,
    generate_created_time,
    generate_id
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
        super().__init__(on_startup=[self.on_startup], on_shutdown=[self.on_shutdown],
                         title='OCR-D Processing Server',
                         description='OCR-D processing and processors')
        self.log = getLogger(__name__)
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

        # Used for buffering/caching processing requests in the Processing Server
        # Key: `workspace_id` or `path_to_mets` depending on which is provided
        # Value: Queue that holds PYInputJob elements
        self.processing_requests_cache = {}

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
            path='/processor/{processor_name}',
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
            path='/processor/{processor_name}/{job_id}',
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
            path='/result_callback',
            endpoint=self.remove_from_request_cache,
            methods=['POST'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Callback used by a worker or processor server for reporting result of a processing request',
        )

        self.router.add_api_route(
            path='/processor/{processor_name}',
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

        # TODO: Remove
        """
        queue_names = set([])
        for data_host in self.deployer.data_hosts:
            for data_worker in data_host.data_workers:
                queue_names.add(data_worker.processor_name)
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

    def check_if_queue_exists(self, processor_name):
        try:
            # Only checks if the process queue exists, if not raises ChannelClosedByBroker
            self.rmq_publisher.create_queue(processor_name, passive=True)
        except ChannelClosedByBroker as error:
            self.log.warning(f"Process queue with id '{processor_name}' not existing: {error}")
            # Reconnect publisher - not efficient, but works
            # TODO: Revisit when reconnection strategy is implemented
            self.connect_publisher(enable_acks=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Process queue with id '{processor_name}' not existing"
            )

    # Returns true if all dependent jobs' states are success, else false
    async def check_if_job_dependencies_met(self, dependencies: List[str]) -> bool:
        # Check the states of all dependent jobs
        for dependency_job_id in dependencies:
            self.log.debug(f"dependency_job_id: {dependency_job_id}")
            try:
                dependency_job_state = (await db_get_processing_job(dependency_job_id)).state
            except ValueError:
                # job_id not (yet) in db. Dependency not met
                return False
            self.log.debug(f"dependency_job_state: {dependency_job_state}")
            # Found a dependent job whose state is not success
            if dependency_job_state != StateEnum.success:
                return False
        return True

    async def find_next_request_from_internal_queue(self, internal_queue: List[PYJobInput]) -> PYJobInput:
        found_request = None
        for i, current_element in enumerate(internal_queue):
            # Request has other job dependencies
            if current_element.depends_on:
                self.log.debug(f"current_element: {current_element}")
                self.log.debug(f"job dependencies: {current_element.depends_on}")
                satisfied_dependencies = await self.check_if_job_dependencies_met(current_element.depends_on)
                self.log.debug(f"satisfied dependencies: {satisfied_dependencies}")
                if not satisfied_dependencies:
                    continue
            # Consume the request from the internal queue
            found_request = internal_queue.pop(i)
            self.log.debug(f"found cached request to be processed: {found_request}")
            break
        return found_request

    def query_ocrd_tool_json_from_server(self, processor_name):
        processor_server_url = self.deployer.resolve_processor_server_url(processor_name)
        if not processor_server_url:
            self.log.exception(f"Processor Server of '{processor_name}' is not available")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processor Server of '{processor_name}' is not available"
            )
        # Request the tool json from the Processor Server
        response = requests.get(
            processor_server_url,
            headers={'Content-Type': 'application/json'}
        )
        if not response.status_code == 200:
            self.log.exception(f"Failed to retrieve '{processor_name}' from: {processor_server_url}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve '{processor_name}' from: {processor_server_url}"
            )
        ocrd_tool = response.json()
        return ocrd_tool, processor_server_url

    async def push_processor_job(self, processor_name: str, data: PYJobInput) -> PYJobOutput:
        if data.job_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Job id field is set but must not be: {data.job_id}"
            )
        # Generate processing job id
        data.job_id = generate_id()

        # Append the processor name to the request itself
        data.processor_name = processor_name

        if data.agent_type not in ['worker', 'server']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown network agent with value: {data.agent_type}"
            )
        workspace_db = await db_get_workspace(
            workspace_id=data.workspace_id,
            workspace_mets_path=data.path_to_mets
        )
        if not workspace_db:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Workspace with id: {data.workspace_id} or path: {data.path_to_mets} not found"
            )

        # Since the path is not resolved yet,
        # the return value is not important for the Processing Server
        await validate_and_return_mets_path(self.log, data)

        page_ids = expand_page_ids(data.page_id)

        # A flag whether the current request must be cached
        # This is set to true if for any output fileGrp there
        # is a page_id value that has been previously locked
        cache_current_request = False

        # Check if there are any dependencies of the current request
        if data.depends_on:
            if not await self.check_if_job_dependencies_met(data.depends_on):
                self.log.debug(f"Caching the received request due to job dependencies")
                cache_current_request = True

        locked_ws_pages = workspace_db.pages_locked
        # No need for further check if the request should be cached
        if not cache_current_request:
            # Check if there are any locked pages for the current request
            for output_fileGrp in data.output_file_grps:
                if output_fileGrp in locked_ws_pages:
                    if "all_pages" in locked_ws_pages[output_fileGrp]:
                        self.log.debug(f"Caching the received request due to locked output file grp pages")
                        cache_current_request = True
                        break
                    # If there are request page ids that are already locked
                    if not set(locked_ws_pages[output_fileGrp]).isdisjoint(page_ids):
                        self.log.debug(f"Caching the received request due to locked output file grp pages")
                        cache_current_request = True
                        break

        if cache_current_request:
            workspace_key = data.workspace_id if data.workspace_id else data.path_to_mets
            # If a record queue of this workspace_id does not exist in the requests cache
            if not self.processing_requests_cache.get(workspace_key, None):
                self.log.debug(f"Creating an internal queue for workspace_key: {workspace_key}")
                self.processing_requests_cache[workspace_key] = []
            self.log.debug(f"Caching the processing request: {data}")
            # Add the processing request to the end of the internal queue
            self.processing_requests_cache[workspace_key].append(data)

            return PYJobOutput(
                job_id=data.job_id,
                processor_name=processor_name,
                workspace_id=data.workspace_id,
                workspace_path=data.path_to_mets,
                state=StateEnum.cached
            )
        else:
            # Update locked pages by locking the pages in the request
            for output_fileGrp in data.output_file_grps:
                if output_fileGrp not in locked_ws_pages:
                    self.log.debug(f"Creating an empty list for output file grp: {output_fileGrp}")
                    locked_ws_pages[output_fileGrp] = []
                # The page id list is not empty - only some pages are in the request
                if page_ids:
                    self.log.debug(f"Locking pages for `{output_fileGrp}`: {page_ids}")
                    locked_ws_pages[output_fileGrp].extend(page_ids)
                else:
                    # Lock all pages with a single value
                    self.log.debug(f"Locking all pages for `{output_fileGrp}`")
                    locked_ws_pages[output_fileGrp].append("all_pages")

            # Update the locked pages dictionary in the database
            await db_update_workspace(
                workspace_id=data.workspace_id,
                workspace_mets_path=data.path_to_mets,
                pages_locked=locked_ws_pages
            )

        # Create a DB entry
        job = DBProcessorJob(
            **data.dict(exclude_unset=True, exclude_none=True),
            internal_callback_url=self.internal_job_callback_url,
            state=StateEnum.queued
        )
        await job.insert()

        job_output = None
        if data.agent_type == 'worker':
            ocrd_tool = await self.get_processor_info(processor_name)
            validate_job_input(self.log, processor_name, ocrd_tool, data)
            processing_message = self.create_processing_message(job)
            await self.push_to_processing_queue(processor_name, processing_message)
            job_output = job.to_job_output()
        if data.agent_type == 'server':
            ocrd_tool, processor_server_url = self.query_ocrd_tool_json_from_server(processor_name)
            validate_job_input(self.log, processor_name, ocrd_tool, data)
            job_output = await self.push_to_processor_server(processor_name, processor_server_url, data)
        if not job_output:
            self.log.exception('Failed to create job output')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to create job output'
            )
        return job_output

    # TODO: Revisit and remove duplications between push_to_* methods
    async def push_to_processing_queue(self, processor_name: str, processing_message: OcrdProcessingMessage):
        if not self.rmq_publisher:
            raise Exception('RMQPublisher is not connected')
        deployed_processors = self.deployer.find_matching_processors(
            worker_only=True,
            str_names_only=True,
            unique_only=True
        )
        if processor_name not in deployed_processors:
            self.check_if_queue_exists(processor_name)

        encoded_processing_message = OcrdProcessingMessage.encode_yml(processing_message)
        try:
            self.rmq_publisher.publish_to_queue(processor_name, encoded_processing_message)
        except Exception as error:
            self.log.exception(f'RMQPublisher has failed: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'RMQPublisher has failed: {error}'
            )

    async def push_to_processor_server(self, processor_name: str, processor_server_url: str, job_input: PYJobInput) -> PYJobOutput:
        try:
            json_data = json.dumps(job_input.dict(exclude_unset=True, exclude_none=True))
        except Exception as e:
            self.log.exception(f"Failed to json dump the PYJobInput, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to json dump the PYJobInput, error: {e}"
            )

        # TODO: The amount of pages should come as a request input
        # TODO: cf https://github.com/OCR-D/core/pull/1030/files#r1152551161
        #  currently, use 200 as a default
        amount_of_pages = 200
        request_timeout = 20.0 * amount_of_pages  # 20 sec timeout per page
        # Post a processing job to the Processor Server asynchronously
        timeout = httpx.Timeout(timeout=request_timeout, connect=30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                processor_server_url,
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

    async def get_processor_job(self, processor_name: str, job_id: str) -> PYJobOutput:
        return await _get_processor_job(self.log, processor_name, job_id)

    async def remove_from_request_cache(self, result_message: PYResultMessage):
        job_id = result_message.job_id
        state = result_message.state
        path_to_mets = result_message.path_to_mets
        workspace_id = result_message.workspace_id

        self.log.debug(f"Received result for job with id: {job_id} has state: {state}")

        if state == StateEnum.failed:
            # TODO: Call the callback to the Workflow server if the current processing step has failed
            pass

        if state != StateEnum.success:
            # TODO: Handle other potential error cases
            pass

        job_db = await db_get_processing_job(job_id)
        if not job_db:
            self.log.exception(f"Processing job with id: {job_id} not found in DB")
        job_output_file_grps = job_db.output_file_grps
        job_page_ids = expand_page_ids(job_db.page_id)

        # Read DB workspace entry
        workspace_db = await db_get_workspace(
            workspace_id=workspace_id,
            workspace_mets_path=path_to_mets
        )
        if not workspace_db:
            self.log.exception(f"Workspace with id: {workspace_id} or path: {path_to_mets} not found in DB")

        # Update locked pages by unlocking the pages in the request
        locked_ws_pages = workspace_db.pages_locked
        for output_fileGrp in job_output_file_grps:
            if output_fileGrp in locked_ws_pages:
                if job_page_ids:
                    # Unlock the previously locked pages
                    self.log.debug(f"Unlocking pages of `{output_fileGrp}`: {job_page_ids}")
                    locked_ws_pages[output_fileGrp] = [x for x in locked_ws_pages[output_fileGrp] if x not in job_page_ids]
                    self.log.debug(f"Remaining locked pages of `{output_fileGrp}`: {locked_ws_pages[output_fileGrp]}")
                else:
                    # Remove the single variable used to indicate all pages are locked
                    self.log.debug(f"Unlocking all pages for: {output_fileGrp}")
                    locked_ws_pages[output_fileGrp].remove("all_pages")

        # Update the locked pages dictionary in the database
        await db_update_workspace(
            workspace_id=workspace_id,
            workspace_mets_path=path_to_mets,
            pages_locked=locked_ws_pages
        )

        # Take the next request from the cache (if any available)
        workspace_key = workspace_id if workspace_id else path_to_mets

        if workspace_key not in self.processing_requests_cache:
            self.log.debug(f"No internal queue available for workspace with key: {workspace_key}")
            return

        if not len(self.processing_requests_cache[workspace_key]):
            # The queue is empty - delete it
            try:
                del self.processing_requests_cache[workspace_key]
            except KeyError as ex:
                self.log.warning(f"Trying to delete non-existing internal queue with key: {workspace_key}")
            return

        data = await self.find_next_request_from_internal_queue(self.processing_requests_cache[workspace_key])
        # Nothing was consumed from the internal queue
        if not data:
            self.log.debug("No data was consumed from the internal queue")
            return

        processor_name = data.processor_name
        # Create a DB entry
        job = DBProcessorJob(
            **data.dict(exclude_unset=True, exclude_none=True),
            internal_callback_url=self.internal_job_callback_url,
            state=StateEnum.queued
        )
        await job.insert()

        job_output = None
        if data.agent_type == 'worker':
            ocrd_tool = await self.get_processor_info(processor_name)
            validate_job_input(self.log, processor_name, ocrd_tool, data)
            processing_message = self.create_processing_message(job)
            await self.push_to_processing_queue(processor_name, processing_message)
            job_output = job.to_job_output()
        if data.agent_type == 'server':
            ocrd_tool, processor_server_url = self.query_ocrd_tool_json_from_server(processor_name)
            validate_job_input(self.log, processor_name, ocrd_tool, data)
            job_output = await self.push_to_processor_server(processor_name, processor_server_url, data)
        if not job_output:
            self.log.exception(f'Failed to create job output for job input data: {data}')

    async def get_processor_info(self, processor_name) -> Dict:
        """ Return a processor's ocrd-tool.json
        """
        ocrd_tool = self.ocrd_all_tool_json.get(processor_name, None)
        if not ocrd_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
