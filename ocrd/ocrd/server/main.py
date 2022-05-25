from functools import lru_cache
from typing import Type, Dict

from fastapi import FastAPI, APIRouter, status

from ocrd import Processor
from ocrd.server.database import initiate_database
from ocrd.server.models.ocrd_tool import OcrdTool


def create_server(title: str, description: str, version: str,
                  ocrd_tool: Dict, processor_class: Type[Processor] | None) -> FastAPI:
    tags_metadata = [
        {
            'name': 'Processing',
            'description': 'OCR-D processing and processors'
        }
    ]

    app = FastAPI(
        title=title,
        description=description,
        version=version,
        openapi_tags=tags_metadata
    )

    router = APIRouter()

    @router.get('/', tags=['Processing'], status_code=status.HTTP_200_OK,
                summary='Get information about this processor.',
                response_model=OcrdTool)
    async def get_processor_info():
        return ocrd_tool

    @router.post('/', tags=['Processing'])
    async def process():
        pass

    app.include_router(router, prefix='/processor')

    @app.on_event("startup")
    async def start_database():
        await initiate_database()

    return app


@lru_cache
async def get_processor(parameter, processor_concrete_class: Type[Processor] | None) -> Processor | None:
    if processor_concrete_class:
        return processor_concrete_class(workspace=None, parameter=parameter)
    return None
