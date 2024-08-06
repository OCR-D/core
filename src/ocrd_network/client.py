from json import dumps, loads
from requests import post as requests_post
from ocrd_utils import config, getLogger, LOG_FORMAT

from .constants import NETWORK_PROTOCOLS


class Client:
    def __init__(self, server_addr_processing: str = config.OCRD_NETWORK_SERVER_ADDR_PROCESSING):
        self.log = getLogger(f"ocrd_network.client")
        self.server_addr_processing = server_addr_processing
        verify_server_protocol(self.server_addr_processing)

    def send_processing_request(self, processor_name: str, req_params: dict):
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
