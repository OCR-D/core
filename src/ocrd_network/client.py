import json
import requests

from ocrd_utils import config


# TODO: This is just a conceptual implementation and first try to
#  trigger further discussions on how this should look like.
class Client:
    def __init__(
            self,
            server_addr_processing: str = config.OCRD_NETWORK_SERVER_ADDR_PROCESSING,
            server_addr_workflow: str = config.OCRD_NETWORK_SERVER_ADDR_WORKFLOW,
            server_addr_workspace: str = config.OCRD_NETWORK_SERVER_ADDR_WORKSPACE,
    ):
        self.server_addr_processing = server_addr_processing
        self.server_addr_workflow = server_addr_workflow
        self.server_addr_workspace = server_addr_workspace

    def send_processing_request(self, processor_name: str, req_params: dict):
        verify_server_protocol(self.server_addr_processing)
        req_url = f'{self.server_addr_processing}/processor/{processor_name}'
        req_headers = {"Content-Type": "application/json; charset=utf-8"}
        req_json = json.loads(json.dumps(req_params))

        print(f'Sending processing request to: {req_url}')
        response = requests.post(url=req_url, headers=req_headers, json=req_json)
        return response.json()


def verify_server_protocol(address: str):
    protocol_matched = False
    for protocol in ['http://', 'https://']:
        if address.startswith(protocol):
            protocol_matched = True
            break
    if not protocol_matched:
        raise ValueError(f'Wrong/Missing protocol in the server address: {address}')
