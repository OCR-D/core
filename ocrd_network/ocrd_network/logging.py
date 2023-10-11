from os import makedirs
from os.path import join
from ocrd_utils import safe_filename

OCRD_NETWORK_MODULES = [
    "mets_servers",
    "processing_jobs",
    "processing_servers",
    "processing_workers",
    "processor_servers"
]


def get_root_logging_dir(module_name: str) -> str:
    if module_name not in OCRD_NETWORK_MODULES:
        raise ValueError(f"Invalid module name: {module_name}, should be one of: {OCRD_NETWORK_MODULES}")
    # TODO: Utilize env variable to set the root
    module_log_dir = join("/tmp/ocrd_network_logs", module_name)
    makedirs(name=module_log_dir, exist_ok=True)
    return module_log_dir


def get_cache_locked_pages_logging_file_path() -> str:
    return join(get_root_logging_dir("processing_servers"), f"cache_locked_pages.log")


def get_cache_processing_requests_logging_file_path() -> str:
    return join(get_root_logging_dir("processing_servers"), f"cache_processing_requests.log")


def get_processing_job_logging_file_path(job_id: str) -> str:
    return join(get_root_logging_dir("processing_jobs"), f"{job_id}.log")


def get_processing_server_logging_file_path(pid: int) -> str:
    return join(get_root_logging_dir("processing_servers"), f"server.{pid}.log")


def get_processing_worker_logging_file_path(processor_name: str, pid: int) -> str:
    return join(get_root_logging_dir("processing_workers"), f"worker.{pid}.{processor_name}.log")


def get_processor_server_logging_file_path(processor_name: str, pid: int) -> str:
    return join(get_root_logging_dir("processor_servers"), f"server.{pid}.{processor_name}.log")


def get_mets_server_logging_file_path(mets_path: str) -> str:
    return join(get_root_logging_dir("mets_servers"), f"{safe_filename(mets_path)}.log")
