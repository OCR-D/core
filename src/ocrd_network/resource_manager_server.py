from os import getpid
from fastapi import FastAPI
from ocrd_utils import initLogging, getLogger
from .logging_utils import configure_file_handler_with_formatter, get_resource_manager_server_logging_file_path


class ResourceManagerServer(FastAPI):
    def __init__(self, host: str, port: int, processor_name: str) -> None:
        self.processor_name = processor_name
        self.title = f"OCR-D Resource Manager Server of type: {self.processor_name}"
        super().__init__(
            title=self.title,
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            description=self.title
        )
        initLogging()
        self.log = getLogger("ocrd_network.resource_manager_server")
        log_file = get_resource_manager_server_logging_file_path(processor_name=self.processor_name, pid=getpid())
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        self.hostname = host
        self.port = port

    async def on_startup(self):
        self.log.info(f"Starting {self.title}")
        pass

    async def on_shutdown(self) -> None:
        pass
