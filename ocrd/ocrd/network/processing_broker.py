from fastapi import FastAPI
import uvicorn
from yaml import safe_load

from ocrd_utils import getLogger
from ocrd_validators import ProcessingBrokerValidator

from ocrd.network.deployer import Deployer
from ocrd.network.deployment_config import ProcessingBrokerConfig
from ocrd.network.rabbitmq_utils import RMQPublisher


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

        # RabbitMQ related fields, hard coded initially
        self.rmq_host = "localhost"
        self.rmq_port = 5672
        self.rmq_vhost = "/"

        # These could also be made configurable,
        # not relevant for the current state
        self.rmq_username = "default-publisher"
        self.rmq_password = "default-publisher"

        self.rmq_publisher = self.connect_publisher()
        self.rmq_publisher.enable_delivery_confirmations()  # Enable acks

        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_deployed_agents,
            methods=['POST'],
            # tags=['TODO: add a tag'],
            # summary='TODO: summary for apidesc',
            # TODO: add response model? add a response body at all?
        )

        # TODO: Call this after the rest of the API is implemented
        # Example of publishing a message inside a specific queue
        # The message type is bytes
        # self.rmq_publisher.publish_to_queue(queue_name="queue_name", message="message")

    def start(self) -> None:
        """
        start processing broker with uvicorn
        """
        self.log.debug(f'starting uvicorn. Host: {self.host}. Port: {self.port}')
        uvicorn.run(self, host=self.hostname, port=self.port)

    @staticmethod
    def parse_config(config_path: str) -> ProcessingBrokerConfig:
        with open(config_path) as fin:
            obj = safe_load(fin)
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

    def connect_publisher(self) -> RMQPublisher:
        rmq_publisher = RMQPublisher(host=self.rmq_host, port=self.rmq_port, vhost=self.rmq_vhost)
        rmq_publisher.authenticate_and_connect(username=self.rmq_username, password=self.rmq_password)
        return rmq_publisher
