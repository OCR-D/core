from requests_unixsocket import Session as requests_unixsocket_session
from .utils import get_uds_path, convert_url_to_uds_format
from typing import Dict
from ocrd_utils import getLogger

SUPPORTED_METHOD_TYPES = ["GET", "POST", "PUT", "DELETE"]


class MetsServerProxy:
    def __init__(self) -> None:
        self.session: requests_unixsocket_session = requests_unixsocket_session()
        self.log = getLogger("ocrd_network.tcp_to_uds_mets_proxy")

    def forward_tcp_request(self, request_body) -> Dict:
        """Forward request to uds mets server

        The caller of the function must know how the request has to be translated.

        `response_type` is the type of data the corresponding uds-mets-server-enpoint returns.

        `request_data` is expected to indicate what type of parameters the corresponding
        uds-mets-server-endpoint accepts. Currently, there are three types: `class` indicates that
        the endpoint's parameter is a single class, `parameter` is used for "common" parameters and
        `form` for form-parameters
        """
        ws_dir_path: str = request_body["workspace_path"]
        request_url: str = request_body["request_url"]
        response_type: str = request_body["response_type"]
        method_type: str = request_body["method_type"]
        request_data = request_body["request_data"]
        if method_type not in SUPPORTED_METHOD_TYPES:
            raise NotImplementedError(f"Method type: {method_type} not recognized")
        ws_socket_file = str(get_uds_path(ws_dir_path=ws_dir_path))
        ws_unix_socket_url = convert_url_to_uds_format(ws_socket_file)
        uds_request_url = f"{ws_unix_socket_url}/{request_url}"

        self.log.info(f"Forwarding TCP mets server request to UDS url: {uds_request_url}")
        self.log.info(f"Forwarding method type {method_type}, request data: {request_data}, "
                      f"expected response type: {response_type}")

        if not request_data:
            response = self.session.request(method_type, uds_request_url)
        elif "params" in request_data:
            response = self.session.request(method_type, uds_request_url, params=request_data["params"])
        elif "form" in request_data:
            response = self.session.request(method_type, uds_request_url, data=request_data["form"])
        elif "class" in request_data:
            response = self.session.request(method_type, uds_request_url, json=request_data["class"])
        else:
            raise ValueError("Expecting request_data to be empty or containing single key: params,"
                             f"form, or class but not {request_data.keys}")
        if response_type == "empty":
            return {}
        if not response:
            self.log.error(f"Uds-Mets-Server gives unexpected error. Response: {response.__dict__}")
            return {"error": response.text}
        elif response_type == "text":
            return {"text": response.text}
        elif response_type == "class" or response_type == "dict":
            return response.json()
        else:
            raise ValueError(f"Unexpected response_type: {response_type}")
