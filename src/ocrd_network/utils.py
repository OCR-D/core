from asyncio import iscoroutine, get_event_loop
from datetime import datetime
from fastapi import UploadFile
from functools import wraps
from hashlib import md5
from pathlib import Path
from re import compile as re_compile, split as re_split
from requests import get as requests_get, Session as Session_TCP
from requests_unixsocket import Session as Session_UDS
from time import sleep
from typing import List
from uuid import uuid4

from ocrd.resolver import Resolver
from ocrd.workspace import Workspace
from ocrd.mets_server import MpxReq
from ocrd_utils import config, generate_range, REGEX_PREFIX, safe_filename, getLogger
from .rabbitmq_utils import OcrdResultMessage


def call_sync(func):
    # Based on: https://gist.github.com/phizaz/20c36c6734878c6ec053245a477572ec
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if iscoroutine(result):
            return get_event_loop().run_until_complete(result)
        return result
    return func_wrapper


def calculate_execution_time(start: datetime, end: datetime) -> int:
    """
    Calculates the difference between 'start' and 'end' datetime.
    Returns the result in milliseconds
    """
    return int((end - start).total_seconds() * 1000)


def calculate_processing_request_timeout(amount_pages: int, timeout_per_page: float = 20.0) -> float:
    return amount_pages * timeout_per_page


def convert_url_to_uds_format(url: str) -> str:
    return f"http+unix://{url.replace('/', '%2F')}"


def expand_page_ids(page_id: str) -> List:
    page_ids = []
    if not page_id:
        return page_ids
    for page_id_token in re_split(pattern=r',', string=page_id):
        if page_id_token.startswith(REGEX_PREFIX):
            page_ids.append(re_compile(pattern=page_id_token[len(REGEX_PREFIX):]))
        elif '..' in page_id_token:
            page_ids += generate_range(*page_id_token.split(sep='..', maxsplit=1))
        else:
            page_ids += [page_id_token]
    return page_ids


def generate_created_time() -> int:
    return int(datetime.utcnow().timestamp())


def generate_id() -> str:
    """
    Generate the id to be used for processing job ids.
    Note, workspace_id and workflow_id in the reference
    WebAPI implementation are produced in the same manner
    """
    return str(uuid4())


async def generate_workflow_content(workflow: UploadFile, encoding: str = "utf-8"):
    return (await workflow.read()).decode(encoding)


def generate_workflow_content_hash(workflow_content: str, encoding: str = "utf-8"):
    return md5(workflow_content.encode(encoding)).hexdigest()


def is_url_responsive(url: str, tries: int = 1, wait_time: int = 3) -> bool:
    while tries > 0:
        try:
            if requests_get(url).status_code == 200:
                return True
        except Exception:
            continue
        sleep(wait_time)
        tries -= 1
    return False


def download_ocrd_all_tool_json(ocrd_all_url: str):
    if not ocrd_all_url:
        raise ValueError(f"The URL of ocrd all tool json is empty")
    headers = {"Accept": "application/json"}
    response = Session_TCP().get(ocrd_all_url, headers=headers)
    if not response.status_code == 200:
        raise ValueError(f"Failed to download ocrd all tool json from: '{ocrd_all_url}'")
    return response.json()


def post_to_callback_url(logger, callback_url: str, result_message: OcrdResultMessage):
    logger.info(f'Posting result message to callback_url "{callback_url}"')
    headers = {"Content-Type": "application/json"}
    json_data = {
        "job_id": result_message.job_id,
        "state": result_message.state,
        "path_to_mets": result_message.path_to_mets,
        "workspace_id": result_message.workspace_id
    }
    response = Session_TCP().post(url=callback_url, headers=headers, json=json_data)
    logger.info(f'Response from callback_url "{response}"')


def get_ocrd_workspace_instance(mets_path: str, mets_server_url: str = None) -> Workspace:
    if mets_server_url:
        if not is_mets_server_running(mets_server_url=mets_server_url, ws_dir_path=str(Path(mets_path).parent)):
            raise RuntimeError(f'The mets server is not running: {mets_server_url}')
    return Resolver().workspace_from_url(mets_url=mets_path, mets_server_url=mets_server_url)


def get_ocrd_workspace_physical_pages(mets_path: str, mets_server_url: str = None) -> List[str]:
    return get_ocrd_workspace_instance(mets_path=mets_path, mets_server_url=mets_server_url).mets.physical_pages


def is_mets_server_running(mets_server_url: str, ws_dir_path: str = None) -> bool:
    protocol = "tcp" if (mets_server_url.startswith("http://") or mets_server_url.startswith("https://")) else "uds"
    session = Session_TCP() if protocol == "tcp" else Session_UDS()
    if protocol == "uds":
        mets_server_url = convert_url_to_uds_format(mets_server_url)
    try:
        if 'tcp_mets' in mets_server_url:
            if not ws_dir_path:
                return False
            path = session.post(
                url=f"{mets_server_url}",
                json=MpxReq.workspace_path(ws_dir_path)
            ).json()["text"]
            return bool(path)
        else:
            try:
                response = session.get(url=f"{mets_server_url}/workspace_path")
                return response.status_code == 200
            except OSError:
                return False
    except Exception:
        getLogger("ocrd_network.utils").exception("Unexpected exception in is_mets_server_running: ")
        return False


def stop_mets_server(mets_server_url: str, ws_dir_path: str = None) -> bool:
    protocol = "tcp" if (mets_server_url.startswith("http://") or mets_server_url.startswith("https://")) else "uds"
    session = Session_TCP() if protocol == "tcp" else Session_UDS()
    if protocol == "uds":
        mets_server_url = convert_url_to_uds_format(mets_server_url)
    try:
        if 'tcp_mets' in mets_server_url:
            if not ws_dir_path:
                return False
            response = session.post(url=f"{mets_server_url}", json=MpxReq.stop(ws_dir_path))
        else:
            response = session.delete(url=f"{mets_server_url}/")
    except Exception:
        return False
    return response.status_code == 200


def get_uds_path(ws_dir_path: str) -> Path:
    return Path(config.OCRD_NETWORK_SOCKETS_ROOT_DIR, f"{safe_filename(ws_dir_path)}.sock")
