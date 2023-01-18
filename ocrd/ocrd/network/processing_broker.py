from fastapi import FastAPI
import uvicorn
from time import sleep
from yaml import safe_load
from typing import List

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
        self.log = getLogger(__name__)

        self.hostname = host
        self.port = port
        # TODO: Ideally the parse_config should return a Tuple with the 3 configs assigned below
        #  to prevent passing the entire parsed config around to methods.
        parsed_config = ProcessingBroker.parse_config(config_path)
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
        self.rmq_host = "localhost"
        self.rmq_port = 5672
        self.rmq_vhost = "/"

        # Gets assigned when `connect_publisher` is called on the working object
        # Note for peer: Check under self.start()
        self.rmq_publisher = None

        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_deployed_agents,
            methods=['POST'],
            # tags=['TODO: add a tag'],
            # summary='TODO: summary for api desc',
            # TODO: add response model? add a response body at all?
        )

        # TODO: Call this after the rest of the API is implemented
        # Example of publishing a message inside a specific queue
        # The message type is bytes
        # self.rmq_publisher.publish_to_queue(queue_name="queue_name", message="message")

    def start(self) -> None:
        """
        deploy things and start the processing broker (aka server) with uvicorn
        """
        """
        Note for a peer:
        Deploying everything together at once is a bad approach. First the RabbitMQ Server and the MongoDB 
        should be deployed. Then the RMQPublisher of the Processing Broker (aka Processing Server) should 
        connect to the running RabbitMQ server. After that point the Processing Workers should be deployed.
        The RMQPublisher should be connected before deploying Processing Workers because the message queues to 
        which the Processing Workers listen to are created based on the deployed processor.
        """
        # Deploy everything specified in the configuration
        # self.deployer.deploy_all()

        # Deploy the RabbitMQ Server, get the URL of the deployed agent
        rabbitmq_url = self.deployer.deploy_rabbitmq()

        # Deploy the MongoDB, get the URL of the deployed agent
        mongodb_url = self.deployer.deploy_mongodb()

        # Give enough time for the RabbitMQ server to get deployed and get fully configured
        # Needed to prevent connection of the publisher before the RabbitMQ is deployed
        sleep(3)  # TODO: Sleeping here is bad and better check should be performed

        # The RMQPublisher is initialized and a connection to the RabbitMQ is performed
        self.connect_publisher()

        self.log.debug(f"Starting to create message queues on RabbitMQ instance url: {rabbitmq_url}")
        self.create_message_queues()

        # Deploy processing hosts where processing workers are running on
        # Note: A deployed processing worker starts listening to a message queue with id processor.name
        self.deployer.deploy_hosts(self.hosts_config, rabbitmq_url, mongodb_url)

        self.log.debug(f'Starting uvicorn: {self.host}:{self.port}')
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
        # TODO: This except block is trapping the user if nothing is following after the keyword.
        #  Is that the expected behaviour here?
        except:
            self.log.debug('error stopping processing servers: ', exc_info=True)
            raise

    async def stop_deployed_agents(self) -> None:
        self.deployer.kill_all()

    def connect_publisher(self, username="default-publisher", password="default-publisher", enable_acks=True):
        self.log.debug(f"Connecting RMQPublisher to RabbitMQ server: {self.rmq_host}:{self.rmq_port}{self.rmq_vhost}")
        self.rmq_publisher = RMQPublisher(host=self.rmq_host, port=self.rmq_port, vhost=self.rmq_vhost)
        # TODO: Remove this information before the release
        self.log.debug(f"RMQPublisher authenticates with username: {username}, password: {password}")
        self.rmq_publisher.authenticate_and_connect(username=username, password=password)
        if enable_acks:
            self.rmq_publisher.enable_delivery_confirmations()
            self.log.debug(f"Delivery confirmations are enabled")
        else:
            self.log.debug(f"Delivery confirmations are disabled")
        self.log.debug(f"Successfully connected RMQPublisher.")

    def create_message_queues(self):
        # Create the message queues based on the occurrence of `processor.name` in the config file
        for host in self.hosts_config:
            for processor in host.processors:
                # The existence/validity of the processor.name is not tested.
                # Even if an ocr-d processor does not exist, the queue is created
                self.log.debug(f"Creating a message queue with id: {processor.name}")
                # TODO: We may want to track here if there are already queues with the same name
                self.rmq_publisher.create_queue(queue_name=processor.name)
