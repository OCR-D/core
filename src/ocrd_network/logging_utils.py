from logging import FileHandler, Formatter, Logger
from pathlib import Path

from ocrd_utils import config, LOG_FORMAT, safe_filename
from .constants import AgentType, NetworkLoggingDirs


def configure_file_handler_with_formatter(logger: Logger, log_file: Path, mode: str = "a") -> None:
    file_handler = FileHandler(filename=log_file, mode=mode)
    file_handler.setFormatter(Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)


def get_root_logging_dir(module_name: NetworkLoggingDirs) -> Path:
    module_log_dir = Path(config.OCRD_NETWORK_LOGS_ROOT_DIR, module_name.value)
    module_log_dir.mkdir(parents=True, exist_ok=True)
    return module_log_dir


def get_cache_locked_pages_logging_file_path() -> Path:
    log_file: str = "cache_locked_pages.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.PROCESSING_SERVERS), log_file)


def get_cache_processing_requests_logging_file_path() -> Path:
    log_file: str = "cache_processing_requests.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.PROCESSING_SERVERS), log_file)


def get_mets_server_logging_file_path(mets_path: str) -> Path:
    log_file: str = f"{safe_filename(mets_path)}.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.METS_SERVERS), log_file)


def get_processing_job_logging_file_path(job_id: str) -> Path:
    log_file: str = f"{job_id}.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.PROCESSING_JOBS), log_file)


def get_processing_server_logging_file_path(pid: int) -> Path:
    log_file: str = f"processing_server.{pid}.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.PROCESSING_SERVERS), log_file)


def get_processing_worker_logging_file_path(processor_name: str, pid: int) -> Path:
    log_file: str = f"{AgentType.PROCESSING_WORKER}.{pid}.{processor_name}.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.PROCESSING_WORKERS), log_file)


def get_processor_server_logging_file_path(processor_name: str, pid: int) -> Path:
    log_file: str = f"{AgentType.PROCESSOR_SERVER}.{pid}.{processor_name}.log"
    return Path(get_root_logging_dir(NetworkLoggingDirs.PROCESSOR_SERVERS), log_file)
