from datetime import datetime
from os import getpid
from shutil import which
from typing import Any
from uvicorn import run as uvicorn_run
from fastapi import APIRouter, FastAPI, HTTPException, status

from ocrd import OcrdResourceManager
from ocrd_utils import getLogger, get_ocrd_tool_json, initLogging
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
        executable: Any = "ocrd-dummy",
        dynamic: bool = True,
        name: Any = None,
        database: Any = None,
        url: Any = None
    ):
        if executable == '*':
            message = f"'*' is not an acceptable executable name! Try with a specific executable."
            self.log.error(message)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
        result = self.resmgr_instance.list_available(executable, dynamic, name, database, url)
        json_message = {
            "result": result
        }
        return json_message

    async def list_installed_resources(self, executable: Any = None):
        if executable == '*':
            message = f"'*' is not an acceptable executable name! Try with a specific executable."
            self.log.error(message)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
        result = self.resmgr_instance.list_available(executable)
        json_message = {
            "result": result
        }
        return json_message

    async def download_resource(
        self,
        executable: str = "ocrd-dummy",
        name: Any = None,
        location: Any = None,
        any_url: str = '',
        no_dynamic: bool = False,
        resource_type: str = 'file',
        path_in_archive: str = '.',
        allow_uninstalled: bool = True,
        overwrite: bool = True
    ):
        resmgr = OcrdResourceManager()
        response = []
        if executable == '*':
            message = f"'*' is not an acceptable executable name! Try with a specific executable."
            self.log.error(message)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
        if name == '*':
            name = None
        if executable and not which(executable):
            if not allow_uninstalled:
                message = (f"Executable '{executable}' is not installed. To download resources anyway, "
                           f"use the -a/--allow-uninstalled flag")
                self.log.error(message)
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
            else:
                message = f"Executable '{executable}' is not installed, but downloading resources anyway."
                self.log.info(message)
                response.append(message)
        reslist = resmgr.list_available(executable=executable, dynamic=not no_dynamic, name=name)
        if not any(r[1] for r in reslist):
            message = f"No resources {name} found in registry for executable {executable}"
            self.log.info(message)
            response.append(message)
            if executable and name:
                reslist = [(executable, [{
                    'url': any_url or '???',
                    'name': name,
                    'type': resource_type,
                    'path_in_archive': path_in_archive}]
                )]
        for this_executable, this_reslist in reslist:
            resource_locations = get_ocrd_tool_json(this_executable)['resource_locations']
            if not location:
                location = resource_locations[0]
            elif location not in resource_locations:
                response.append(
                    f"The selected --location {location} is not in the {this_executable}'s resource search path, "
                    f"refusing to install to invalid location. Instead installing to: {resource_locations[0]}")
            res_dest_dir = resmgr.build_resource_dest_dir(location=location, executable=this_executable)
            for res_dict in this_reslist:
                try:
                    fpath = resmgr.handle_resource(
                        res_dict=res_dict,
                        executable=this_executable,
                        dest_dir=res_dest_dir,
                        any_url=any_url,
                        overwrite=overwrite,
                        resource_type=resource_type,
                        path_in_archive=path_in_archive
                    )
                    if not fpath:
                        continue
                except FileExistsError as exc:
                    response.append(str(exc))
                usage = res_dict.get('parameter_usage', 'as-is')
                response.append(f"Use in parameters as '{resmgr.parameter_usage(res_dict['name'], usage)}'")
        json_message = { "result": response }
        return json_message
