from pathlib import Path
from src.ocrd_network.constants import NetworkLoggingDirs
from src.ocrd_network.logging_utils import (
    get_root_logging_dir
)
from tests.network.config import test_config

OCRD_NETWORK_LOGS_ROOT_DIR = test_config.OCRD_NETWORK_LOGS_ROOT_DIR


def root_logging_dir(module_name: NetworkLoggingDirs):
    func_result = get_root_logging_dir(module_name=module_name)
    expected_result = Path(OCRD_NETWORK_LOGS_ROOT_DIR, module_name)
    assert func_result == expected_result, f"Mismatch in root logging dir of module: {module_name}"


def test_root_logging_dir_mets_servers():
    root_logging_dir(module_name=NetworkLoggingDirs.METS_SERVERS)


def test_root_logging_dir_processor_servers():
    root_logging_dir(module_name=NetworkLoggingDirs.PROCESSOR_SERVERS)


def test_root_logging_dir_processing_workers():
    root_logging_dir(module_name=NetworkLoggingDirs.PROCESSING_WORKERS)


def test_root_logging_dir_processing_servers():
    root_logging_dir(module_name=NetworkLoggingDirs.PROCESSING_SERVERS)


def test_root_logging_dir_processing_jobs():
    root_logging_dir(module_name=NetworkLoggingDirs.PROCESSING_JOBS)
