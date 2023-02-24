import json
from typing import Dict
import uvicorn
from yaml import safe_load

from beanie import PydanticObjectId
from fastapi import FastAPI, status, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ocrd_utils import (
    getLogger,
    get_ocrd_tool_json,
)
from ocrd_validators import (
    ParameterValidator,
    ProcessingServerValidator
)
from ocrd_network.database import initiate_database
from ocrd_network.deployer import Deployer
from ocrd_network.deployment_config import ProcessingServerConfig
from ocrd_network.rabbitmq_utils import (
    RMQPublisher,
    OcrdProcessingMessage
)
from ocrd_network.models.job import (
    Job,
    JobInput,
    JobOutput,
    StateEnum
)
from ocrd_network.models.workspace import Workspace


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
                         title="OCR-D Processing Server",
                         description="OCR-D processing and processors")
        self.log = getLogger(__name__)
        self.hostname = host
        self.port = port
        self.config = ProcessingServer.parse_config(config_path)
        self.deployer = Deployer(self.config)
        self.mongodb_url = None
        self.rmq_host = self.config.queue.address
        self.rmq_port = self.config.queue.port
        self.rmq_vhost = '/'
        self.rmq_username = self.config.queue.credentials[0]
        self.rmq_password = self.config.queue.credentials[1]

        # Gets assigned when `connect_publisher` is called on the working object
        self.rmq_publisher = None

        # This list holds all processors mentioned in the config file
        self._processor_list = None

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
            response_model=JobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/processor/{_processor_name}/{job_id}',
            endpoint=self.get_job,
            methods=['GET'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about a job based on its ID',
            response_model=JobOutput,
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
            self.log.error(f"{request}: {exc_str}")
            content = {'status_code': 10422, 'message': exc_str, 'data': None}
            return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def start(self) -> None:
        """ deploy agents (db, queue, workers) and start the processing server with uvicorn
        """
        try:
            rabbitmq_hostinfo = self.deployer.deploy_rabbitmq()
            # Assign the credentials to the rabbitmq url parameter
            rabbitmq_url = f'{self.rmq_username}:{self.rmq_password}@{rabbitmq_hostinfo}'

            self.mongodb_url = self.deployer.deploy_mongodb()

            # The RMQPublisher is initialized and a connection to the RabbitMQ is performed
            self.connect_publisher()

            self.log.debug(f'Creating message queues on RabbitMQ instance url: {rabbitmq_url}')
            self.create_message_queues()

            # Deploy processing hosts where processing workers are running on
            # Note: A deployed processing worker starts listening to a message queue with id
            #       processor.name
            self.deployer.deploy_hosts(rabbitmq_url, self.mongodb_url)
        except Exception:
            self.log.error('Error during startup of processing server. '
                           'Trying to kill parts of incompletely deployed service')
            self.deployer.kill_all()
            raise
        uvicorn.run(self, host=self.hostname, port=self.port)

    @staticmethod
    def parse_config(config_path: str) -> ProcessingServerConfig:
        with open(config_path) as fin:
            obj = safe_load(fin)
        report = ProcessingServerValidator.validate(obj)
        if not report.is_valid:
            raise Exception(f'Processing-Server configuration file is invalid:\n{report.errors}')
        return ProcessingServerConfig(obj)

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
        """Create the message queues based on the occurrence of `processor.name` in the config file
        """
        for host in self.config.hosts:
            for processor in host.processors:
                # The existence/validity of the processor.name is not tested.
                # Even if an ocr-d processor does not exist, the queue is created
                self.log.info(f'Creating a message queue with id: {processor.name}')
                self.rmq_publisher.create_queue(queue_name=processor.name)

    @property
    def processor_list(self):
        if self._processor_list:
            return self._processor_list
        res = set([])
        for host in self.config.hosts:
            for processor in host.processors:
                res.add(processor.name)
        self._processor_list = list(res)
        return self._processor_list

    async def push_processor_job(self, processor_name: str, data: JobInput) -> JobOutput:
        """ Queue a processor job
        """
        if processor_name not in self.processor_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Processor not available'
            )

        # validate additional parameters
        if data.parameters:
            ocrd_tool = get_ocrd_tool_json(processor_name)
            if not ocrd_tool:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(f'Processor \'{processor_name}\' not available. It\'s ocrd_tool is '
                            'empty or missing')
                )
            validator = ParameterValidator(ocrd_tool)
            report = validator.validate(data.parameters)
            if not report.is_valid:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=report.errors)

        # determine path to mets if workspace_id is provided
        if bool(data.path) == bool(data.workspace_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Either \'path\' or \'workspace_id\' must be set'
            )
        elif data.workspace_id:
            workspace = await Workspace.get(data.workspace_id)
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f'Workspace for id \'{data.workspace_id}\' not existing'
                )
            data.path = workspace.workspace_mets_path

        job = Job(**data.dict(exclude_unset=True, exclude_none=True), processor_name=processor_name,
                  state=StateEnum.queued)
        await job.insert()
        processing_message = OcrdProcessingMessage.from_job(job)
        encoded_processing_message = OcrdProcessingMessage.encode_yml(processing_message)
        if self.rmq_publisher:
            self.rmq_publisher.publish_to_queue(processor_name, encoded_processing_message)
        else:
            raise Exception('RMQPublisher is not connected')
        return job.to_job_output()

    async def get_processor_info(self, processor_name) -> Dict:
        """ Return a processor's ocrd-tool.json
        """
        if processor_name not in self.processor_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Processor not available'
            )
        return get_ocrd_tool_json(processor_name)

    async def get_job(self, _processor_name: str, job_id: PydanticObjectId) -> JobOutput:
        """ Return job-information from the database
        """
        job = await Job.get(job_id)
        if job:
            return job.to_job_output()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Job not found.'
        )

    async def list_processors(self) -> str:
        """ Return a list of all available processors
        """
        return json.dumps(self.processor_list)
