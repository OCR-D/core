"""
# METS server functionality
"""
import re
from os import _exit, chmod
from typing import Dict, Optional, Union, List, Tuple
from time import sleep
from pathlib import Path
from subprocess import Popen, run as subprocess_run
from urllib.parse import urlparse
import socket
import atexit

from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import JSONResponse
from requests import Session as requests_session
from requests.exceptions import ConnectionError
from requests_unixsocket import Session as requests_unixsocket_session
from pydantic import BaseModel, Field, ValidationError

import uvicorn

from ocrd_models import OcrdFile, ClientSideOcrdFile, OcrdAgent, ClientSideOcrdAgent
from ocrd_utils import getLogger, deprecated_alias


#
# Models
#


class OcrdFileModel(BaseModel):
    file_grp: str = Field()
    file_id: str = Field()
    mimetype: str = Field()
    page_id: Optional[str] = Field()
    url: Optional[str] = Field()
    local_filename: Optional[str] = Field()

    @staticmethod
    def create(
        file_grp: str, file_id: str, page_id: Optional[str], url: Optional[str],
        local_filename: Optional[Union[str, Path]], mimetype: str
    ):
        return OcrdFileModel(
            file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, url=url,
            local_filename=str(local_filename)
        )


class OcrdAgentModel(BaseModel):
    name: str = Field()
    type: str = Field()
    role: str = Field()
    otherrole: Optional[str] = Field()
    othertype: str = Field()
    notes: Optional[List[Tuple[Dict[str, str], Optional[str]]]] = Field()

    @staticmethod
    def create(
        name: str, _type: str, role: str, otherrole: str, othertype: str,
        notes: List[Tuple[Dict[str, str], Optional[str]]]
    ):
        return OcrdAgentModel(name=name, type=_type, role=role, otherrole=otherrole, othertype=othertype, notes=notes)


class OcrdFileListModel(BaseModel):
    files: List[OcrdFileModel] = Field()

    @staticmethod
    def create(files: List[OcrdFile]):
        ret = OcrdFileListModel(
            files=[
                OcrdFileModel.create(
                    file_grp=f.fileGrp, file_id=f.ID, mimetype=f.mimetype, page_id=f.pageId, url=f.url,
                    local_filename=f.local_filename
                ) for f in files
            ]
        )
        return ret


class OcrdFileGroupListModel(BaseModel):
    file_groups: List[str] = Field()

    @staticmethod
    def create(file_groups: List[str]):
        return OcrdFileGroupListModel(file_groups=file_groups)


class OcrdAgentListModel(BaseModel):
    agents: List[OcrdAgentModel] = Field()

    @staticmethod
    def create(agents: List[OcrdAgent]):
        return OcrdAgentListModel(
            agents=[
                OcrdAgentModel.create(
                    name=a.name, _type=a.type, role=a.role, otherrole=a.otherrole, othertype=a.othertype, notes=a.notes
                ) for a in agents
            ]
        )


#
# Client
#


class ClientSideOcrdMets:
    """
    Partial substitute for :py:class:`ocrd_models.ocrd_mets.OcrdMets` which provides for
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.find_files`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.find_all_files`, and
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.add_agent`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.agents`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.add_file` to query via HTTP a
    :py:class:`ocrd.mets_server.OcrdMetsServer`.
    """

    def __init__(self, url, workspace_path: Optional[str] = None):
        self.protocol = "tcp" if url.startswith("http://") else "uds"
        self.log = getLogger(f"ocrd.mets_client[{url}]")
        self.url = url if self.protocol == "tcp" else f'http+unix://{url.replace("/", "%2F")}'
        self.ws_dir_path = workspace_path if workspace_path else None

        if self.protocol == "tcp" and "tcp_mets" in self.url:
            self.multiplexing_mode = True
            if not self.ws_dir_path:
                # Must be set since this path is the way to multiplex among multiple workspaces on the PS side
                raise ValueError("ClientSideOcrdMets runs in multiplexing mode but the workspace dir path is not set!")
        else:
            self.multiplexing_mode = False

    @property
    def session(self) -> Union[requests_session, requests_unixsocket_session]:
        return requests_session() if self.protocol == "tcp" else requests_unixsocket_session()

    def __getattr__(self, name):
        raise NotImplementedError(f"ClientSideOcrdMets has no access to '{name}' - try without METS server")

    def __str__(self):
        return f"<ClientSideOcrdMets[url={self.url}]>"

    def save(self):
        """
        Request writing the changes to the file system
        """
        if not self.multiplexing_mode:
            self.session.request("PUT", url=self.url)
        else:
            self.session.request(
                "POST",
                self.url,
                json=MpxReq.save(self.ws_dir_path)
            )

    def stop(self):
        """
        Request stopping the mets server
        """
        try:
            if not self.multiplexing_mode:
                self.session.request("DELETE", self.url)
                return
            else:
                self.session.request(
                    "POST",
                    self.url,
                    json=MpxReq.stop(self.ws_dir_path)
                )
        except ConnectionError:
            # Expected because we exit the process without returning
            pass

    def reload(self):
        """
        Request reloading of the mets file from the file system
        """
        if not self.multiplexing_mode:
            return self.session.request("POST", f"{self.url}/reload").text
        else:
            return self.session.request(
                "POST",
                self.url,
                json=MpxReq.reload(self.ws_dir_path)
            ).json()["text"]

    @property
    def unique_identifier(self):
        if not self.multiplexing_mode:
            return self.session.request("GET", f"{self.url}/unique_identifier").text
        else:
            return self.session.request(
                "POST",
                self.url,
                json=MpxReq.unique_identifier(self.ws_dir_path)
            ).json()["text"]

    @property
    def workspace_path(self):
        if not self.multiplexing_mode:
            self.ws_dir_path = self.session.request("GET", f"{self.url}/workspace_path").text
            return self.ws_dir_path
        else:
            self.ws_dir_path = self.session.request(
                "POST",
                self.url,
                json=MpxReq.workspace_path(self.ws_dir_path)
            ).json()["text"]
            return self.ws_dir_path

    @property
    def file_groups(self):
        if not self.multiplexing_mode:
            return self.session.request("GET", f"{self.url}/file_groups").json()["file_groups"]
        else:
            return self.session.request(
                "POST",
                self.url,
                json=MpxReq.file_groups(self.ws_dir_path)
            ).json()["file_groups"]

    @property
    def agents(self):
        if not self.multiplexing_mode:
            agent_dicts = self.session.request("GET", f"{self.url}/agent").json()["agents"]
        else:
            agent_dicts = self.session.request(
                "POST",
                self.url,
                json=MpxReq.agents(self.ws_dir_path)
            ).json()["agents"]

        for agent_dict in agent_dicts:
            agent_dict["_type"] = agent_dict.pop("type")
        return [ClientSideOcrdAgent(None, **agent_dict) for agent_dict in agent_dicts]

    def add_agent(self, *args, **kwargs):
        if not self.multiplexing_mode:
            return self.session.request("POST", f"{self.url}/agent", json=OcrdAgentModel.create(**kwargs).dict())
        else:
            self.session.request(
                "POST",
                self.url,
                json=MpxReq.add_agent(self.ws_dir_path, OcrdAgentModel.create(**kwargs).dict())
            ).json()
            return OcrdAgentModel.create(**kwargs)

    @deprecated_alias(ID="file_id")
    @deprecated_alias(pageId="page_id")
    @deprecated_alias(fileGrp="file_grp")
    def find_files(self, **kwargs):
        self.log.debug("find_files(%s)", kwargs)
        if "pageId" in kwargs:
            kwargs["page_id"] = kwargs.pop("pageId")
        if "ID" in kwargs:
            kwargs["file_id"] = kwargs.pop("ID")
        if "fileGrp" in kwargs:
            kwargs["file_grp"] = kwargs.pop("fileGrp")

        if not self.multiplexing_mode:
            r = self.session.request(method="GET", url=f"{self.url}/file", params={**kwargs})
        else:
            r = self.session.request(
                "POST",
                self.url,
                json=MpxReq.find_files(self.ws_dir_path, {**kwargs})
            )

        for f in r.json()["files"]:
            yield ClientSideOcrdFile(
                None, ID=f["file_id"], pageId=f["page_id"], fileGrp=f["file_grp"], url=f["url"],
                local_filename=f["local_filename"], mimetype=f["mimetype"]
            )

    def find_all_files(self, *args, **kwargs):
        return list(self.find_files(*args, **kwargs))

    @deprecated_alias(pageId="page_id")
    @deprecated_alias(ID="file_id")
    def add_file(
        self, file_grp, content=None, file_id=None, url=None, local_filename=None, mimetype=None, page_id=None, **kwargs
    ):
        data = OcrdFileModel.create(
            file_id=file_id, file_grp=file_grp, page_id=page_id, mimetype=mimetype, url=url,
            local_filename=local_filename
        )

        if not self.multiplexing_mode:
            r = self.session.request("POST", f"{self.url}/file", data=data.dict())
            if not r:
                raise RuntimeError("Add file failed. Please check provided parameters")
        else:
            r = self.session.request("POST", self.url, json=MpxReq.add_file(self.ws_dir_path, data.dict()))
            if "error" in r:
                raise RuntimeError(f"Add file failed: Msg: {r['error']}")

        return ClientSideOcrdFile(
            None, ID=file_id, fileGrp=file_grp, url=url, pageId=page_id, mimetype=mimetype,
            local_filename=local_filename
        )


class MpxReq:
    """This class wrapps the request bodies needed for the tcp forwarding

    For every mets-server-call like find_files or workspace_path a special request_body is
    needed to call `MetsServerProxy.forward_tcp_request`. These are created by this functions.

    Reason to put this to a separate class is to allow easier testing
    """

    @staticmethod
    def __args_wrapper(
        workspace_path: str, method_type: str, response_type: str, request_url: str, request_data: dict
    ) -> Dict:
        return {
            "workspace_path": workspace_path,
            "method_type": method_type,
            "response_type": response_type,
            "request_url": request_url,
            "request_data": request_data
        }

    @staticmethod
    def save(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="PUT", response_type="empty", request_url="", request_data={})

    @staticmethod
    def stop(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="DELETE", response_type="empty", request_url="", request_data={})

    @staticmethod
    def reload(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="POST", response_type="text", request_url="reload", request_data={})

    @staticmethod
    def unique_identifier(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="GET", response_type="text", request_url="unique_identifier", request_data={})

    @staticmethod
    def workspace_path(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="GET", response_type="text", request_url="workspace_path", request_data={})

    @staticmethod
    def file_groups(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="GET", response_type="dict", request_url="file_groups", request_data={})

    @staticmethod
    def agents(ws_dir_path: str) -> Dict:
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="GET", response_type="class", request_url="agent", request_data={})

    @staticmethod
    def add_agent(ws_dir_path: str, agent_model: Dict) -> Dict:
        request_data = {"class": agent_model}
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="POST", response_type="class", request_url="agent", request_data=request_data)

    @staticmethod
    def find_files(ws_dir_path: str, params: Dict) -> Dict:
        request_data = {"params": params}
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="GET", response_type="class", request_url="file", request_data=request_data)

    @staticmethod
    def add_file(ws_dir_path: str, data: Dict) -> Dict:
        request_data = {"form": data}
        return MpxReq.__args_wrapper(
            ws_dir_path, method_type="POST", response_type="class", request_url="file", request_data=request_data)

#
# Server
#


class OcrdMetsServer:
    def __init__(self, workspace, url):
        self.workspace = workspace
        self.url = url
        self.is_uds = not (url.startswith('http://') or url.startswith('https://'))
        self.log = getLogger(f'ocrd.models.ocrd_mets.server.{self.url}')

    @staticmethod
    def create_process(mets_server_url: str, ws_dir_path: str, log_file: str) -> int:
        sub_process = Popen(
            args=["ocrd", "workspace", "-U", f"{mets_server_url}", "-d", f"{ws_dir_path}", "server", "start"],
            stdout=open(file=log_file, mode="w"), stderr=open(file=log_file, mode="a"), cwd=ws_dir_path,
            shell=False, universal_newlines=True, start_new_session=True
        )
        # Wait for the mets server to start
        sleep(2)
        if sub_process.poll():
            raise RuntimeError(f"Mets server starting failed. See {log_file} for errors")
        return sub_process.pid

    @staticmethod
    def kill_process(mets_server_pid: int):
        subprocess_run(args=["kill", "-s", "SIGINT", f"{mets_server_pid}"], shell=False, universal_newlines=True)
        return

    def shutdown(self):
        if self.is_uds:
            if Path(self.url).exists():
                self.log.debug(f'UDS socket {self.url} still exists, removing it')
                Path(self.url).unlink()
        # os._exit because uvicorn catches SystemExit raised by sys.exit
        _exit(0)

    def startup(self):
        self.log.info("Starting up METS server")

        workspace = self.workspace

        app = FastAPI(
            title="OCR-D METS Server",
            description="Providing simultaneous write-access to mets.xml for OCR-D",
        )

        @app.exception_handler(ValidationError)
        async def exception_handler_validation_error(request: Request, exc: ValidationError):
            return JSONResponse(status_code=400, content=exc.errors())

        @app.exception_handler(FileExistsError)
        async def exception_handler_file_exists(request: Request, exc: FileExistsError):
            return JSONResponse(status_code=400, content=str(exc))

        @app.exception_handler(re.error)
        async def exception_handler_invalid_regex(request: Request, exc: re.error):
            return JSONResponse(status_code=400, content=f'invalid regex: {exc}')

        @app.put(path='/')
        def save():
            """
            Write current changes to the file system
            """
            return workspace.save_mets()

        @app.delete(path='/')
        async def stop():
            """
            Stop the mets server
            """
            getLogger('ocrd.models.ocrd_mets').info(f'Shutting down METS Server {self.url}')
            workspace.save_mets()
            self.shutdown()

        @app.post(path='/reload')
        async def workspace_reload_mets():
            """
            Reload mets file from the file system
            """
            workspace.reload_mets()
            return Response(content=f'Reloaded from {workspace.directory}', media_type="text/plain")

        @app.get(path='/unique_identifier', response_model=str)
        async def unique_identifier():
            return Response(content=workspace.mets.unique_identifier, media_type='text/plain')

        @app.get(path='/workspace_path', response_model=str)
        async def workspace_path():
            return Response(content=workspace.directory, media_type="text/plain")

        @app.get(path='/file_groups', response_model=OcrdFileGroupListModel)
        async def file_groups():
            return {'file_groups': workspace.mets.file_groups}

        @app.get(path='/agent', response_model=OcrdAgentListModel)
        async def agents():
            return OcrdAgentListModel.create(workspace.mets.agents)

        @app.post(path='/agent', response_model=OcrdAgentModel)
        async def add_agent(agent: OcrdAgentModel):
            kwargs = agent.dict()
            kwargs['_type'] = kwargs.pop('type')
            workspace.mets.add_agent(**kwargs)
            return agent

        @app.get(path="/file", response_model=OcrdFileListModel)
        async def find_files(
            file_grp: Optional[str] = None,
            file_id: Optional[str] = None,
            page_id: Optional[str] = None,
            mimetype: Optional[str] = None,
            local_filename: Optional[str] = None,
            url: Optional[str] = None
        ):
            """
            Find files in the mets
            """
            found = workspace.mets.find_all_files(
                fileGrp=file_grp, ID=file_id, pageId=page_id, mimetype=mimetype, local_filename=local_filename, url=url
            )
            return OcrdFileListModel.create(found)

        @app.post(path='/file', response_model=OcrdFileModel)
        async def add_file(
            file_grp: str = Form(),
            file_id: str = Form(),
            page_id: Optional[str] = Form(),
            mimetype: str = Form(),
            url: Optional[str] = Form(None),
            local_filename: Optional[str] = Form(None)
        ):
            """
            Add a file
            """
            # Validate
            file_resource = OcrdFileModel.create(
                file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, url=url,
                local_filename=local_filename
            )
            # Add to workspace
            kwargs = file_resource.dict()
            workspace.add_file(**kwargs)
            return file_resource

        # ------------- #

        if self.is_uds:
            # Create socket and change to world-readable and -writable to avoid permission errors
            self.log.debug(f"chmod 0o677 {self.url}")
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if Path(self.url).exists() and not is_socket_in_use(self.url):
                # remove leftover unused socket which blocks startup
                Path(self.url).unlink()
            server.bind(self.url)  # creates the socket file
            atexit.register(self.shutdown)
            server.close()
            chmod(self.url, 0o666)
            uvicorn_kwargs = {'uds': self.url}
        else:
            parsed = urlparse(self.url)
            uvicorn_kwargs = {'host': parsed.hostname, 'port': parsed.port}
        uvicorn_kwargs['log_config'] = None
        uvicorn_kwargs['access_log'] = False

        self.log.debug("Starting uvicorn")
        uvicorn.run(app, **uvicorn_kwargs)


def is_socket_in_use(socket_path):
    if Path(socket_path).exists():
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(socket_path)
        except OSError:
            return False
        client.close()
        return True
