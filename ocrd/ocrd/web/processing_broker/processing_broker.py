import uvicorn
from fastapi import FastAPI
from .deployment import Deployer
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

        self.router.add_api_route(
            path='/stop',
            endpoint=self.stop_processing_servers,
            methods=['POST'],
            # tags=['TODO: add a tag'],
            # summary='TODO: summary for apidesc',
            # TODO: add response model? add a response body at all?
        )

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
