"""
Abstraction of the deployment functionality for processors.

The Processing Server provides the configuration parameters to the Deployer agent.
The Deployer agent runs the RabbitMQ Server, MongoDB and the Processing Hosts.
Each Processing Host may have several Processing Workers.
Each Processing Worker is an instance of an OCR-D processor.
"""
from __future__ import annotations
from pathlib import Path
import psutil
from typing import Dict, List

from ocrd import OcrdMetsServer
from ocrd_utils import getLogger
from ..logging_utils import get_mets_server_logging_file_path
from ..utils import get_uds_path, is_mets_server_running, stop_mets_server
from .config_parser import parse_hosts_data, parse_mongodb_data, parse_rabbitmq_data, validate_and_load_config
from .hosts import DataHost
from .network_services import DataMongoDB, DataRabbitMQ


class Deployer:
    def __init__(self, config_path: str) -> None:
        self.log = getLogger("ocrd_network.deployer")
        ps_config = validate_and_load_config(config_path)
        self.data_mongo: DataMongoDB = parse_mongodb_data(ps_config["database"])
        self.data_queue: DataRabbitMQ = parse_rabbitmq_data(ps_config["process_queue"])
        self.data_hosts: List[DataHost] = parse_hosts_data(ps_config["hosts"])
        self.internal_callback_url = ps_config.get("internal_callback_url", None)
        self.mets_servers: Dict = {}  # {"mets_server_url": "mets_server_pid"}
        # This is required to store UDS urls that are multiplexed through the TCP proxy and are not preserved anywhere
        self.mets_servers_paths: Dict = {}  # {"ws_dir_path": "mets_server_url"}
        self.use_tcp_mets = ps_config.get("use_tcp_mets", False)

    def deploy_workers(self, mongodb_url: str, rabbitmq_url: str) -> None:
        self.log.debug("Deploying processing workers...")
        for host_data in self.data_hosts:
            host_data.deploy_workers(logger=self.log, mongodb_url=mongodb_url, rabbitmq_url=rabbitmq_url)

    def stop_workers(self) -> None:
        self.log.debug("Stopping processing workers...")
        for host_data in self.data_hosts:
            host_data.stop_workers(logger=self.log)

    def deploy_rabbitmq(self) -> str:
        self.data_queue.deploy_rabbitmq(self.log)
        return self.data_queue.service_url

    def stop_rabbitmq(self):
        self.data_queue.stop_service_rabbitmq(self.log)

    def deploy_mongodb(self) -> str:
        self.data_mongo.deploy_mongodb(self.log)
        return self.data_mongo.service_url

    def stop_mongodb(self):
        self.data_mongo.stop_service_mongodb(self.log)

    def stop_all(self) -> None:
        """
        The order of stopping is important to optimize graceful shutdown in the future.
        If RabbitMQ server is stopped before stopping Processing Workers that may have
        a bad outcome and leave Processing Workers in an unpredictable state.
        """
        self.stop_workers()
        self.stop_mongodb()
        self.stop_rabbitmq()

    def start_uds_mets_server(self, ws_dir_path: str) -> Path:
        log_file = get_mets_server_logging_file_path(mets_path=ws_dir_path)
        mets_server_url = get_uds_path(ws_dir_path=ws_dir_path)
        if is_mets_server_running(mets_server_url=str(mets_server_url)):
            self.log.debug(f"The UDS mets server for {ws_dir_path} is already started: {mets_server_url}")
            return mets_server_url
        elif Path(mets_server_url).is_socket():
            self.log.warning(
                f"The UDS mets server for {ws_dir_path} is not running but the socket file exists: {mets_server_url}."
                "Removing to avoid any weird behavior before starting the server.")
            Path(mets_server_url).unlink()
        self.log.info(f"Starting UDS mets server: {mets_server_url}")
        pid = OcrdMetsServer.create_process(mets_server_url=str(mets_server_url),
                                            ws_dir_path=str(ws_dir_path),
                                            log_file=str(log_file))
        self.mets_servers[str(mets_server_url)] = pid
        self.mets_servers_paths[str(ws_dir_path)] = str(mets_server_url)
        return mets_server_url

    def stop_uds_mets_server(self, mets_server_url: str, path_to_mets: str) -> None:
        self.log.info(f"Stopping UDS mets server: {mets_server_url}")
        self.log.info(f"Path to the mets file: {path_to_mets}")
        self.log.debug(f"mets_server: {self.mets_servers}")
        self.log.debug(f"mets_server_paths: {self.mets_servers_paths}")
        workspace_path = str(Path(path_to_mets).parent)
        mets_server_url_uds = self.mets_servers_paths[workspace_path]
        mets_server_pid = self.mets_servers[mets_server_url_uds]
        self.log.info(f"Terminating mets server with pid: {mets_server_pid}")
        p = psutil.Process(mets_server_pid)
        stop_mets_server(self.log, mets_server_url=mets_server_url, ws_dir_path=workspace_path)
        if p.is_running():
            p.wait()
            self.log.info(f"Terminated mets server with pid: {mets_server_pid}")
        else:
            self.log.info(f"Mets server with pid: {mets_server_pid} has already terminated.")
        del self.mets_servers_paths[workspace_path]
        del self.mets_servers[mets_server_url_uds]
        return
