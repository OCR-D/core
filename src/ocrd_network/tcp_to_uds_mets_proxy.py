from requests_unixsocket import Session as requests_unixsocket_session
from .utils import get_uds_path

SUPPORTED_METHOD_TYPES = ["GET", "POST", "PUT", "DELETE"]


class MetsServerProxy:
    def __init__(self) -> None:
        self.session: requests_unixsocket_session = requests_unixsocket_session()
        pass

    def forward_tcp_request(self, request_body: dict):
        ws_dir_path = request_body["workspace_path"]
        request_url: str = request_body["request_url"]
        method_type: str = request_body["method_type"]
        request_data: dict = request_body["request_data"]
        if method_type not in SUPPORTED_METHOD_TYPES:
            raise NotImplementedError(f"Method type: {method_type} not recognized")
        uds_root_mets_server = str(get_uds_path(ws_dir_path=ws_dir_path))
        full_request_url = f"{uds_root_mets_server}/{request_url}"
        return self.session.request(method=method_type, url=full_request_url, json=request_data)
