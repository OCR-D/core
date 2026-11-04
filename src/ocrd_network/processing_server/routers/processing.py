from fastapi import APIRouter, status

from ocrd_network.constants import ServerApiTags
from ocrd_network.models import PYJobOutput

from ..services.coordinator import ProcessingCoordinator
from ..services.processing import ProcessingService
from ..services.workspace import WorkspaceService


def create_processing_router(
    processing_service: ProcessingService,
    processing_coordinator: ProcessingCoordinator,
    workspace_service: WorkspaceService,
) -> APIRouter:
    router = APIRouter()

    router.add_api_route(
        path="/processor",
        endpoint=processing_service.list_processors,
        methods=["GET"],
        tags=[ServerApiTags.PROCESSING, ServerApiTags.DISCOVERY],
        status_code=status.HTTP_200_OK,
        summary="Get a list of all available processors",
    )
    router.add_api_route(
        path="/processor/info/{processor_name}",
        endpoint=processing_service.get_worker_ocrd_tool,
        methods=["GET"],
        tags=[ServerApiTags.PROCESSING, ServerApiTags.DISCOVERY],
        status_code=status.HTTP_200_OK,
        summary="Get information about this processor",
    )
    router.add_api_route(
        path="/processor/run/{processor_name}",
        endpoint=processing_coordinator.validate_and_forward_job_to_worker,
        methods=["POST"],
        tags=[ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Submit a job to this processor",
        response_model=PYJobOutput,
        response_model_exclude_unset=True,
        response_model_exclude_none=True,
    )
    router.add_api_route(
        path="/processor/job/{job_id}",
        endpoint=processing_service.get_processor_job,
        methods=["GET"],
        tags=[ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Get information about a job based on its ID",
        response_model=PYJobOutput,
        response_model_exclude_unset=True,
        response_model_exclude_none=True,
    )
    router.add_api_route(
        path="/processor/log/{job_id}",
        endpoint=processing_service.get_processor_job_log,
        methods=["GET"],
        tags=[ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Get the log file of a job id",
    )
    router.add_api_route(
        path="/result_callback",
        endpoint=workspace_service.remove_job_from_request_cache,
        methods=["POST"],
        tags=[ServerApiTags.PROCESSING],
        status_code=status.HTTP_200_OK,
        summary="Callback used by a worker for reporting result of a processing request",
    )

    return router