"""
# METS server functionality
"""
import re
from os import environ, _exit
from io import BytesIO
from typing import Any, Dict, Optional, Union, List, Tuple

from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import JSONResponse
from requests import request, Session as requests_session
from requests_unixsocket import Session as requests_unixsocket_session
from pydantic import BaseModel, Field, ValidationError

import uvicorn

from ocrd_models import OcrdMets, OcrdFile, OcrdAgent
from ocrd_utils import initLogging, getLogger, deprecated_alias

#
# XXX HACKS TODO
#
initLogging()

#
# Models
#

class OcrdFileModel(BaseModel):
    file_grp : str = Field()
    file_id : str = Field()
    mimetype : str = Field()
    page_id : Union[str, None] = Field()
    local_filename : str = Field()

    @staticmethod
    def create(file_grp : str, file_id : str, page_id : Union[str, None], local_filename : str, mimetype : str):
        return OcrdFileModel(file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, local_filename=local_filename)

class OcrdAgentModel(BaseModel):
    name : str = Field()
    _type : str = Field()
    role : str = Field()
    otherrole : Optional[str] = Field()
    othertype : str = Field()
    notes : Optional[List[Tuple[Dict[str, str], Optional[str]]]] = Field()

    @staticmethod
    def create(name : str, _type : str, role : str, otherrole : str, othertype : str, notes : List[Tuple[Dict[str, str], Optional[str]]]):
        return OcrdAgentModel(name=name, _type=_type, role=role, otherrole=otherrole, othertype=othertype, notes=notes)


class OcrdFileListModel(BaseModel):
    files : List[OcrdFileModel] = Field()

    @staticmethod
    def create(files : List[OcrdFile]):
        return OcrdFileListModel(
            files=[OcrdFileModel.create(file_grp=f.fileGrp, file_id=f.ID, mimetype=f.mimetype, page_id=f.pageId, local_filename=f.local_filename) for f in files]
        )

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
            agents=[OcrdAgentModel(name=a.name, _type=a.type, role=a.role, otherrole=a.otherrole, othertype=a.othertype, notes=a.notes) for a in agents]
        )

#
# Client
#

class ClientSideOcrdFile:
    """
    Provides the same interface as :py:class:`ocrd_models.ocrd_file.OcrdFile`
    but without attachment to :py:class:`ocrd_models.ocrd_mets.OcrdMets` since
    this represents the response of the :py:class:`ocrd.mets_server.OcrdMetsServer`.
    """

    def __init__(self, el, mimetype=None, pageId=None, loctype='OTHER', local_filename=None, mets=None, url=None, ID=None, fileGrp=None):
        """
        Args:
            el (): ignored
        Keyword Args:
            mets (): ignored
            mimetype (string): ``@MIMETYPE`` of this ``mets:file``
            pageId (string): ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file``
            loctype (string): ``@LOCTYPE`` of this ``mets:file``
            local_filename (): ``@xlink:href`` of this ``mets:file`` - XXX the local file once we have proper mets:FLocat bookkeeping
            ID (string): ``@ID`` of this ``mets:file``
        """
        self.ID = ID
        self.mimetype = mimetype
        self.local_filename = local_filename
        self.loctype = loctype
        self.pageId = pageId
        self.fileGrp = fileGrp

class ClientSideOcrdAgent():
    """
    Provides the same interface as :py:class:`ocrd_models.ocrd_file.OcrdAgent`
    but without attachment to :py:class:`ocrd_models.ocrd_mets.OcrdMets` since
    this represents the response of the :py:class:`ocrd.mets_server.OcrdMetsServer`.
    """

    def __init__(self, el, name=None, _type=None, othertype=None, role=None, otherrole=None,
                 notes=None):
        """
        Args:
            el (): ignored
        Keyword Args:
            name (string):
            _type (string):
            othertype (string):
            role (string):
            otherrole (string):
            notes (dict):
        """
        self.name = name
        self.type = _type
        self.othertype = othertype
        self.role = role
        self.otherrole = otherrole
        self.notes = notes

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

    def __init__(self, host, port, socket):
        self.log = getLogger('ocrd.mets_client.%s' % ('uds' if socket else 'tcp'))
        if socket:
            self.url = f'http+unix://{socket.replace("/", "%2F")}'
            self.session = requests_unixsocket_session()
        else:
            self.url = f'http://{host}:{port}'
            self.session = requests_session()

    @deprecated_alias(ID="file_id")
    @deprecated_alias(pageId="page_id")
    @deprecated_alias(fileGrp="file_grp")
    def find_files(self, **kwargs):
        if 'pageId' in kwargs:
            kwargs['page_id'] = kwargs.pop('pageId')
        if 'ID' in kwargs:
            kwargs['file_id'] = kwargs.pop('ID')
        if 'fileGrp' in kwargs:
            kwargs['file_grp'] = kwargs.pop('fileGrp')
        r = self.session.request('GET', f'{self.url}/file', params={**kwargs})
        for f in r.json()['files']:
            yield ClientSideOcrdFile(None, ID=f['file_id'], pageId=f['page_id'], fileGrp=f['file_grp'], local_filename=f['local_filename'], mimetype=f['mimetype'])

    def find_all_files(self, *args, **kwargs):
        return list(self.find_files(*args, **kwargs))

    def add_agent(self, *args, **kwargs):
        return self.session.request('POST', f'{self.url}/agent', json=OcrdAgentModel.create(**kwargs).dict())

    @property
    def agents(self):
        return [ClientSideOcrdAgent(None, **agent_dict) for agent_dict in self.session.request('GET', f'{self.url}/agent').json()['agents']]

    @property
    def file_groups(self):
        return self.session.request('GET', f'{self.url}/file_groups').json()['file_groups']

    @deprecated_alias(pageId="page_id")
    @deprecated_alias(ID="file_id")
    def add_file(self, file_grp, content=None, file_id=None, local_filename=None, mimetype=None, page_id=None, **kwargs):
        return self.session.request(
            'POST',
            f'{self.url}/file',
            data=OcrdFileModel.create(
                file_id=file_id,
                file_grp=file_grp,
                page_id=page_id,
                mimetype=mimetype,
                local_filename=local_filename).dict(),
        )

    def save(self):
        self.session.request('PUT', self.url)

    def stop(self):
        self.session.request('DELETE', self.url)

#
# Server
#

class OcrdMetsServer():

    def __init__(self, workspace, host, port, socket):
        self.workspace = workspace
        if socket and host:
            raise ValueError("Expecting either socket or host/port")
        if not socket and not(host and port):
            raise ValueError("Expecting both host and port")
        self.host = host
        self.port = port
        self.socket = socket
        self.log = getLogger('ocrd.workspace_client')

    def shutdown(self):
        _exit(0)

    def startup(self):

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
            file_grp : Union[str, None] = None,
            file_id : Union[str, None] = None,
            page_id : Union[str, None] = None,
            mimetype : Union[str, None] = None,
        ):
            """
            Find files in the mets
            """
            found = workspace.mets.find_all_files(fileGrp=file_grp, ID=file_id, pageId=page_id, mimetype=mimetype)
            return OcrdFileListModel.create(found)

        @app.put('/')
        def save():
            return workspace.save_mets()

        @app.post('/file', response_model=OcrdFileModel)
        async def add_file(
            file_grp : str = Form(),
            file_id : str = Form(),
            page_id : Union[str, None] = Form(),
            mimetype : str = Form(),
            local_filename : str = Form(),
        ):
            """
            Add a file
            """
            # Validate
            file_resource = OcrdFileModel.create(file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, local_filename=local_filename)
            # Add to workspace
            kwargs = file_resource.dict()
            kwargs['page_id'] = page_id
            workspace.add_file(**kwargs)
            return file_resource

        @app.get('/file_groups', response_model=OcrdFileGroupListModel)
        async def file_groups():
            return {'file_groups': workspace.mets.file_groups}

        @app.post('/agent', response_model=OcrdAgentModel)
        async def add_agent(agent : OcrdAgentModel):
            kwargs = agent.dict()
            workspace.mets.add_agent(**kwargs)
            return agent

        @app.get('/agent', response_model=OcrdAgentListModel)
        async def agents():
            return OcrdAgentListModel.create(workspace.mets.agents)

        @app.delete('/')
        async def stop():
            """
            Stop the server
            """
            getLogger('ocrd_models.ocrd_mets').info('Shutting down')
            workspace.save_mets()
            # os._exit because uvicorn catches SystemExit raised by sys.exit
            _exit(0)

        uvicorn.run(app, host=self.host, port=self.port, uds=self.socket)
