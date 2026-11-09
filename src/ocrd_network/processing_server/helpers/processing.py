from logging import Logger
from pathlib import Path
from typing import Any, Dict

from fastapi import status
from fastapi.responses import FileResponse
from ocrd_validators import ParameterValidator

from ...database import db_get_processing_job
from ...models import DBProcessorJob, PYJobInput, PYJobOutput
from ...rabbitmq_utils import OcrdProcessingMessage
from ...utils import generate_created_time
from .common import raise_http_exception


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
        message = "Failed to create OcrdProcessingMessage from DBProcessorJob"
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def get_processor_job(logger: Logger, job_id: str) -> PYJobOutput:
    """Return processing job information from the database."""
    try:
        job = await db_get_processing_job(job_id)
        return job.to_job_output()
    except ValueError as error:
        message = f"Processing job with id '{job_id}' not existing."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def get_processor_job_log(logger: Logger, job_id: str) -> FileResponse:
    db_job = await get_processor_job(logger, job_id)
    log_file_path = Path(db_job.log_file_path)
    return FileResponse(path=log_file_path, filename=log_file_path.name)


def validate_job_input(logger: Logger, processor_name: str, ocrd_tool: Dict[str, Any], job_input: PYJobInput) -> None:
    if bool(job_input.path_to_mets) == bool(job_input.workspace_id):
        message = (
            "Wrong processing job input format. "
            "Either 'path_to_mets' or 'workspace_id' must be provided. "
            "Both are provided or both are missing."
        )
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message)
    if not ocrd_tool:
        message = "Missing ocrd tool, failed parsing processing tasks from a workflow."
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message)
    try:
        report = ParameterValidator(ocrd_tool).validate(dict(job_input.parameters))
    except Exception as error:
        message = f"Failed to validate processing job input against the ocrd tool json of processor: {processor_name}"
        raise_http_exception(logger, status.HTTP_400_BAD_REQUEST, message, error)
    if report and not report.is_valid:
        message = f"Failed to validate processing job input against the tool json of processor: {processor_name}\n"
        raise_http_exception(logger, status.HTTP_400_BAD_REQUEST, f"{message}{report.errors}")