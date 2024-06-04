"""
Abstraction of the deployment functionality for processors.

The Processing Server provides the configuration parameters to the Deployer agent.
The Deployer agent runs the RabbitMQ Server, MongoDB and the Processing Hosts.
Each Processing Host may have several Processing Workers.
Each Processing Worker is an instance of an OCR-D processor.
"""
from __future__ import annotations
from pathlib import Path
from subprocess import Popen, run as subprocess_run
from time import sleep
from typing import Dict, List, Union

from ocrd import OcrdMetsServer
from ocrd_utils import config, getLogger, safe_filename
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
        self.use_tcp_mets = ps_config.get("use_tcp_mets", False)

    # TODO: Reconsider this.
    def find_matching_network_agents(
        self, worker_only: bool = False, server_only: bool = False, docker_only: bool = False,
        native_only: bool = False, str_names_only: bool = False, unique_only: bool = False
    ) -> Union[List[str], List[object]]:
        """Finds and returns a list of matching data objects of type:
        `DataProcessingWorker` and `DataProcessorServer`.

        :py:attr:`worker_only` match only worker network agents (DataProcessingWorker)
        :py:attr:`server_only` match only server network agents (DataProcessorServer)
        :py:attr:`docker_only` match only docker network agents (DataProcessingWorker and DataProcessorServer)
        :py:attr:`native_only` match only native network agents (DataProcessingWorker and DataProcessorServer)
        :py:attr:`str_names_only` returns the processor_name filed instead of the Data* object
        :py:attr:`unique_only` remove duplicate names from the matches

        `worker_only` and `server_only` are mutually exclusive to each other
        `docker_only` and `native_only` are mutually exclusive to each other
        `unique_only` is allowed only together with `str_names_only`
        """

        if worker_only and server_only:
            msg = f"Only 'worker_only' or 'server_only' is allowed, not both."
            self.log.exception(msg)
            raise ValueError(msg)
        if docker_only and native_only:
            msg = f"Only 'docker_only' or 'native_only' is allowed, not both."
            self.log.exception(msg)
            raise ValueError(msg)
        if not str_names_only and unique_only:
            msg = f"Value 'unique_only' is allowed only together with 'str_names_only'"
            self.log.exception(msg)
            raise ValueError(msg)

        # Find all matching objects of type DataProcessingWorker or DataProcessorServer
        matched_objects = []
        for data_host in self.data_hosts:
            if not server_only:
                if not docker_only:
                    for data_worker in data_host.network_agents_worker_native:
                        matched_objects.append(data_worker)
                if not native_only:
                    for data_worker in data_host.network_agents_worker_docker:
                        matched_objects.append(data_worker)
            if not worker_only:
                if not docker_only:
                    for data_server in data_host.network_agents_server_native:
                        matched_objects.append(data_server)
                if not native_only:
                    for data_server in data_host.network_agents_server_docker:
                        matched_objects.append(data_server)
        if not str_names_only:
            return matched_objects
        # Gets only the processor names of the matched objects
        matched_names = [match.processor_name for match in matched_objects]
        if not unique_only:
            return matched_names
        # Removes any duplicate entries from matched names
        return list(dict.fromkeys(matched_names))

    def resolve_processor_server_url(self, processor_name) -> str:
        processor_server_url = ''
        for data_host in self.data_hosts:
            processor_server_url = data_host.resolve_processor_server_url(processor_name=processor_name)
        return processor_server_url

    def deploy_network_agents(self, mongodb_url: str, rabbitmq_url: str) -> None:
        self.log.debug("Deploying processing workers/processor servers...")
        for host_data in self.data_hosts:
            host_data.deploy_network_agents(logger=self.log, mongodb_url=mongodb_url, rabbitmq_url=rabbitmq_url)

    def stop_network_agents(self) -> None:
        self.log.debug("Stopping processing workers/processor servers...")
        for host_data in self.data_hosts:
            host_data.stop_network_agents(logger=self.log)

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
        self.stop_network_agents()
        self.stop_mongodb()
        self.stop_rabbitmq()

    def start_uds_mets_server(self, ws_dir_path: str) -> Path:
        log_file = get_mets_server_logging_file_path(mets_path=ws_dir_path)
        mets_server_url = get_uds_path(ws_dir_path=ws_dir_path)
        if is_mets_server_running(mets_server_url=str(mets_server_url)):
            self.log.debug(f"The UDS mets server for {ws_dir_path} is already started: {mets_server_url}")
            return mets_server_url
        self.log.info(f"Starting UDS mets server: {mets_server_url}")
        pid = OcrdMetsServer.create_process(mets_server_url=mets_server_url, ws_dir_path=ws_dir_path, log_file=log_file)
        self.mets_servers[mets_server_url] = pid
        return mets_server_url

    def stop_uds_mets_server(self, mets_server_url: str, stop_with_pid: bool = False) -> None:
        self.log.info(f"Stopping UDS mets server: {mets_server_url}")
        if stop_with_pid:
            if Path(mets_server_url) not in self.mets_servers:
                message = f"UDS Mets server not found at URL: {mets_server_url}"
                self.log.exception(message)
                raise Exception(message)
            mets_server_pid = self.mets_servers[Path(mets_server_url)]
            OcrdMetsServer.kill_process(mets_server_pid=mets_server_pid)
            return
        # TODO: Reconsider this again
        #  Not having this sleep here causes connection errors
        #  on the last request processed by the processing worker.
        #  Sometimes 3 seconds is enough, sometimes not.
        sleep(5)
        stop_mets_server(mets_server_url=mets_server_url)
        return
