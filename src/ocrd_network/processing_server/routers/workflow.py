from fastapi import APIRouter, status

from ...constants import ServerApiTags
from ...models import PYWorkflowJobOutput

from ..services.workflow import WorkflowService


def create_workflow_router(workflow_service: WorkflowService) -> APIRouter:
    router = APIRouter()

    router.add_api_route(
        path="/workflow",
        endpoint=workflow_service.upload_workflow,
        methods=["POST"],
        tags=[ServerApiTags.WORKFLOW],
        status_code=status.HTTP_201_CREATED,
        summary="Upload/Register a new workflow script",
    )
    router.add_api_route(
        path="/workflow/{workflow_id}",
        endpoint=workflow_service.download_workflow,
        methods=["GET"],
        tags=[ServerApiTags.WORKFLOW],
        status_code=status.HTTP_200_OK,
        summary="Download a workflow script",
    )
    router.add_api_route(
        path="/workflow/{workflow_id}",
        endpoint=workflow_service.replace_workflow,
        methods=["PUT"],
        tags=[ServerApiTags.WORKFLOW],
        status_code=status.HTTP_200_OK,
        summary="Update/Replace a workflow script",
    )
    router.add_api_route(
        path="/workflow/run",
        endpoint=workflow_service.run_workflow,
        methods=["POST"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Run a workflow",
        response_model=PYWorkflowJobOutput,
        response_model_exclude_defaults=True,
        response_model_exclude_unset=True,
        response_model_exclude_none=True,
    )
    router.add_api_route(
        path="/workflow/job-simple/{workflow_job_id}",
        endpoint=workflow_service.get_workflow_info_simple,
        methods=["GET"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Get simplified overall job status",
    )
    router.add_api_route(
        path="/workflow/job/{workflow_job_id}",
        endpoint=workflow_service.get_workflow_info,
        methods=["GET"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Get information about a workflow run",
    )

    return router