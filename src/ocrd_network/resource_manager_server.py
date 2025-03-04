from datetime import datetime
from os import getpid
from pathlib import Path
import requests
from shutil import which
from typing import Any
from uvicorn import run as uvicorn_run
from fastapi import APIRouter, FastAPI, HTTPException, status

from ocrd import OcrdResourceManager
from ocrd_utils import directory_size, getLogger, get_moduledir, get_ocrd_tool_json, initLogging
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

    async def download_resource(
        self,
        executable: str,
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
        if executable != '*' and not name:
            message = f"Unless EXECUTABLE ('{executable}') is the '*' wildcard, NAME is required"
            self.log.error(message)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
        elif executable == '*':
            executable = None
        if name == '*':
            name = None
        is_url = (any_url.startswith('https://') or any_url.startswith('http://')) if any_url else False
        is_filename = Path(any_url).exists() if any_url else False
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
            for resdict in this_reslist:
                if 'size' in resdict:
                    registered = "registered"
                else:
                    registered = "unregistered"
                if any_url:
                    resdict['url'] = any_url
                if resdict['url'] == '???':
                    message = f"Cannot download user resource {resdict['name']}"
                    self.log.info(message)
                    response.append(message)
                    continue
                if resdict['url'].startswith('https://') or resdict['url'].startswith('http://'):
                    message = f"Downloading {registered} resource '{resdict['name']}' ({resdict['url']})"
                    self.log.info(message)
                    response.append(message)
                    if 'size' not in resdict:
                        with requests.head(resdict['url']) as r:
                            resdict['size'] = int(r.headers.get('content-length', 0))
                else:
                    message = f"Copying {registered} resource '{resdict['name']}' ({resdict['url']})"
                    self.log.info(message)
                    response.append(message)
                    urlpath = Path(resdict['url'])
                    resdict['url'] = str(urlpath.resolve())
                    if Path(urlpath).is_dir():
                        resdict['size'] = directory_size(urlpath)
                    else:
                        resdict['size'] = urlpath.stat().st_size
                if not location:
                    location = get_ocrd_tool_json(this_executable)['resource_locations'][0]
                elif location not in get_ocrd_tool_json(this_executable)['resource_locations']:
                    message = (f"The selected --location {location} is not in the {this_executable}'s resource search "
                               f"path, refusing to install to invalid location")
                    self.log.error(message)
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
                if location != 'module':
                    basedir = resmgr.location_to_resource_dir(location)
                else:
                    basedir = get_moduledir(this_executable)
                    if not basedir:
                        basedir = resmgr.location_to_resource_dir('data')
                try:
                    fpath = resmgr.download(
                        this_executable,
                        resdict['url'],
                        basedir,
                        name=resdict['name'],
                        resource_type=resdict.get('type', resource_type),
                        path_in_archive=resdict.get('path_in_archive', path_in_archive),
                        overwrite=overwrite,
                        no_subdir=location in ['cwd', 'module'],
                        progress_cb=None
                    )
                    if registered == 'unregistered':
                        message = (f"{this_executable} resource '{name}' ({any_url}) not a known resource, "
                                   f"creating stub in {resmgr.user_list}'")
                        self.log.info(message)
                        response.append(message)
                        resmgr.add_to_user_database(this_executable, fpath, url=any_url)
                    resmgr.save_user_list()
                    message = f"Installed resource {resdict['url']} under {fpath}"
                    self.log.info(message)
                    response.append(message)
                except FileExistsError as exc:
                    response.append(str(exc))
                parameter_usage = resmgr.parameter_usage(
                    resdict['name'], usage=resdict.get('parameter_usage', 'as-is'))
                message = f"Use in parameters as '{parameter_usage}'"
                self.log.info(message)
                response.append(message)
        json_message = {
            "result": response
        }
        return json_message
