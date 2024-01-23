"""
# METS server functionality
"""
import re
from os import environ, _exit, chmod
from io import BytesIO
from typing import Any, Dict, Optional, Union, List, Tuple
from pathlib import Path
from urllib.parse import urlparse
import socket

from fastapi import FastAPI, Request, File, Form, Response
from fastapi.responses import JSONResponse
from requests import request, Session as requests_session
from requests.exceptions import ConnectionError
from requests_unixsocket import Session as requests_unixsocket_session
from pydantic import BaseModel, Field, ValidationError

import uvicorn

from ocrd_models import OcrdMets, OcrdFile, ClientSideOcrdFile, OcrdAgent, ClientSideOcrdAgent
from ocrd_utils import initLogging, getLogger, deprecated_alias

#
# Models
#

class OcrdFileModel(BaseModel):
    file_grp : str = Field()
    file_id : str = Field()
    mimetype : str = Field()
    page_id : Optional[str] = Field()
    url : Optional[str] = Field()
    local_filename : Optional[str] = Field()

    @staticmethod
    def create(file_grp : str, file_id : str, page_id : Optional[str], url : Optional[str], local_filename : Optional[Union[str, Path]], mimetype : str):
        return OcrdFileModel(file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, url=url, local_filename=str(local_filename))

class OcrdAgentModel(BaseModel):
    name : str = Field()
    type : str = Field()
    role : str = Field()
    otherrole : Optional[str] = Field()
    othertype : str = Field()
    notes : Optional[List[Tuple[Dict[str, str], Optional[str]]]] = Field()

    @staticmethod
    def create(name : str, _type : str, role : str, otherrole : str, othertype : str, notes : List[Tuple[Dict[str, str], Optional[str]]]):
        return OcrdAgentModel(name=name, type=_type, role=role, otherrole=otherrole, othertype=othertype, notes=notes)


class OcrdFileListModel(BaseModel):
    files : List[OcrdFileModel] = Field()

    @staticmethod
    def create(files : List[OcrdFile]):
        ret = OcrdFileListModel(
            files=[OcrdFileModel.create(
                file_grp=f.fileGrp,
                file_id=f.ID,
                mimetype=f.mimetype,
                page_id=f.pageId,
                url=f.url,
                local_filename=f.local_filename
            ) for f in files])
        return ret

class OcrdFileGroupListModel(BaseModel):
    file_groups : List[str] = Field()

    @staticmethod
    def create(file_groups : List[str]):
        return OcrdFileGroupListModel(file_groups=file_groups)

class OcrdAgentListModel(BaseModel):
    agents : List[OcrdAgentModel] = Field()

    @staticmethod
    def create(agents : List[OcrdAgent]):
        return OcrdAgentListModel(
            agents=[OcrdAgentModel.create(name=a.name, _type=a.type, role=a.role, otherrole=a.otherrole, othertype=a.othertype, notes=a.notes) for a in agents]
        )

#
# Client
#


class ClientSideOcrdMets():
    """
    Partial substitute for :py:class:`ocrd_models.ocrd_mets.OcrdMets` which provides for
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.find_files`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.find_all_files`, and
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.add_agent`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.agents`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.add_file` to query via HTTP a
    :py:class:`ocrd.mets_server.OcrdMetsServer`.
    """

    def __init__(self, url):
        protocol = 'tcp' if url.startswith('http://') else 'uds'
        self.log = getLogger(f'ocrd.mets_client[{url}]')
        self.url = url if protocol == 'tcp' else f'http+unix://{url.replace("/", "%2F")}'
        self.session = requests_session() if protocol == 'tcp' else requests_unixsocket_session()

    def __getattr__(self, name):
        raise NotImplementedError(f"ClientSideOcrdMets has no access to '{name}' - try without METS server")

    def __str__(self):
        return f'<ClientSideOcrdMets[url={self.url}]>'

    @property
    def workspace_path(self):
        return self.session.request('GET', f'{self.url}/workspace_path').text

    def reload(self):
        return self.session.request('POST', f'{self.url}/reload').text

    @deprecated_alias(ID="file_id")
    @deprecated_alias(pageId="page_id")
    @deprecated_alias(fileGrp="file_grp")
    def find_files(self, **kwargs):
        self.log.debug('find_files(%s)', kwargs)
        if 'pageId' in kwargs:
            kwargs['page_id'] = kwargs.pop('pageId')
        if 'ID' in kwargs:
            kwargs['file_id'] = kwargs.pop('ID')
        if 'fileGrp' in kwargs:
            kwargs['file_grp'] = kwargs.pop('fileGrp')
        r = self.session.request('GET', f'{self.url}/file', params={**kwargs})
        for f in r.json()['files']:
            yield ClientSideOcrdFile(None, ID=f['file_id'], pageId=f['page_id'], fileGrp=f['file_grp'], url=f['url'], local_filename=f['local_filename'], mimetype=f['mimetype'])

    def find_all_files(self, *args, **kwargs):
        return list(self.find_files(*args, **kwargs))

    def add_agent(self, *args, **kwargs):
        return self.session.request('POST', f'{self.url}/agent', json=OcrdAgentModel.create(**kwargs).dict())

    @property
    def agents(self):
        agent_dicts = self.session.request('GET', f'{self.url}/agent').json()['agents']
        for agent_dict in agent_dicts:
            agent_dict['_type'] = agent_dict.pop('type')
        return [ClientSideOcrdAgent(None, **agent_dict) for agent_dict in agent_dicts]

    @property
    def unique_identifier(self):
        return self.session.request('GET', f'{self.url}/unique_identifier').text

    @property
    def file_groups(self):
        return self.session.request('GET', f'{self.url}/file_groups').json()['file_groups']

    @deprecated_alias(pageId="page_id")
    @deprecated_alias(ID="file_id")
    def add_file(self, file_grp, content=None, file_id=None, url=None, local_filename=None, mimetype=None, page_id=None, **kwargs):
        data = OcrdFileModel.create(
            file_id=file_id,
            file_grp=file_grp,
            page_id=page_id,
            mimetype=mimetype,
            url=url,
            local_filename=local_filename)
        r = self.session.request('POST', f'{self.url}/file', data=data.dict())
        return ClientSideOcrdFile(
                None,
                ID=file_id,
                fileGrp=file_grp,
                url=url,
                pageId=page_id,
                mimetype=mimetype,
                local_filename=local_filename)


    def save(self):
        self.session.request('PUT', self.url)

    def stop(self):
        try:
            self.session.request('DELETE', self.url)
        except ConnectionError:
            # Expected because we exit the process without returning
            pass

#
# Server
#

class OcrdMetsServer():

    def __init__(self, workspace, url):
        self.workspace = workspace
        self.url = url
        self.is_uds = not (url.startswith('http://') or url.startswith('https://'))
        self.log = getLogger(f'ocrd.mets_server[{self.url}]')

    def shutdown(self):
        self.log.info("Shutting down METS server")
        if self.is_uds:
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

        @app.get("/file", response_model=OcrdFileListModel)
        async def find_files(
            file_grp : Optional[str] = None,
            file_id : Optional[str] = None,
            page_id : Optional[str] = None,
            mimetype : Optional[str] = None,
            local_filename : Optional[str] = None,
            url : Optional[str] = None,
        ):
            """
            Find files in the mets
            """
            found = workspace.mets.find_all_files(fileGrp=file_grp, ID=file_id, pageId=page_id, mimetype=mimetype, local_filename=local_filename, url=url)
            return OcrdFileListModel.create(found)

        @app.put('/')
        def save():
            return workspace.save_mets()

        @app.post('/file', response_model=OcrdFileModel)
        async def add_file(
            file_grp : str = Form(),
            file_id : str = Form(),
            page_id : Optional[str] = Form(),
            mimetype : str = Form(),
            url : Optional[str] = Form(None),
            local_filename : Optional[str] = Form(None),
        ):
            """
            Add a file
            """
            # Validate
            file_resource = OcrdFileModel.create(file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, url=url, local_filename=local_filename)
            # Add to workspace
            kwargs = file_resource.dict()
            workspace.add_file(**kwargs)
            return file_resource

        @app.get('/file_groups', response_model=OcrdFileGroupListModel)
        async def file_groups():
            return {'file_groups': workspace.mets.file_groups}

        @app.post('/agent', response_model=OcrdAgentModel)
        async def add_agent(agent : OcrdAgentModel):
            kwargs = agent.dict()
            kwargs['_type'] = kwargs.pop('type')
            workspace.mets.add_agent(**kwargs)
            return agent

        @app.get('/agent', response_model=OcrdAgentListModel)
        async def agents():
            return OcrdAgentListModel.create(workspace.mets.agents)

        @app.get('/unique_identifier', response_model=str)
        async def unique_identifier():
            return Response(content=workspace.mets.unique_identifier, media_type='text/plain')

        @app.get('/workspace_path', response_model=str)
        async def workspace_path():
            return Response(content=workspace.directory, media_type="text/plain")

        @app.post('/reload')
        async def workspace_reload_mets():
            workspace.reload_mets()
            return Response(content=f'Reloaded from {workspace.directory}', media_type="text/plain")

        @app.delete('/')
        async def stop():
            """
            Stop the server
            """
            getLogger('ocrd.models.ocrd_mets').info('Shutting down')
            workspace.save_mets()
            self.shutdown()

        # ------------- #

        if self.is_uds:
            # Create socket and change to world-readable and -writable to avoid
            # permsission errors
            self.log.debug(f"chmod 0o677 {self.url}")
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(self.url)  # creates the socket file
            server.close()
            chmod(self.url, 0o666)
            uvicorn_kwargs = {'uds': self.url}
        else:
            parsed = urlparse(self.url)
            uvicorn_kwargs = {'host': parsed.hostname, 'port': parsed.port}

        self.log.debug("Starting uvicorn")
        uvicorn.run(app, **uvicorn_kwargs)
