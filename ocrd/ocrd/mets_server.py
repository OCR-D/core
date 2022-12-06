import re
from os import environ
from typing import Any, Dict, Optional, Union, List

from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import JSONResponse
from requests import request
from pydantic import BaseModel, Field, constr, ValidationError

from ocrd import Resolver
from ocrd_utils import initLogging, getLogger, deprecated_alias

#
# XXX
#
initLogging()
workspace = Resolver().workspace_from_url('/home/kba/monorepo/assets/data/kant_aufklaerung_1784/data/mets.xml')

#
# Models
#

class OcrdFileModel(BaseModel):
    file_grp : str = Field()
    file_id : str = Field()
    mimetype : str = Field()
    page_id : Union[str, None] = Field()
    url : str = Field()

class OcrdFileListModel(BaseModel):
    files : List[OcrdFileModel] = Field()

#
# Client
#

class ClientSideOcrdFile:

    def __init__(self, el, mimetype=None, pageId=None, loctype='OTHER', local_filename=None, mets=None, url=None, ID=None):
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

class OcrdWorkspaceClient():

    def __init__(self, hostname, port):
        self.log = getLogger('ocrd.workspace_client')
        self.url = f'http://{hostname}:{port}'

    def find_files(self, **kwargs):
        r = request('GET', self.url, params={**kwargs})
        for f in r.json()['files']:
            yield ClientSideOcrdFile(None, ID=f.file_id, pageId=f.page_id, fileGrp=f.file_grp, url=f.url)

    def find_all_files(self, *args, **kwargs):
        return list(self.find_files(*args, **kwargs))

    @deprecated_alias(pageId="page_id")
    @deprecated_alias(ID="file_id")
    def add_file(self, file_grp, content=None, file_id=None, url=None, mimetype=None, page_id=None, **kwargs):
        r = request(
            'POST',
            self.url,
            data=OcrdFileModel(
                file_id=file_id,
                file_grp=file_grp,
                page_id=page_id,
                mimetype=mimetype,
                url=url).json(),
            files=('data', content)
        )

#
# FastAPI
#

app = FastAPI(
    title="OCR-D Workspace Server",
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

@app.on_event("startup")
async def on_startup():
    getLogger('ocrd.mets_server').info("Starting up")


@app.on_event("shutdown")
async def on_shutdown():
    getLogger('ocrd.mets_server').info("Shutting down")

@app.get(
    "/",
    # response_model=OcrdFileListModel,
)
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

@app.delete('/')
async def stop():
    """
    Stop the server
    """
    # TODO

@app.post(
    '/',
    response_model=OcrdFileModel
)
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

#
# Server
#

class OcrdWorkspaceServer():

    def __init__(self):
        self.hostname = hostname
        self.port = port
        self.log = getLogger('ocrd.workspace_client')

    def shutdown():
        pass

    def startup():
        uvicorn.run(workspace_server.app, hostname=self.hostname, port=self.port)


