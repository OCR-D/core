from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from httpx import AsyncClient, Timeout
from json import dumps, loads
from logging import Logger
from pathlib import Path
from requests import get as requests_get
from typing import Dict, List, Union
from urllib.parse import urljoin

from ocrd.resolver import Resolver
from ocrd.task_sequence import ProcessorTask
from ocrd.workspace import Workspace
from ocrd_validators import ParameterValidator

from .database import (
    db_create_workspace,
    db_get_processing_job,
    db_get_workflow_job,
    db_get_workflow_script,
    db_get_workspace
)
from .models import DBProcessorJob, DBWorkflowJob, DBWorkspace, PYJobInput, PYJobOutput
from .rabbitmq_utils import OcrdProcessingMessage
from .utils import (
    calculate_processing_request_timeout,
    expand_page_ids,
    generate_created_time,
    generate_workflow_content,
    get_ocrd_workspace_physical_pages
)


def create_processing_message(logger: Logger, job: DBProcessorJob) -> OcrdProcessingMessage:
    try:
        processing_message = OcrdProcessingMessage(
            job_id=job.job_id,
            processor_name=job.processor_name,
            created_time=generate_created_time(),
            path_to_mets=job.path_to_mets,
            workspace_id=job.workspace_id,
            input_file_grps=job.input_file_grps,
            output_file_grps=job.output_file_grps,
            page_id=job.page_id,
            parameters=job.parameters,
            result_queue_name=job.result_queue_name,
            callback_url=job.callback_url,
            internal_callback_url=job.internal_callback_url
        )
        return processing_message
    except ValueError as error:
        message = f"Failed to create OcrdProcessingMessage from DBProcessorJob"
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def create_workspace_if_not_exists(logger: Logger, mets_path: str) -> DBWorkspace:
    try:
        # Core cannot create workspaces by API, but the Processing Server needs
        # the workspace in the database. The workspace is created if the path is
        # available locally and not existing in the database - since it has not
        # been uploaded through the Workspace Server.
        db_workspace = await db_create_workspace(mets_path)
        return db_workspace
    except FileNotFoundError as error:
        message = f"Mets file path not existing: {mets_path}"
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


async def get_from_database_workflow_job(logger: Logger, workflow_job_id: str) -> DBWorkflowJob:
    try:
        workflow_job = await db_get_workflow_job(workflow_job_id)
        return workflow_job
    except ValueError as error:
        message = f"Workflow job with id '{workflow_job_id}' not found in the DB."
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


async def get_from_database_workspace(
    logger: Logger,
    workspace_id: str = None,
    workspace_mets_path: str = None
) -> DBWorkspace:
    try:
        db_workspace = await db_get_workspace(workspace_id, workspace_mets_path)
        return db_workspace
    except ValueError as error:
        message = f"Workspace with id '{workspace_id}' not found in the DB."
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


def get_page_ids_list(logger: Logger, mets_path: str, page_id: str) -> List[str]:
    try:
        if page_id:
            page_range = expand_page_ids(page_id)
        else:
            # If no page_id is specified, all physical pages are assigned as page range
            page_range = get_ocrd_workspace_physical_pages(mets_path=mets_path)
        return page_range
    except Exception as error:
        message = f"Failed to determine page range for mets path: {mets_path}"
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def _get_processor_job(logger: Logger, job_id: str) -> PYJobOutput:
    """ Return processing job-information from the database
    """
    try:
        job = await db_get_processing_job(job_id)
        return job.to_job_output()
    except ValueError as error:
        message = f"Processing job with id '{job_id}' not existing."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def _get_processor_job_log(logger: Logger, job_id: str) -> FileResponse:
    db_job = await _get_processor_job(logger, job_id)
    log_file_path = Path(db_job.log_file_path)
    return FileResponse(path=log_file_path, filename=log_file_path.name)


def request_processor_server_tool_json(logger: Logger, processor_server_base_url: str) -> Dict:
    # Request the ocrd tool json from the Processor Server
    try:
        response = requests_get(
            urljoin(base=processor_server_base_url, url="info"),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            message = f"Failed to retrieve tool json from: {processor_server_base_url}, code: {response.status_code}"
            raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message)
        return response.json()
    except Exception as error:
        message = f"Failed to retrieve ocrd tool json from: {processor_server_base_url}"
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


async def forward_job_to_processor_server(
    logger: Logger, job_input: PYJobInput, processor_server_base_url: str
) -> PYJobOutput:
    try:
        json_data = dumps(job_input.dict(exclude_unset=True, exclude_none=True))
    except Exception as error:
        message = f"Failed to json dump the PYJobInput: {job_input}"
        raise_http_exception(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, message, error)

    # TODO: The amount of pages should come as a request input
    # TODO: cf https://github.com/OCR-D/core/pull/1030/files#r1152551161
    #  currently, use 200 as a default
    request_timeout = calculate_processing_request_timeout(amount_pages=200, timeout_per_page=20.0)

    # Post a processing job to the Processor Server asynchronously
    async with AsyncClient(timeout=Timeout(timeout=request_timeout, connect=30.0)) as client:
        response = await client.post(
            urljoin(base=processor_server_base_url, url="run"),
            headers={"Content-Type": "application/json"},
            json=loads(json_data)
        )
    if response.status_code != 202:
        message = f"Failed to post '{job_input.processor_name}' job to: {processor_server_base_url}"
        raise_http_exception(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, message)
    job_output = response.json()
    return job_output


async def get_workflow_content(logger: Logger, workflow_id: str, workflow: Union[UploadFile, None]) -> str:
    if not workflow and not workflow_id:
        message = "Either 'workflow' must be uploaded as a file or 'workflow_id' must be provided. Both are missing."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message)
    if workflow_id:
        try:
            db_workflow = await db_get_workflow_script(workflow_id)
            return db_workflow.content
        except ValueError as error:
            message = f"Workflow with id '{workflow_id}' not found"
            raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)
    return await generate_workflow_content(workflow)


async def validate_and_return_mets_path(logger: Logger, job_input: PYJobInput) -> str:
    if job_input.workspace_id:
        db_workspace = await get_from_database_workspace(logger, job_input.workspace_id)
        return db_workspace.workspace_mets_path
    return job_input.path_to_mets


def parse_workflow_tasks(logger: Logger, workflow_content: str) -> List[ProcessorTask]:
    try:
        tasks_list = workflow_content.splitlines()
        return [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
    except ValueError as error:
        message = f"Failed parsing processing tasks from a workflow."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


def raise_http_exception(logger: Logger, status_code: int, message: str, error: Exception = None) -> None:
    logger.exception(f"{message} {error}")
    raise HTTPException(status_code=status_code, detail=message)


def validate_job_input(logger: Logger, processor_name: str, ocrd_tool: dict, job_input: PYJobInput) -> None:
    if bool(job_input.path_to_mets) == bool(job_input.workspace_id):
        message = (
            "Wrong processing job input format. "
            "Either 'path_to_mets' or 'workspace_id' must be provided. "
            "Both are provided or both are missing."
        )
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message)
    if not ocrd_tool:
        message = f"Failed parsing processing tasks from a workflow."
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message)
    try:
        report = ParameterValidator(ocrd_tool).validate(dict(job_input.parameters))
        if not report.is_valid:
            message = f"Failed to validate processing job input against the tool json of processor: {processor_name}\n"
            raise_http_exception(logger, status.HTTP_404_BAD_REQUEST, message + report.errors)
    except Exception as error:
        message = f"Failed to validate processing job input against the ocrd tool json of processor: {processor_name}"
        raise_http_exception(logger, status.HTTP_404_BAD_REQUEST, message, error)


def validate_workflow(logger: Logger, workflow: str) -> None:
    """
    Check whether workflow is not empty and parseable to a lists of ProcessorTask
    """
    if not workflow.strip():
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message="Workflow is invalid, empty.")
    try:
        tasks_list = workflow.splitlines()
        [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
    except ValueError as error:
        message = "Provided workflow script is invalid, failed to parse ProcessorTasks."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


def validate_first_task_input_file_groups_existence(logger: Logger, mets_path: str, input_file_grps: List[str]):
    # Validate the input file groups of the first task in the workflow
    available_groups = Workspace(Resolver(), Path(mets_path).parents[0]).mets.file_groups
    for group in input_file_grps:
        if group not in available_groups:
            message = f"Input file group '{group}' of the first processor not found: {input_file_grps}"
            raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message)
