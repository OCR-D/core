from logging import Logger
from typing import List, Union

from fastapi import status, UploadFile
from httpx import AsyncClient, Timeout
from ocrd.task_sequence import ProcessorTask

from ...constants import JobState
from ...database import db_get_workflow_job, db_get_workflow_script
from ...models import DBWorkflowJob
from ...utils import expand_page_ids, generate_workflow_content, get_ocrd_workspace_physical_pages
from .common import raise_http_exception


async def get_from_database_workflow_job(logger: Logger, workflow_job_id: str) -> DBWorkflowJob:
    try:
        return await db_get_workflow_job(workflow_job_id)
    except ValueError as error:
        message = f"Workflow job with id '{workflow_job_id}' not found in the DB."
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


def get_page_ids_list(logger: Logger, mets_path: str, page_id: str) -> List[str]:
    try:
        if page_id:
            page_range = expand_page_ids(page_id)
        else:
            # If no page_id is specified, all physical pages are assigned as page range.
            page_range = get_ocrd_workspace_physical_pages(mets_path=mets_path)
        return page_range
    except Exception as error:
        message = f"Failed to determine page range for mets path: {mets_path}"
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def get_workflow_content(
    logger: Logger, workflow_id: str, workflow: Union[UploadFile, str, None]
) -> str:
    if not workflow and not workflow_id:
        message = (
            "Either 'workflow' must be uploaded as a file or 'workflow_id' must be provided. "
            "Both are missing."
        )
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message)
    if workflow_id:
        try:
            db_workflow = await db_get_workflow_script(workflow_id)
            return db_workflow.content
        except ValueError as error:
            message = f"Workflow with id '{workflow_id}' not found"
            raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)
    if isinstance(workflow, str):
        with open(workflow) as wf_file:
            return wf_file.read()
    return await generate_workflow_content(workflow)


def parse_workflow_tasks(logger: Logger, workflow_content: str) -> List[ProcessorTask]:
    try:
        tasks_list = workflow_content.splitlines()
        return [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
    except ValueError as error:
        message = "Failed parsing processing tasks from a workflow."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)


async def send_workflow_callback(logger: Logger, workflow_job: DBWorkflowJob, state: JobState) -> bool:
    """Notify the callback URL about a workflow's terminal state."""
    callback_url = workflow_job.workflow_callback_url
    if not callback_url:
        return True
    payload = {"job_id": workflow_job.job_id, "state": state}
    try:
        async with AsyncClient(timeout=Timeout(10.0)) as client:
            response = await client.post(callback_url, json=payload)
            response.raise_for_status()
        logger.info(f"Workflow callback delivered for workflow {workflow_job.job_id} (state={state.value})")
        return True
    except Exception:
        logger.exception(f"Failed to deliver workflow callback for workflow {workflow_job.job_id}")
        return False


def validate_workflow(logger: Logger, workflow: str) -> None:
    """Check whether workflow is not empty and parseable to a list of ProcessorTask objects."""
    if not workflow.strip():
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message="Workflow is invalid, empty.")
    try:
        tasks_list = workflow.splitlines()
        [ProcessorTask.parse(task_str) for task_str in tasks_list if task_str.strip()]
    except ValueError as error:
        message = "Provided workflow script is invalid, failed to parse ProcessorTasks."
        raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message, error)