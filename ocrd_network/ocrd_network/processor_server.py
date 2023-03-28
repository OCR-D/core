from datetime import datetime
import json
import logging
from os import environ, getpid
from subprocess import run, PIPE
from typing import List
import uvicorn

from fastapi import FastAPI, HTTPException, status, BackgroundTasks

from ocrd.processor.helpers import run_cli, run_processor
from ocrd import Resolver
from ocrd_validators import ParameterValidator
from ocrd_utils import (
    initLogging,
    getLogger,
    get_ocrd_tool_json
)

from .database import (
    DBProcessorJob,
    db_get_processing_job,
    db_get_workspace,
    db_update_processing_job,
    initiate_database
)
from .models import (
    PYJobInput,
    PYJobOutput,
    PYOcrdTool,
    StateEnum
)
from .utils import calculate_execution_time, generate_id

# TODO: Check this again when the logging is refactored
try:
    # This env variable must be set before importing from Keras
    environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    from tensorflow.keras.utils import disable_interactive_logging
    # Enabled interactive logging throws an exception
    # due to a call of sys.stdout.flush()
    disable_interactive_logging()
except Exception:
    # Nothing should be handled here if TF is not available
    pass


class ProcessorServer(FastAPI):
    def __init__(self, mongodb_addr: str, processor_name: str = "", processor_class=None):
        if not (processor_name or processor_class):
            raise ValueError('Either "processor_name" or "processor_class" must be provided')
        initLogging()
        self.log = getLogger(__name__)

        self.db_url = mongodb_addr
        self.processor_name = processor_name
        self.ProcessorClass = processor_class
        self.ocrd_tool = None
        self.version = None

        self.version = self.get_version()
        self.ocrd_tool = self.get_ocrd_tool()

        if not self.ocrd_tool:
            raise Exception(f"The ocrd_tool is empty or missing")

        if not self.processor_name:
            self.processor_name = self.ocrd_tool['executable']

        tags_metadata = [
            {
                'name': 'Processing',
                'description': 'OCR-D Processor Server'
            }
        ]

        super().__init__(
            title=self.processor_name,
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
            endpoint=self.create_processor_job_task,
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
        if not self.ocrd_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Empty or missing ocrd_tool'
            )
        return self.ocrd_tool

    # Note: The Processing server pushes to a queue, while
    #  the Processor Server creates (pushes to) a background task
    async def create_processor_job_task(self, data: PYJobInput, background_tasks: BackgroundTasks):
        if not self.ocrd_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Empty or missing ocrd_tool'
            )
        report = ParameterValidator(self.ocrd_tool).validate(dict(data.parameters))
        if not report.is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=report.errors)

        if bool(data.path_to_mets) == bool(data.workspace_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either 'path' or 'workspace_id' must be provided, but not both"
            )

        # This check is done to return early in case
        # the workspace_id is provided but not existing in the DB
        elif data.workspace_id:
            try:
                await db_get_workspace(data.workspace_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Workspace with id '{data.workspace_id}' not existing"
                )

        job = DBProcessorJob(
            **data.dict(exclude_unset=True, exclude_none=True),
            job_id=generate_id(),
            processor_name=self.processor_name,
            state=StateEnum.queued
        )
        await job.insert()

        if self.ProcessorClass:
            # Run the processor in the background
            background_tasks.add_task(
                self.run_processor_from_server,
                job_id=job.id,
                workspace_id=data.workspace_id,
                page_id=data.page_id,
                parameter=data.parameters,
                input_file_grps=data.input_file_grps,
                output_file_grps=data.output_file_grps,
            )
        else:
            # Run the CLI in the background
            background_tasks.add_task(
                self.run_cli_from_server,
                job_id=job.id,
                workspace_id=data.workspace_id,
                page_id=data.page_id,
                input_file_grps=data.input_file_grps,
                output_file_grps=data.output_file_grps,
                parameter=data.parameters
            )
        return job.to_job_output()

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
            ocrd_tool = self.ProcessorClass(workspace=None, version=True).ocrd_tool
        else:
            ocrd_tool = get_ocrd_tool_json(self.processor_name)
        return ocrd_tool

    def get_version(self) -> str:
        if self.version:
            return self.version
        if self.ProcessorClass:
            version_str = self.ProcessorClass(workspace=None, version=True).version
        else:
            version_str = run(
                [self.processor_name, '--version'],
                stdout=PIPE,
                check=True,
                universal_newlines=True
            ).stdout
        return version_str

    def run_server(self, host, port, access_log=False):
        # TODO: Provide more flexibility for configuring file logging (i.e. via ENV variables)
        file_handler = logging.FileHandler(f'/tmp/server_{self.processor_name}_{port}_{getpid()}.log', mode='a')
        logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_handler.setFormatter(logging.Formatter(logging_format))
        file_handler.setLevel(logging.DEBUG)
        self.log.addHandler(file_handler)
        uvicorn.run(self, host=host, port=port, access_log=access_log)

    async def run_cli_from_server(
            self,
            job_id: str,
            processor_name: str,
            workspace_id: str,
            input_file_grps: List[str],
            output_file_grps: List[str],
            page_id: str,
            parameters: dict
    ):
        log = getLogger('ocrd.processor.helpers.run_cli_from_api')

        # Turn input/output file groups into a comma separated string
        input_file_grps_str = ','.join(input_file_grps)
        output_file_grps_str = ','.join(output_file_grps)

        workspace_db = await db_get_workspace(workspace_id)
        path_to_mets = workspace_db.workspace_mets_path
        workspace = Resolver().workspace_from_url(path_to_mets)

        start_time = datetime.now()
        await db_update_processing_job(
            job_id=job_id,
            state=StateEnum.running,
            start_time=start_time
        )
        # Execute the processor
        return_code = run_cli(
            executable=processor_name,
            workspace=workspace,
            page_id=page_id,
            input_file_grp=input_file_grps_str,
            output_file_grp=output_file_grps_str,
            parameter=json.dumps(parameters),
            mets_url=workspace.mets_target
        )
        end_time = datetime.now()
        # Execution duration in ms
        execution_duration = calculate_execution_time(start_time, end_time)

        if return_code != 0:
            job_state = StateEnum.failed
            log.error(f'{self.processor_name} exited with non-zero return value {return_code}.')
        else:
            job_state = StateEnum.success

        await db_update_processing_job(
            job_id=job_id,
            state=job_state,
            end_time=end_time,
            exec_time=f'{execution_duration} ms'
        )

    async def run_processor_from_server(
            self,
            job_id: str,
            workspace_id: str,
            input_file_grps: List[str],
            output_file_grps: List[str],
            page_id: str,
            parameters: dict,
    ):
        log = getLogger('ocrd.processor.helpers.run_processor_from_api')

        # Turn input/output file groups into a comma separated string
        input_file_grps_str = ','.join(input_file_grps)
        output_file_grps_str = ','.join(output_file_grps)

        workspace_db = await db_get_workspace(workspace_id)
        path_to_mets = workspace_db.workspace_mets_path
        workspace = Resolver().workspace_from_url(path_to_mets)

        is_success = True
        start_time = datetime.now()
        await db_update_processing_job(
            job_id=job_id,
            state=StateEnum.running,
            start_time=start_time
        )
        try:
            run_processor(
                processorClass=self.ProcessorClass,
                workspace=workspace,
                page_id=page_id,
                parameter=parameters,
                input_file_grp=input_file_grps_str,
                output_file_grp=output_file_grps_str,
                instance_caching=True
            )
        except Exception as e:
            is_success = False
            log.exception(e)

        end_time = datetime.now()
        # Execution duration in ms
        execution_duration = calculate_execution_time(start_time, end_time)
        job_state = StateEnum.success if is_success else StateEnum.failed
        await db_update_processing_job(
            job_id=job_id,
            state=job_state,
            end_time=end_time,
            exec_time=f'{execution_duration} ms'
        )
