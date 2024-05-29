from requests_unixsocket import Session as requests_unixsocket_session
from .utils import get_uds_path
from typing import Dict

SUPPORTED_METHOD_TYPES = ["GET", "POST", "PUT", "DELETE"]


class MetsServerProxy:
    def __init__(self) -> None:
        self.session: requests_unixsocket_session = requests_unixsocket_session()
        pass

    def forward_tcp_request(self, request_body) -> Dict:
        ws_dir_path: str = request_body["workspace_path"]
        request_url: str = request_body["request_url"]
        response_type: str = request_body["response_type"]
        method_type: str = request_body["method_type"]
        request_data = request_body["request_data"]
        if method_type not in SUPPORTED_METHOD_TYPES:
            raise NotImplementedError(f"Method type: {method_type} not recognized")
        ws_socket_file = str(get_uds_path(ws_dir_path=ws_dir_path))
        ws_unix_socket_url = f'http+unix://{ws_socket_file.replace("/", "%2F")}'
        uds_request_url = f"{ws_unix_socket_url}/{request_url}"

        if method_type == "GET":
            response = self.session.request(method=method_type, url=uds_request_url, params=request_data)
        else:
            response = self.session.request(method=method_type, url=uds_request_url, json=request_data)

        if response_type == "empty":
            return {}
        elif response_type == "text":
            return {"text": response.text}
        elif response_type == "class" or response_type == "dict":
            return response.json()
        else:
            raise ValueError(f"Unexpected response_type: {response_type}")
