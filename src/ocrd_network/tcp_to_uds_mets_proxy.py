from requests_unixsocket import Session as requests_unixsocket_session
from .utils import get_uds_path

SUPPORTED_METHOD_TYPES = ["GET", "POST", "PUT", "DELETE"]


class MetsServerProxy:
    def __init__(self) -> None:
        self.session: requests_unixsocket_session = requests_unixsocket_session()
        pass

    def forward_tcp_request(self, request_body):
        ws_dir_path: str = request_body["workspace_path"]
        request_url: str = request_body["request_url"]
        method_type: str = request_body["method_type"]
        request_data = request_body["request_data"]
        if method_type not in SUPPORTED_METHOD_TYPES:
            raise NotImplementedError(f"Method type: {method_type} not recognized")
        ws_socket_file = str(get_uds_path(ws_dir_path=ws_dir_path))
        ws_unix_socket_url = f'http+unix://{ws_socket_file.replace("/", "%2F")}'
        uds_request_url = f"{ws_unix_socket_url}/{request_url}"
        return self.session.request(method=method_type, url=uds_request_url, json=request_data)
