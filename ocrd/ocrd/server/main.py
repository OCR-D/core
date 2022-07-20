import json
from typing import Type

from beanie import PydanticObjectId
from fastapi import FastAPI, HTTPException, status, BackgroundTasks

from ocrd import Processor, Resolver
from ocrd.processor.helpers import run_processor_from_api, run_cli_from_api, get_processor
from ocrd.server.database import initiate_database
from ocrd.server.models.job import Job, JobInput, StateEnum
from ocrd.server.models.ocrd_tool import OcrdTool


class ProcessorAPI(FastAPI):

    def __init__(self, title: str, description: str, version: str, db_url: str, ocrd_tool: dict,
                 processor_class: Type[Processor] = None):
        # Description for the Swagger page
        tags_metadata = [
            {
                'name': 'Processing',
                'description': 'OCR-D processing and processors'
            }
        ]
        self.db_url = db_url
        self.ocrd_tool = ocrd_tool
        self.processor_class = processor_class

        # Set collection name for the Job model
        Job.Settings.name = ocrd_tool['executable']

        super().__init__(title=title, description=description, version=version, openapi_tags=tags_metadata,
                         on_startup=[self.startup])

        # Create routes
        self.router.add_api_route(
            path='/',
            endpoint=self.get_processor_info,
            methods=['GET'],
            tags=['Processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about this processor.',
            response_model=OcrdTool,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/',
            endpoint=self.process,
            methods=['POST'],
            tags=['Processing'],
            status_code=status.HTTP_202_ACCEPTED,
            summary='Submit a job to this processor.',
            response_model=Job,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

        self.router.add_api_route(
            path='/{job_id}',
            endpoint=self.get_job,
            methods=['GET'],
            tags=['Processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about a job based on its ID',
            response_model=Job,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

    async def startup(self):
        await initiate_database(db_url=self.db_url)

    async def get_processor_info(self):
        return self.ocrd_tool

    async def process(self, data: JobInput, background_tasks: BackgroundTasks):
        job = Job(**data.dict(exclude_unset=True, exclude_none=True), state=StateEnum.queued)
        await job.insert()

        # Build the workspace
        resolver = Resolver()
        workspace = resolver.workspace_from_url(data.path)

        try:
            # Get the processor, if possible
            processor = get_processor(json.dumps(data.parameters), self.processor_class)
        except Exception as e:
            # In case of bad parameters
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

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
                executable=self.title,
                workspace=workspace,
                page_id=data.page_id,
                input_file_grps=data.input_file_grps,
                output_file_grps=data.output_file_grps,
                parameter=data.parameters
            )

        return job

    async def get_job(self, job_id: PydanticObjectId):
        job = await Job.get(job_id)
        if job:
            return job
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Job not found.'
        )
