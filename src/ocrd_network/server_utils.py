from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List

from ocrd.resolver import Resolver
from ocrd.task_sequence import ProcessorTask
from ocrd.workspace import Workspace
from ocrd_validators import ParameterValidator

from .database import db_get_processing_job, db_get_workspace
from .models import PYJobInput, PYJobOutput


async def _get_processor_job(logger, job_id: str) -> PYJobOutput:
    """ Return processing job-information from the database
    """
    try:
        job = await db_get_processing_job(job_id)
        return job.to_job_output()
    except ValueError as error:
        msg = f"Processing job with id '{job_id}' not existing."
        logger.exception(f"{msg}, error: {error}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


async def _get_processor_job_log(logger, job_id: str) -> FileResponse:
    db_job = await _get_processor_job(logger, job_id)
    log_file_path = Path(db_job.log_file_path)
    return FileResponse(path=log_file_path, filename=log_file_path.name)


async def validate_and_return_mets_path(logger, job_input: PYJobInput) -> str:
    # This check is done to return early in case the workspace_id is provided
    # but the abs mets path cannot be queried from the DB
    if not job_input.path_to_mets and job_input.workspace_id:
        try:
            db_workspace = await db_get_workspace(job_input.workspace_id)
            path_to_mets = db_workspace.workspace_mets_path
        except ValueError as error:
            msg = f"Workspace with id '{job_input.workspace_id}' not existing."
            logger.exception(f"{msg}, error: {error}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
        return path_to_mets
    return job_input.path_to_mets


def validate_job_input(logger, processor_name: str, ocrd_tool: dict, job_input: PYJobInput) -> None:
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


def validate_workflow(workflow: str, logger=None) -> None:
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


def validate_first_task_input_file_groups_existence(logger, mets_path: str, input_file_grps: List[str]):
    # Validate the input file groups of the first task in the workflow
    available_groups = Workspace(Resolver(), Path(mets_path).parents[0]).mets.file_groups
    for grp in input_file_grps:
        if grp not in available_groups:
            msg = f"Input file grps of the 1st processor not found: {input_file_grps}"
            logger.exception(msg)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
