from datetime import datetime
from os import getpid
from typing import Any
from uvicorn import run as uvicorn_run
from fastapi import APIRouter, FastAPI, status

from ocrd import OcrdResourceManager
from ocrd.cli.resmgr import resmgr_cli
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

        self.resmgr_instance = OcrdResourceManager()

        self.hostname = host
        self.port = port

        self.add_api_routes()

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
        base_router.add_api_route(
            path="/list_available",
            endpoint=self.list_available_resources,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary=""
        )
        base_router.add_api_route(
            path="/list_installed",
            endpoint=self.list_installed_resources,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary=""
        )
        base_router.add_api_route(
            path="/download",
            endpoint=self.download_resource,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            summary=""
        )
        self.include_router(base_router)

    async def home_page(self):
        message = f"The home page of the {self.title}"
        json_message = {
            "message": message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return json_message

    async def list_available_resources(
        self,
        executable: Any = None,
        dynamic: bool = True,
        name: Any = None,
        database: Any = None,
        url: Any = None
    ):
        result = self.resmgr_instance.list_available(executable, dynamic, name, database, url)
        json_message = {
            "result": result
        }
        return json_message

    async def list_installed_resources(self, executable: Any = None):
        result = self.resmgr_instance.list_available(executable)
        json_message = {
            "result": result
        }
        return json_message

    @staticmethod
    async def download_resource(
        any_url,
        no_dynamic,
        resource_type,
        path_in_archive,
        allow_uninstalled,
        overwrite,
        location,
        executable,
        name
    ):
        resmgr_cli.download(
            any_url=any_url,
            no_dynamic=no_dynamic,
            resource_type=resource_type,
            path_in_archive=path_in_archive,
            allow_uninstalled=allow_uninstalled,
            overwrite=overwrite,
            location=location,
            executable=executable,
            name=name
        )
        json_message = {
            "result": "Success"
        }
        return json_message
