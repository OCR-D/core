import json
import requests
import httpx
from typing import Dict, List
import uvicorn

from fastapi import FastAPI, status, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pika.exceptions import ChannelClosedByBroker

from ocrd_utils import getLogger
from .database import initiate_database
from .deployer import Deployer
from .models import (
    DBProcessorJob,
    PYJobInput,
    PYJobOutput,
    StateEnum
)
from .rabbitmq_utils import RMQPublisher, OcrdProcessingMessage
from .server_utils import (
    _get_processor_job,
    validate_and_resolve_mets_path,
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
        if data.agent_type not in ['worker', 'server']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown network agent with value: {data.agent_type}"
            )
        job_output = None
        if data.agent_type == 'worker':
            job_output = await self.push_to_processing_queue(processor_name, data)
        if data.agent_type == 'server':
            job_output = await self.push_to_processor_server(processor_name, data)
        if not job_output:
            self.log.exception('Failed to create job output')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to create job output'
            )
        return job_output

    # TODO: Revisit and remove duplications between push_to_* methods
    async def push_to_processing_queue(self, processor_name: str, job_input: PYJobInput) -> PYJobOutput:
        ocrd_tool = await self.get_processor_info(processor_name)
        validate_job_input(self.log, processor_name, ocrd_tool, job_input)
        job_input = await validate_and_resolve_mets_path(self.log, job_input, resolve=False)
        if not self.rmq_publisher:
            raise Exception('RMQPublisher is not connected')
        deployed_processors = self.deployer.find_matching_processors(
            worker_only=True,
            str_names_only=True,
            unique_only=True
        )
        if processor_name not in deployed_processors:
            self.check_if_queue_exists(processor_name)

        job = DBProcessorJob(
            **job_input.dict(exclude_unset=True, exclude_none=True),
            job_id=generate_id(),
            processor_name=processor_name,
            state=StateEnum.queued
        )
        await job.insert()
        processing_message = self.create_processing_message(job)
        encoded_processing_message = OcrdProcessingMessage.encode_yml(processing_message)
        try:
            self.rmq_publisher.publish_to_queue(processor_name, encoded_processing_message)
        except Exception as error:
            self.log.exception(f'RMQPublisher has failed: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'RMQPublisher has failed: {error}'
            )
        return job.to_job_output()

    async def push_to_processor_server(self, processor_name: str, job_input: PYJobInput) -> PYJobOutput:
        ocrd_tool, processor_server_url = self.query_ocrd_tool_json_from_server(processor_name)
        validate_job_input(self.log, processor_name, ocrd_tool, job_input)
        job_input = await validate_and_resolve_mets_path(self.log, job_input, resolve=False)
        try:
            json_data = json.dumps(job_input.dict(exclude_unset=True, exclude_none=True))
        except Exception as e:
            self.log.exception(f"Failed to json dump the PYJobInput, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to json dump the PYJobInput, error: {e}"
            )
        
        # TODO: The amount of pages should come as a request input
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
