from fastapi import APIRouter, status
from typing import TYPE_CHECKING

from ocrd_network.constants import ServerApiTags
from ocrd_network.models import PYWorkflowJobOutput

if TYPE_CHECKING:
    from ..server import ProcessingServer


def create_workflow_router(server: "ProcessingServer") -> APIRouter:
    router = APIRouter()

    router.add_api_route(
        path="/workflow",
        endpoint=server.upload_workflow,
        methods=["POST"],
        tags=[ServerApiTags.WORKFLOW],
        status_code=status.HTTP_201_CREATED,
        summary="Upload/Register a new workflow script"
    )
    router.add_api_route(
        path="/workflow/{workflow_id}",
        endpoint=server.download_workflow,
        methods=["GET"],
        tags=[ServerApiTags.WORKFLOW],
        status_code=status.HTTP_200_OK,
        summary="Download a workflow script"
    )
    router.add_api_route(
        path="/workflow/{workflow_id}",
        endpoint=server.replace_workflow,
        methods=["PUT"],
        tags=[ServerApiTags.WORKFLOW],
        status_code=status.HTTP_200_OK,
        summary="Update/Replace a workflow script"
    )
    router.add_api_route(
        path="/workflow/run",
        endpoint=server.run_workflow,
        methods=["POST"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Run a workflow",
        response_model=PYWorkflowJobOutput,
        response_model_exclude_defaults=True,
        response_model_exclude_unset=True,
        response_model_exclude_none=True
    )
    router.add_api_route(
        path="/workflow/job-simple/{workflow_job_id}",
        endpoint=server.get_workflow_info_simple,
        methods=["GET"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Get simplified overall job status"
    )
    router.add_api_route(
        path="/workflow/job/{workflow_job_id}",
        endpoint=server.get_workflow_info,
        methods=["GET"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Get information about a workflow run"
    )

    return router