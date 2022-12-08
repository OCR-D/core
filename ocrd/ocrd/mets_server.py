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
from pydantic import BaseModel, Field, constr, ValidationError

import uvicorn

from ocrd_models import OcrdMets
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
    url : str = Field()

class OcrdAgentModel(BaseModel):
    name : str = Field()
    _type : str = Field()
    role : str = Field()
    otherrole : str = Field()
    othertype : str = Field()
    notes : List[Tuple[Dict[str, str], Optional[str]]] = Field()

class OcrdFileListModel(BaseModel):
    files : List[OcrdFileModel] = Field()

class OcrdFileGroupListModel(BaseModel):
    file_groups : List[str] = Field()

#
# Client
#

class ClientSideOcrdFile:
    """
    Provides the same interface as :py:class:`ocrd_models.ocrd_file.OcrdFile`
    but without attachment to :py:class:`ocrd_models.ocrd_mets.OcrdMets` since
    this represents the response of the :py:class:`ocrd.mets_server.OcrdWorkspaceServer`.
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
            local_filename (): ignored
            url (string): ``@xlink:href`` of this ``mets:file``
            ID (string): ``@ID`` of this ``mets:file``
        """
        self.ID = ID
        self.mimetype = mimetype
        self.url = url
        self.loctype = loctype
        self.pageId = pageId
        self.fileGrp = fileGrp

class ClientSideOcrdMets():
    """
    Replacement for :py:class:`ocrd_models.ocrd_mets.OcrdMets` with overrides for
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.find_files`,
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.find_all_files`, and
    :py:meth:`ocrd_models.ocrd_mets.OcrdMets.add_file` to query via HTTP a
    :py:class:`ocrd.mets_server.OcrdMetsServer`.
    """

    def __init__(self, host, port, socket):
        self.log = getLogger('ocrd.workspace_client')
        if socket:
            self.url = f'http+unix://{socket.replace("/", "%2F")}'
            self.session = requests_unixsocket_session()
        else:
            self.url = f'http://{host}:{port}'
            self.session = requests_session()

    def find_files(self, **kwargs):
        r = self.session.request('GET', self.url, params={**kwargs})
        for f in r.json()['files']:
            yield ClientSideOcrdFile(None, ID=f['file_id'], pageId=f['page_id'], fileGrp=f['file_grp'], url=f['url'], mimetype=f['mimetype'])

    def find_all_files(self, *args, **kwargs):
        return list(self.find_files(*args, **kwargs))

    def add_agent(self, *args, **kwargs):
        return self.session.request('POST', f'{self.url}/agent', data=OcrdAgentModel(**kwargs))

    @property
    def file_groups():
        return self.session.request('GET', f'{self.url}/file_groups').json()['file_groups']

    @deprecated_alias(pageId="page_id")
    @deprecated_alias(ID="file_id")
    def add_file(self, file_grp, content=None, file_id=None, url=None, mimetype=None, page_id=None, **kwargs):
        r = self.session.request(
            'POST',
            self.url,
            data=OcrdFileModel(
                file_id=file_id,
                file_grp=file_grp,
                page_id=page_id,
                mimetype=mimetype,
                url=url).dict(),
            files={'data': content}
        )

    def save(self):
        self.session.request('PUT', self.url)


#
# Server
#

class OcrdMetsServer():

    def __init__(self, workspace, host, port, socket):
        self.workspace = workspace
        self.host = host
        self.port = port
        self.socket = socket
        self.log = getLogger('ocrd.workspace_client')


    def startup(self):

        # XXX HACK 
        # circumventing dependency injection like this is bad and
        # needs to be refactored once it's all runnign
        workspace = self.workspace

        app = FastAPI(
            title="OCR-D METS Server",
            description="Providing simultaneous write-access to mets.xml for OCR-D",
        )

        @app.exception_handler(ValidationError)
        async def exception_handler_invalid400(request: Request, exc: ValidationError):
            return JSONResponse(status_code=400, content=exc.errors())

        @app.exception_handler(FileExistsError)
        async def exception_handler_invalid400(request: Request, exc: FileExistsError):
            return JSONResponse(status_code=400, content=str(exc))

        @app.exception_handler(re.error)
        async def exception_handler_invalid400(request: Request, exc: re.error):
            return JSONResponse(status_code=400, content=f'invalid regex: {exc}')

        @app.get("/", response_model=OcrdFileListModel)
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
            return OcrdFileListModel(
                files=[OcrdFileModel(file_grp=of.fileGrp, file_id=of.ID, mimetype=of.mimetype, page_id=of.pageId, url=of.url) for of in found]
            )

        @app.put('/')
        def save():
            return workspace.save_mets()

        @app.post('/', response_model=OcrdFileModel)
        async def add_file(
            data : bytes = File(),
            file_grp : str = Form(),
            file_id : str = Form(),
            page_id : Union[str, None] = Form(),
            mimetype : str = Form(),
            url : str = Form(),
        ):
            """
            Add a file
            """
            # Validate
            file_resource = OcrdFileModel(file_grp=file_grp, file_id=file_id, page_id=page_id, mimetype=mimetype, url=url)
            # Add to workspace
            kwargs = file_resource.dict()
            kwargs['page_id'] = page_id
            kwargs['content'] = data
            kwargs['local_filename'] = kwargs.pop('url')
            workspace.add_file(**kwargs)
            workspace.save_mets()
            return file_resource

        @app.get('/file_groups', response_model=OcrdFileGroupListModel)
        async def file_groups():
            return {'file_groups': workspace.mets.file_groups}

        @app.post('/agent', response_model=OcrdAgentModel)
        async def add_agent(agent : OcrdAgentModel):
            kwargs = agent.dict()
            workspace.mets.add_agent(**kwargs)
            workspace.save_mets()
            return agent

        @app.delete('/')
        async def stop():
            """
            Stop the server
            """
            getLogger('ocrd_models.ocrd_mets').info('Shutting down')
            workspace.save_mets()
            # XXX HACK os._exit to not trigger SystemExit caught by uvicorn with sys.exit
            _exit(0)


        uvicorn.run(app, host=self.host, port=self.port, uds=self.socket)


