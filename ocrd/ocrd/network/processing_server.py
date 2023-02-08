from fastapi import FastAPI, status, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from yaml import safe_load
from typing import Dict, Set

from ocrd_utils import (
    getLogger,
    get_ocrd_tool_json,
)
from ocrd_validators import ProcessingServerValidator

from ocrd.network.deployer import Deployer
from ocrd.network.deployment_config import ProcessingServerConfig
from ocrd.network.rabbitmq_utils import RMQPublisher, OcrdProcessingMessage
from ocrd.network.helpers import construct_dummy_processing_message
from ocrd.network.models.job import Job, JobInput, StateEnum
from ocrd_validators import ParameterValidator
from ocrd.network.database import initiate_database
from beanie import PydanticObjectId
from time import sleep
import json


# TODO: rename to ProcessingServer (module-file too)
class ProcessingServer(FastAPI):
    """
    TODO: doc for ProcessingServer and its methods
    """

    def __init__(self, config_path: str, host: str, port: int) -> None:
        # TODO: set other args: title, description, version, openapi_tags
        super().__init__(on_startup=[self.on_startup], on_shutdown=[self.on_shutdown])
        self.log = getLogger(__name__)

        self.hostname = host
        self.port = port
        # TODO: Ideally the parse_config should return a Tuple with the 3 configs assigned below
        #  to prevent passing the entire parsed config around to methods.
        parsed_config = ProcessingServer.parse_config(config_path)
        self.queue_config = parsed_config.queue_config
        self.mongo_config = parsed_config.mongo_config
        self.hosts_config = parsed_config.hosts_config
        self.deployer = Deployer(
            queue_config=self.queue_config,
            mongo_config=self.mongo_config,
            hosts_config=self.hosts_config
        )

        # TODO: Parse the RabbitMQ related data from the `queue_config`
        #  above instead of using the hard coded ones below

        # RabbitMQ related fields, hard coded initially
        self.rmq_host = 'localhost'
        self.rmq_port = 5672
        self.rmq_vhost = '/'

        # Gets assigned when `connect_publisher` is called on the working object
        # Note for peer: Check under self.start()
        self.rmq_publisher = None

        self._processor_list = None

        # Create routes
        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_deployed_agents,
            methods=['POST'],
            # tags=['TODO: add a tag'],
            # summary='TODO: summary for api desc',
            # TODO: add response model? add a response body at all?
        )

        self.router.add_api_route(
            path='/test-dummy',
            endpoint=self.publish_default_processing_message,
            methods=['POST'],
            status_code=status.HTTP_202_ACCEPTED
        )

        self.router.add_api_route(
            path='/processor/{processor_name}',
            endpoint=self.run_processor,
            methods=['POST'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Submit a job to this processor',
            response_model=Job,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/processor/{processor_name}/{job_id}',
            endpoint=self.get_job,
            methods=['GET'],
            tags=['processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about a job based on its ID',
            response_model=Job,
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
        """
        deploy things and start the processing server with uvicorn
        """
        """
        Note for a peer:
        Deploying everything together at once is a bad approach. First the RabbitMQ Server and the MongoDB
        should be deployed. Then the RMQPublisher of the Processing Server (aka Processing Server) should
        connect to the running RabbitMQ server. After that point the Processing Workers should be deployed.
        The RMQPublisher should be connected before deploying Processing Workers because the message queues to
        which the Processing Workers listen to are created based on the deployed processor.
        """
        # Deploy everything specified in the configuration
        # self.deployer.deploy_all()

        # Deploy the RabbitMQ Server, get the URL of the deployed agent
        rabbitmq_url = self.deployer.deploy_rabbitmq()

        # Deploy the MongoDB, get the URL of the deployed agent
        self.mongodb_url = self.deployer.deploy_mongodb()

        # Give enough time for the RabbitMQ server to get deployed and get fully configured
        # Needed to prevent connection of the publisher before the RabbitMQ is deployed
        sleep(3)  # TODO: Sleeping here is bad and better check should be performed

        # The RMQPublisher is initialized and a connection to the RabbitMQ is performed
        self.connect_publisher()

        self.log.debug(f'Starting to create message queues on RabbitMQ instance url: {rabbitmq_url}')
        self.create_message_queues()

        # Deploy processing hosts where processing workers are running on
        # Note: A deployed processing worker starts listening to a message queue with id processor.name
        self.deployer.deploy_hosts(self.hosts_config, rabbitmq_url, self.mongodb_url)

        self.log.debug(f'Starting uvicorn: {self.hostname}:{self.port}')
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

    def connect_publisher(self, username: str = 'default-publisher',
                          password: str = 'default-publisher', enable_acks: bool =True) -> None:
        self.log.debug(f'Connecting RMQPublisher to RabbitMQ server: {self.rmq_host}:{self.rmq_port}{self.rmq_vhost}')
        self.rmq_publisher = RMQPublisher(host=self.rmq_host, port=self.rmq_port, vhost=self.rmq_vhost)
        # TODO: Remove this information before the release
        self.log.debug(f'RMQPublisher authenticates with username: {username}, password: {password}')
        self.rmq_publisher.authenticate_and_connect(username=username, password=password)
        if enable_acks:
            self.rmq_publisher.enable_delivery_confirmations()
            self.log.debug('Delivery confirmations are enabled')
        else:
            self.log.debug('Delivery confirmations are disabled')
        self.log.debug('Successfully connected RMQPublisher.')

    def create_message_queues(self) -> None:
        """Create the message queues based on the occurrence of `processor.name` in the config file
        """
        for host in self.hosts_config:
            for processor in host.processors:
                # The existence/validity of the processor.name is not tested.
                # Even if an ocr-d processor does not exist, the queue is created
                self.log.debug(f'Creating a message queue with id: {processor.name}')
                # TODO: We may want to track here if there are already queues with the same name
                self.rmq_publisher.create_queue(queue_name=processor.name)

    def publish_default_processing_message(self) -> None:
        processing_message = construct_dummy_processing_message()
        queue_name = processing_message.processor_name
        # TODO: switch back to pickle?!
        encoded_processing_message = OcrdProcessingMessage.encode_yml(processing_message)
        if self.rmq_publisher:
            self.log.debug('Publishing the default processing message')
            self.rmq_publisher.publish_to_queue(queue_name=queue_name,
                                                message=encoded_processing_message)
        else:
            self.log.error('RMQPublisher is not connected')
            raise Exception('RMQPublisher is not connected')

    @property
    def processor_list(self):
        if self._processor_list:
            return self._processor_list
        res = set([])
        for host in self.hosts_config:
            for processor in host.processors:
                res.add(processor.name)
        self._processor_list = list(res)
        return self._processor_list

    # TODO: how do we want to do the whole model-stuff? Webapi (openapi.yml) uses ProcessorJob
    async def run_processor(self, processor_name: str, data: JobInput) -> Job:
        self.log.debug('processing_server.run_processor() called')
        if processor_name not in self.processor_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Processor not available'
            )
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

        job = Job(**data.dict(exclude_unset=True, exclude_none=True), processor_name=processor_name,
                  state=StateEnum.queued)
        await job.insert()
        processing_message = OcrdProcessingMessage.from_job(job)
        encoded_processing_message = OcrdProcessingMessage.encode_yml(processing_message)
        if self.rmq_publisher:
            self.rmq_publisher.publish_to_queue(processor_name, encoded_processing_message)
        else:
            raise Exception('RMQPublisher is not connected')
        return job

    async def get_processor_info(self, processor_name) -> Dict:
        self.log.debug('processing_server.get_processor_info() called')
        if processor_name not in self.processor_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Processor not available'
            )
        return get_ocrd_tool_json(processor_name)

    async def get_job(self, processor_name: str, job_id: PydanticObjectId) -> Job:
        self.log.debug('processing_server.get_job() called')
        job = await Job.get(job_id)
        if job:
            return job
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Job not found.'
        )

    async def list_processors(self) -> str:
        self.log.debug('processing_server.list_processors() called')
        return json.dumps(self.processor_list)
