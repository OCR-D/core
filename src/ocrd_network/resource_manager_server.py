from datetime import datetime
from os import getpid
from uvicorn import run as uvicorn_run
from fastapi import APIRouter, FastAPI, status
from ocrd_utils import initLogging, getLogger
from .logging_utils import configure_file_handler_with_formatter, get_resource_manager_server_logging_file_path


class ResourceManagerServer(FastAPI):
    def __init__(self, host: str, port: int) -> None:
        self.title = f"OCR-D Resource Manager Server"
        super().__init__(
            title=self.title,
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            description=self.title
        )
        initLogging()
        self.log = getLogger("ocrd_network.resource_manager_server")
        log_file = get_resource_manager_server_logging_file_path(pid=getpid())
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        self.hostname = host
        self.port = port

        self.add_api_routes()

        base_router = APIRouter()
        base_router.add_api_route(
            path="/",
            endpoint=self.home_page,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary="Get information about the processing server"
        )

    def start(self):
        uvicorn_run(self, host=self.hostname, port=int(self.port))

    async def on_startup(self):
        self.log.info(f"Starting {self.title}")
        pass

    async def on_shutdown(self) -> None:
        pass

    def add_api_routes(self):
        base_router = APIRouter()
        base_router.add_api_route(
            path="/",
            endpoint=self.home_page,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary="Get information about the OCR-D Resource Manager Server"
        )
        self.include_router(base_router)

    async def home_page(self):
        message = f"The home page of the {self.title}"
        json_message = {
            "message": message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return json_message
