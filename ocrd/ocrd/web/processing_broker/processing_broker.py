import uvicorn
from fastapi import FastAPI
from .deployer import Deployer
from ocrd_utils import getLogger
import yaml
from jsonschema import validate, ValidationError
from ocrd_utils.package_resources import resource_string


class ProcessingBroker(FastAPI):
    """
    TODO: doc for ProcessingBroker and its methods
    """

    def __init__(self, config_path):
        # TODO: set other args: title, description, version, openapi_tags
        super().__init__(on_shutdown=[self.on_shutdown])
        with open(config_path) as fin:
            self.config = yaml.safe_load(fin)
        self.deployer = Deployer(self.config)
        self.deployer.deploy()
        self.log = getLogger("ocrd.processingbroker")

        # RMQPublisher object must be created here, reference: RabbitMQ Library (WebAPI Implementation)
        # Based on the API calls the ProcessingBroker will send messages to the running instance
        # of the RabbitMQ Server (deployed by the Deployer object) through the RMQPublisher object.
        self.rmq_publisher = self.configure_publisher(self.config)

        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_processing_servers,
            methods=['POST'],
            # tags=['TODO: add a tag'],
            # summary='TODO: summary for apidesc',
            # TODO: add response model? add a response body at all?
        )

        """
        Publish messages based on the API calls
        Here is a call example to be adopted later
        
        # The message type is bytes
        # Call this method to publish a message
        self.rmq_publisher.publish_to_queue(queue_name="queue_name", message="message")
        """

    def start(self):
        """
        start processing broker with uvicorn
        """
        assert self.config, "config was not parsed correctly"
        # TODO: change where to run the processing server: default params, read from config or read
        #       from cmd? Or do not run at all as fastapi?
        # TODO: activate next line again (commented just for testing)
        port = 5050
        host = 'localhost'
        self.log.debug(f"starting uvicorn. Host: {host}. Port: {port}")
        uvicorn.run(self, host=host, port=port)

    @staticmethod
    def validate_config(config_path):
        with open(config_path) as fin:
            obj = yaml.safe_load(fin)
        # TODO: move schema to another place?!
        schema = yaml.safe_load(resource_string(__name__, 'config.schema.yml'))
        try:
            validate(obj, schema)
        except ValidationError as e:
            return f"{e.message}. At {e.json_path}"
        return None

    async def on_shutdown(self):
        # TODO: shutdown docker containers
        """
        - hosts and pids should be stored somewhere
        - ensure queue is empty or processor is not currently running
        - connect to hosts and kill pids
        """
        try:
            await self.stop_processing_servers()
        except:
            self.log.debug("error stopping processing servers: ", exc_info=True)
            raise

    async def stop_processing_servers(self):
        self.deployer.kill()

    @staticmethod
    def configure_publisher(config_file):
        rmq_publisher = "RMQPublisher Object"
        """
        Here is a template implementation to be adopted later
        
        rmq_publisher = RMQPublisher(host="localhost", port=5672, vhost="/")
        # The credentials are configured inside definitions.json
        # when building the RabbitMQ docker image
        rmq_publisher.authenticate_and_connect(
            username="default-publisher",
            password="default-publisher"
        )
        rmq_publisher.enable_delivery_confirmations()
        """
        return rmq_publisher
