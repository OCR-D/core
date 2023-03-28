from contextlib import redirect_stdout
from io import StringIO
from subprocess import run, PIPE
import uvicorn

from fastapi import FastAPI, HTTPException, status, BackgroundTasks

from ocrd import Resolver
# from ocrd.processor.helpers import run_processor_from_api, run_cli_from_api
from ocrd_validators import ParameterValidator
from ocrd_utils import (
    get_ocrd_tool_json,
    parse_json_string_with_comments,
    set_json_key_value_overrides
)

from .database import (
    DBProcessorJob,
    db_get_processing_job,
    initiate_database
)
from .models import (
    PYJobInput,
    PYJobOutput,
    PYOcrdTool,
    StateEnum
)


class ProcessorServer(FastAPI):

    def __init__(self, processor_name: str, mongodb_addr: str, processor_class=None):
        self.processor_name = processor_name
        self.db_url = mongodb_addr
        self.ProcessorClass = processor_class
        self.ocrd_tool = None
        self.version = None

        self.version = self.get_version()
        self.ocrd_tool = self.get_ocrd_tool()

        if not self.ocrd_tool:
            raise Exception(f"The ocrd_tool is empty or missing")

        tags_metadata = [
            {
                'name': 'Processing',
                'description': 'OCR-D Processor Server'
            }
        ]

        super().__init__(
            title=self.ocrd_tool['executable'],
            description=self.ocrd_tool['description'],
            version=self.version,
            openapi_tags=tags_metadata,
            on_startup=[self.startup]
        )

        # Create routes
        self.router.add_api_route(
            path='/',
            endpoint=self.get_processor_info,
            methods=['GET'],
            tags=['Processing'],
            status_code=status.HTTP_200_OK,
            summary='Get information about this processor.',
            response_model=PYOcrdTool,
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
            response_model=PYJobOutput,
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
            response_model=PYJobOutput,
            response_model_exclude_unset=True,
            response_model_exclude_none=True
        )

    async def startup(self):
        await initiate_database(db_url=self.db_url)
        DBProcessorJob.Settings.name = self.processor_name

    async def get_processor_info(self):
        return self.ocrd_tool

    async def process(self, data: PYJobInput, background_tasks: BackgroundTasks):
        # TODO: Adapt from #884
        pass

    async def get_job(self, processor_name: str, job_id: str) -> PYJobOutput:
        """ Return processing job-information from the database
        """
        try:
            job = await db_get_processing_job(job_id)
            return job.to_job_output()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Processing job with id '{job_id}' of processor type '{processor_name}' not existing"
            )

    def get_ocrd_tool(self):
        if self.ocrd_tool:
            return self.ocrd_tool
        if self.ProcessorClass:
            str_out = StringIO()
            with redirect_stdout(str_out):
                self.ProcessorClass(workspace=None, dump_json=True)
            ocrd_tool = parse_json_string_with_comments(str_out.getvalue())
        else:
            ocrd_tool = get_ocrd_tool_json(self.processor_name)
        return ocrd_tool

    def get_version(self) -> str:
        if self.version:
            return self.version
        if self.ProcessorClass:
            str_out = StringIO()
            with redirect_stdout(str_out):
                self.ProcessorClass(workspace=None, show_version=True)
            version_str = str_out.getvalue()
        else:
            version_str = run(
                [self.processor_name, '--version'],
                stdout=PIPE,
                check=True,
                universal_newlines=True
            ).stdout
        # the version string is in format: Version %s, ocrd/core %s
        return version_str

    def run_server(self, host, port):
        uvicorn.run(self, host=host, port=port, access_log=False)
