import uvicorn
from fastapi import FastAPI
from .deployment import (
    Deployer,
    Config
)
from ocrd_utils import (
    getLogger
)


class ProcessingBroker(FastAPI):
    """
    TODO: doc for ProcessingBroker and its methods
    """

    def __init__(self, config_path):
        # TODO: set other args: title, description, version, openapi_tags
        super().__init__(on_shutdown=[self.on_shutdown])
        # TODO: validate: shema can be used to validate the content of the yaml file. decide if to
        # validate here or in Config-Constructor
        self.config = Config(config_path)
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


    async def on_shutdown(self):
        # TODO: shutdown docker containers
        """
        - hosts and pids should be stored somewhere
        - ensure queue is empty or processor is not currently running
        - connect to hosts and kill pids
        """
        await self.stop_processing_servers()

    async def stop_processing_servers(self):
        self.deployer.kill()
