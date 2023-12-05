from pathlib import Path
from ocrd_utils import safe_filename, config

from .constants import NETWORK_AGENT_SERVER, NETWORK_AGENT_WORKER

OCRD_NETWORK_MODULES = [
    "mets_servers",
    "processing_jobs",
    "processing_servers",
    "processing_workers",
    "processor_servers"
]


def get_root_logging_dir(module_name: str) -> Path:
    if module_name not in OCRD_NETWORK_MODULES:
        raise ValueError(f"Invalid module name: {module_name}, should be one of: {OCRD_NETWORK_MODULES}")
    module_log_dir = Path(config.OCRD_NETWORK_LOGS_ROOT_DIR, module_name)
    module_log_dir.mkdir(parents=True, exist_ok=True)
    return module_log_dir


def get_cache_locked_pages_logging_file_path() -> Path:
    return get_root_logging_dir("processing_servers") / "cache_locked_pages.log"


def get_cache_processing_requests_logging_file_path() -> Path:
    return get_root_logging_dir("processing_servers") / "cache_processing_requests.log"


def get_processing_job_logging_file_path(job_id: str) -> Path:
    return get_root_logging_dir("processing_jobs") / f"{job_id}.log"


def get_processing_server_logging_file_path(pid: int) -> Path:
    return get_root_logging_dir("processing_servers") / f"processing_server.{pid}.log"


def get_processing_worker_logging_file_path(processor_name: str, pid: int) -> Path:
    return get_root_logging_dir("processing_workers") / f"{NETWORK_AGENT_WORKER}.{pid}.{processor_name}.log"


def get_processor_server_logging_file_path(processor_name: str, pid: int) -> Path:
    return get_root_logging_dir("processor_servers") / f"{NETWORK_AGENT_SERVER}.{pid}.{processor_name}.log"


def get_mets_server_logging_file_path(mets_path: str) -> Path:
    return get_root_logging_dir("mets_servers") / f"{safe_filename(mets_path)}.log"
