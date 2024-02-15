from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from logging import Logger
from pathlib import Path
from typing import List, Union

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
from .models import DBWorkflowJob, DBWorkspace, PYJobInput, PYJobOutput
from .utils import (
    expand_page_ids,
    generate_workflow_content,
    get_ocrd_workspace_physical_pages
)


async def create_workspace_if_not_exists(logger: Logger, mets_path: str) -> DBWorkspace:
    try:
        # Core cannot create workspaces by API, but the Processing Server needs
        # the workspace in the database. The workspace is created if the path is
        # available locally and not existing in the database - since it has not
        # been uploaded through the Workspace Server.
        db_workspace = await db_create_workspace(mets_path)
    except FileNotFoundError as error:
        msg = f"Mets file path not existing: {mets_path}"
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    return db_workspace


async def get_from_database_workflow_job(logger: Logger, workflow_job_id: str) -> DBWorkflowJob:
    try:
        workflow_job = await db_get_workflow_job(workflow_job_id)
    except ValueError as error:
        msg = f"Workflow job with id: {workflow_job_id} not found"
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    return workflow_job


async def get_from_database_workspace(
    logger: Logger,
    workspace_id: str = None,
    workspace_mets_path: str = None
) -> DBWorkspace:
    try:
        db_workspace = await db_get_workspace(workspace_id, workspace_mets_path)
    except ValueError as error:
        logger.exception(error)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id '{workspace_id}' not found in the DB."
        )
    return db_workspace


def get_page_ids_list(logger: Logger, mets_path: str, page_id: str) -> List[str]:
    try:
        if page_id:
            page_range = expand_page_ids(page_id)
        else:
            # If no page_id is specified, all physical pages are assigned as page range
            page_range = get_ocrd_workspace_physical_pages(mets_path=mets_path)
        return page_range
    except BaseException as error:
        msg = f"Failed to determine page range for mets path: {mets_path}"
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


async def _get_processor_job(logger: Logger, job_id: str) -> PYJobOutput:
    """ Return processing job-information from the database
    """
    try:
        job = await db_get_processing_job(job_id)
        return job.to_job_output()
    except ValueError as error:
        msg = f"Processing job with id '{job_id}' not existing."
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


async def _get_processor_job_log(logger: Logger, job_id: str) -> FileResponse:
    db_job = await _get_processor_job(logger, job_id)
    log_file_path = Path(db_job.log_file_path)
    return FileResponse(path=log_file_path, filename=log_file_path.name)


async def get_workflow_content(logger: Logger, workflow_id: str, workflow: Union[UploadFile, None]) -> str:
    if not workflow and not workflow_id:
        msg = """
            Either 'workflow' binary or 'workflow_id' must be provided. 
            Both are missing.
            """
        logger.exception(msg)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    if workflow_id:
        try:
            db_workflow = await db_get_workflow_script(workflow_id)
        except ValueError as error:
            msg = f"Workflow with id '{workflow_id}' not found"
            logger.exception(f"{msg}, error: {error}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return db_workflow.content
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
        msg = f"Failed parsing processing tasks from a workflow"
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


def validate_job_input(logger: Logger, processor_name: str, ocrd_tool: dict, job_input: PYJobInput) -> None:
    if bool(job_input.path_to_mets) == bool(job_input.workspace_id):
        msg = """
        Wrong processing job input format. 
        Either 'path_to_mets' or 'workspace_id' must be provided. 
        Both are provided or both are missing.
        """
        logger.exception(msg)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    if not ocrd_tool:
        msg = f"Processor '{processor_name}' not available. Empty or missing ocrd tool json."
        logger.exception(msg)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    try:
        report = ParameterValidator(ocrd_tool).validate(dict(job_input.parameters))
    except Exception as error:
        msg = f"Failed to validate processing job input against the ocrd tool json of processor: {processor_name}"
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    if not report.is_valid:
        msg = f"Failed to validate processing job input against the ocrd tool json of processor: {processor_name}"
        logger.exception(f"{msg}, report error: {report.errors}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def validate_workflow(logger: Logger, workflow: str) -> None:
    """
    Check whether workflow is not empty and parseable to a lists of ProcessorTask
    """
    if not workflow.strip():
        msg = "Workflow is invalid, empty."
        logger.exception(f"{msg}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    try:
        tasks_list = workflow.splitlines()
        [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
    except ValueError as error:
        msg = "Provided workflow script is invalid, failed to parse ProcessorTasks"
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


def validate_first_task_input_file_groups_existence(logger: Logger, mets_path: str, input_file_grps: List[str]):
    # Validate the input file groups of the first task in the workflow
    available_groups = Workspace(Resolver(), Path(mets_path).parents[0]).mets.file_groups
    for grp in input_file_grps:
        if grp not in available_groups:
            msg = f"Input file grps of the 1st processor not found: {input_file_grps}"
            logger.exception(msg)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
