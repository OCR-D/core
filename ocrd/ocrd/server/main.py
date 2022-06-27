import json
from functools import lru_cache

from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter, status, HTTPException, BackgroundTasks

from ocrd import Processor, Resolver
from ocrd.processor.helpers import run_processor_from_api, run_cli_from_api
from ocrd.server.config import Config
from ocrd.server.database import initiate_database
from ocrd.server.models.job import StateEnum, JobInput, Job
from ocrd.server.models.ocrd_tool import OcrdTool
from ocrd_validators import ParameterValidator

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


@router.post('/', tags=['Processing'], status_code=status.HTTP_202_ACCEPTED,
             summary='Submit a job to this processor.',
             response_model=Job)
async def process(data: JobInput, background_tasks: BackgroundTasks):
    job = Job(**data.dict(skip_defaults=True), state=StateEnum.queued)
    await job.insert()

    # Build the workspace
    resolver = Resolver()
    workspace = resolver.workspace_from_url(data.path)

    # Get the processor, if possible
    processor = get_processor(json.dumps(data.parameters))

    if processor:
        # Run the processor in the background
        background_tasks.add_task(
            run_processor_from_api,
            job_id=job.id,
            processor=processor,
            workspace=workspace,
            page_id=data.page_id,
            input_file_grps=data.input_file_grps,
            output_file_grps=data.output_file_grps,
        )
    else:
        # Run the CLI in the background
        background_tasks.add_task(
            run_cli_from_api,
            job_id=job.id,
            executable=Config.title,
            workspace=workspace,
            page_id=data.page_id,
            input_file_grps=data.input_file_grps,
            output_file_grps=data.output_file_grps,
            parameter=data.parameters
        )

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
def get_processor(parameter_str: str) -> Processor | None:
    """
    Call this function to get back an instance of a processor. The results are cached based on the parameters.
    The parameters must be passed as a string because
    `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_ is unhashable,
    therefore cannot be cached.
    Args:
        parameter_str (string): a serialized version of a dictionary of parameters.

    Returns:
        When the server is started by the `ocrd server` command, the concrete class of the processor is unknown.
        In this case, `None` is returned. Otherwise, an instance of the `:py:class:~ocrd.Processor` is returned.
    """
    parameter = json.loads(parameter_str)

    # Validate the parameter
    parameter_validator = ParameterValidator(Config.ocrd_tool)
    report = parameter_validator.validate(parameter)
    if not report.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=report.errors,
        )

    if Config.processor_class:
        return Config.processor_class(workspace=None, parameter=parameter)
    return None
