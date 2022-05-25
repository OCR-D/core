from functools import lru_cache

from fastapi import FastAPI, APIRouter, status

from ocrd import Processor
from ocrd.server.config import Config
from ocrd.server.database import initiate_database
from ocrd.server.models.ocrd_tool import OcrdTool
from ocrd.server.models.processing import Processing

tags_metadata = [
    {
        'name': 'Processing',
        'description': 'OCR-D processing and processors'
    }
]

app = FastAPI(
    title=Config.title,
    description=Config.description,
    version=Config.version,
    openapi_tags=tags_metadata
)

router = APIRouter()


@router.get('/', tags=['Processing'], status_code=status.HTTP_200_OK,
            summary='Get information about this processor.',
            response_model=OcrdTool)
async def get_processor_info():
    return Config.ocrd_tool


@router.post('/', tags=['Processing'])
async def process(data: Processing):
    await data.create()
    return {'message': 'Done'}


app.include_router(router, prefix='/processor')


@app.on_event('startup')
async def startup():
    await initiate_database(db_url=Config.db_url)


@lru_cache
async def get_processor(parameter) -> Processor | None:
    if Config.processor_class:
        return Config.processor_class(workspace=None, parameter=parameter)
    return None
