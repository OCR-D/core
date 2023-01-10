import uvicorn
from fastapi import FastAPI
from ocrd.network.deployer import Deployer
from ocrd_utils import getLogger
import yaml
from jsonschema import validate, ValidationError
from ocrd_utils.package_resources import resource_string
from typing import Union
from ocrd_validators import ProcessingBrokerValidator
from ocrd.network.deployment_config import ProcessingBrokerConfig


class ProcessingBroker(FastAPI):
    """
    TODO: doc for ProcessingBroker and its methods
    """

    def __init__(self, config_path: str, host: str, port: int) -> None:
        # TODO: set other args: title, description, version, openapi_tags
        super().__init__(on_shutdown=[self.on_shutdown])
        self.hostname = host
        self.port = port
        self.config = ProcessingBroker.parse_config(config_path)
        self.deployer = Deployer(self.config)
        # Deploy everything specified in the configuration
        self.deployer.deploy_all()
        self.log = getLogger(__name__)

        # RMQPublisher object must be created here, reference: RabbitMQ Library (WebAPI Implementation)
        # Based on the API calls the ProcessingBroker will send messages to the running instance
        # of the RabbitMQ Server (deployed by the Deployer object) through the RMQPublisher object.
        self.rmq_publisher = self.configure_publisher(self.config)

        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_deployed_agents,
            methods=['POST'],
            # tags=['TODO: add a tag'],
            # summary='TODO: summary for apidesc',
            # TODO: add response model? add a response body at all?
        )
        # TODO:
        # Publish messages based on the API calls
        # Here is a call example to be adopted later
        #
        # # The message type is bytes
        # # Call this method to publish a message
        # self.rmq_publisher.publish_to_queue(queue_name='queue_name', message='message')

    def start(self) -> None:
        """
        start processing broker with uvicorn
        """
        self.log.debug(f'starting uvicorn. Host: {self.host}. Port: {self.port}')
        uvicorn.run(self, host=self.hostname, port=self.port)

    @staticmethod
    def parse_config(config_path: str) -> ProcessingBrokerConfig:
        with open(config_path) as fin:
            obj = yaml.safe_load(fin)
        report = ProcessingBrokerValidator.validate(obj)
        if not report.is_valid:
            raise Exception(f"Processing-Broker configuration file is invalid:\n{report.errors}")
        return ProcessingBrokerConfig(obj)

    async def on_shutdown(self) -> None:
        # TODO: shutdown docker containers
        """
        - hosts and pids should be stored somewhere
        - ensure queue is empty or processor is not currently running
        - connect to hosts and kill pids
        """
        # TODO: remove the try/except before beta. This is only needed for development. All
        # exceptions this function (on_shutdown) throws are ignored / not printed, when it is used
        # as shutdown-hook as it is now. So this try/except and logging is neccessary to make them
        # visible when testing
        try:
            await self.stop_deployed_agents()
        except:
            self.log.debug('error stopping processing servers: ', exc_info=True)
            raise

    async def stop_deployed_agents(self) -> None:
        self.deployer.kill_all()

    # TODO: add correct typehint if RMQPublisher is available here in core
    @staticmethod
    def configure_publisher(config_file: ProcessingBrokerConfig) -> 'RMQPublisher':
        rmq_publisher = 'RMQPublisher Object'
        # TODO:
        # Here is a template implementation to be adopted later
        #
        # rmq_publisher = RMQPublisher(host='localhost', port=5672, vhost='/')
        # # The credentials are configured inside definitions.json
        # # when building the RabbitMQ docker image
        # rmq_publisher.authenticate_and_connect(
        #     username='default-publisher',
        #     password='default-publisher'
        # )
        # rmq_publisher.enable_delivery_confirmations()
        return rmq_publisher
