import re
from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
from ocrd_validators import ParameterValidator
from ocrd_utils import (
    generate_range,
    REGEX_PREFIX
)
from .database import (
    db_get_processing_job,
    db_get_workspace,
)
from .models import PYJobInput, PYJobOutput


async def _get_processor_job(logger, job_id: str) -> PYJobOutput:
    """ Return processing job-information from the database
    """
    try:
        job = await db_get_processing_job(job_id)
        return job.to_job_output()
    except ValueError as e:
        logger.exception(f"Processing job with id '{job_id}' not existing, error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Processing job with id '{job_id}' not existing"
        )


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
        except ValueError as e:
            logger.exception(f"Workspace with id '{job_input.workspace_id}' not existing: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Workspace with id '{job_input.workspace_id}' not existing"
            )
        return path_to_mets
    return job_input.path_to_mets


def expand_page_ids(page_id: str) -> List:
    page_ids = []
    if not page_id:
        return page_ids
    for page_id_token in re.split(r',', page_id):
        if page_id_token.startswith(REGEX_PREFIX):
            page_ids.append(re.compile(page_id_token[len(REGEX_PREFIX):]))
        elif '..' in page_id_token:
            page_ids += generate_range(*page_id_token.split('..', 1))
        else:
            page_ids += [page_id_token]
    return page_ids


def validate_job_input(logger, processor_name: str, ocrd_tool: dict, job_input: PYJobInput) -> None:
    if bool(job_input.path_to_mets) == bool(job_input.workspace_id):
        logger.exception("Either 'path_to_mets' or 'workspace_id' must be provided, but not both")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'path_to_mets' or 'workspace_id' must be provided, but not both"
        )
    if not ocrd_tool:
        logger.exception(f"Processor '{processor_name}' not available. Empty or missing ocrd_tool")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processor '{processor_name}' not available. Empty or missing ocrd_tool"
        )
    try:
        report = ParameterValidator(ocrd_tool).validate(dict(job_input.parameters))
    except Exception as e:
        logger.exception(f'Failed to validate processing job against the ocrd_tool: {e}')
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Failed to validate processing job against the ocrd_tool'
        )
    else:
        if not report.is_valid:
            log_msg = f'Failed to validate processing job against the ocrd_tool, errors: {report.errors}'
            logger.exception(log_msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=log_msg)
