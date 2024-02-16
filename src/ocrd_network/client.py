from json import dumps, loads
from requests import post as requests_post
from ocrd_utils import config, getLogger, LOG_FORMAT

from .constants import NETWORK_PROTOCOLS


# TODO: This is just a conceptual implementation and first try to
#  trigger further discussions on how this should look like.
class Client:
    def __init__(
        self,
        server_addr_processing: str = config.OCRD_NETWORK_SERVER_ADDR_PROCESSING,
        server_addr_workflow: str = config.OCRD_NETWORK_SERVER_ADDR_WORKFLOW,
        server_addr_workspace: str = config.OCRD_NETWORK_SERVER_ADDR_WORKSPACE
    ):
        self.log = getLogger(f"ocrd_network.client")
        self.server_addr_processing = server_addr_processing
        self.server_addr_workflow = server_addr_workflow
        self.server_addr_workspace = server_addr_workspace

    def send_processing_request(self, processor_name: str, req_params: dict):
        verify_server_protocol(self.server_addr_processing)
        req_url = f"{self.server_addr_processing}/processor/{processor_name}"
        req_headers = {"Content-Type": "application/json; charset=utf-8"}
        req_json = loads(dumps(req_params))
        self.log.info(f"Sending processing request to: {req_url}")
        self.log.debug(req_json)
        response = requests_post(url=req_url, headers=req_headers, json=req_json)
        return response.json()


def verify_server_protocol(address: str):
    for protocol in NETWORK_PROTOCOLS:
        if address.startswith(protocol):
            return
    raise ValueError(f"Wrong/Missing protocol in the server address: {address}, must be one of: {NETWORK_PROTOCOLS}")
