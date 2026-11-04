from fastapi import APIRouter
from typing import TYPE_CHECKING

from ocrd_network.constants import ServerApiTags

if TYPE_CHECKING:
    from ..server import ProcessingServer


def create_others_router(server: "ProcessingServer") -> APIRouter:
    router = APIRouter()

    router.add_api_route(
        path="/",
        endpoint=server.home_page,
        methods=["GET"],
        status_code=200,
        summary="Get information about the processing server"
    )

    router.add_api_route(
        path="/user_workflow_callback_test",
        endpoint=server.user_workflow_callback_test,
        methods=["POST"],
        status_code=200,
        summary="Used for testing the user workflow callback mechanism without requiring a separate server"
    )

    router.add_api_route(
        path="/stop",
        endpoint=server.stop_deployed_agents,
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
        endpoint=server.kill_mets_server_zombies,
        methods=["DELETE"],
        tags=[ServerApiTags.WORKFLOW, ServerApiTags.PROCESSING],
        status_code=200,
        summary="!! Workaround Do Not Use Unless You Have A Reason "
                "!! Kill all METS servers on this machine that have been created more than 60 minutes ago."
    )

    return router