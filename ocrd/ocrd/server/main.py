from functools import lru_cache

from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter, status, HTTPException

from ocrd import Processor
from ocrd.server.config import Config
from ocrd.server.database import initiate_database
from ocrd.server.models.ocrd_tool import OcrdTool
from ocrd.server.models.job import StateEnum, JobInput, Job

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


@router.post('/', tags=['Processing'], status_code=status.HTTP_200_OK,
             summary='Submit a job to this processor.',
             response_model=Job)
async def process(data: JobInput):
    job = Job(**data.dict(skip_defaults=True), state=StateEnum.queued)
    await job.insert()
    return job


@router.get('/{job_id}', tags=['Processing'], status_code=status.HTTP_200_OK,
            summary='Get information about a job based on its ID',
            response_model=Job)
async def get_job(job_id: PydanticObjectId):
    job = await Job.get(job_id)
    if job:
        return job
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Job not found.'
    )


app.include_router(router, prefix='/processor')


@app.on_event('startup')
async def startup():
    await initiate_database(db_url=Config.db_url)


@lru_cache
async def get_processor(parameter) -> Processor | None:
    if Config.processor_class:
        return Config.processor_class(workspace=None, parameter=parameter)
    return None
