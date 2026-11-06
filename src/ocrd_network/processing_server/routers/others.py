from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from logging import Logger
from typing import Dict, TYPE_CHECKING

from ...constants import ServerApiTags
from ..helpers.maintenance import kill_mets_server_zombies


if TYPE_CHECKING:
    from ..server import ProcessingServer


def create_others_router(server: "ProcessingServer", log: Logger) -> APIRouter:
    router = APIRouter()

    async def home_page() -> Dict[str, str]:
        return {
            "message": f"The home page of the {server.title}",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    async def user_workflow_callback_test(request: Request) -> JSONResponse:
        payload = await request.json()
        job_id = payload.get("job_id")
        state = payload.get("state")
        log.info(f"Received test workflow callback: job_id={job_id}, state={state}")
        return JSONResponse(
            status_code=200,
            content={"received": True, "job_id": job_id, "state": state}
        )

    router.add_api_route(
        path="/",
        endpoint=home_page,
        methods=["GET"],
        status_code=200,
        summary="Get information about the processing server"
    )

    router.add_api_route(
        path="/user_workflow_callback_test",
        endpoint=user_workflow_callback_test,
        methods=["POST"],
        status_code=200,
        summary="Used for testing the user workflow callback mechanism without requiring a separate server"
    )

    router.add_api_route(
        path="/stop",
        endpoint=server.on_shutdown,
        methods=["POST"],
        tags=[ServerApiTags.TOOLS],
        summary="Stop database, queue and processing-workers"
    )

    router.add_api_route(
        path="/tcp_mets",
        endpoint=server.forward_tcp_request_to_uds_mets_server,
        methods=["POST"],
        tags=[ServerApiTags.WORKSPACE],
        summary="Forward a TCP request to UDS mets server"
    )

    router.add_api_route(
        path="/kill_mets_server_zombies",
        endpoint=kill_mets_server_zombies,
        methods=["DELETE"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=200,
        summary="!! Workaround Do Not Use Unless You Have A Reason "
                "!! Kill all METS servers on this machine that have been created more than 60 minutes ago."
    )

    return router