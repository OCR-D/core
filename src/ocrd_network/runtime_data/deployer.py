"""
Abstraction of the deployment functionality for processors.

The Processing Server provides the configuration parameters to the Deployer agent.
The Deployer agent runs the RabbitMQ Server, MongoDB and the Processing Hosts.
Each Processing Host may have several Processing Workers.
Each Processing Worker is an instance of an OCR-D processor.
"""
from __future__ import annotations
from pathlib import Path
from subprocess import Popen
from time import sleep
from typing import Dict, List, Union

from ocrd_utils import config, getLogger, safe_filename
from ..logging import get_mets_server_logging_file_path
from ..utils import is_mets_server_running, stop_mets_server, validate_and_load_config
from .config_parser import parse_hosts_data, parse_mongodb_data, parse_rabbitmq_data
from .hosts import DataHost
from .network_agents import DeployType
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

    # TODO: Reconsider this.
    def find_matching_processors(
        self,
        worker_only: bool = False,
        server_only: bool = False,
        docker_only: bool = False,
        native_only: bool = False,
        str_names_only: bool = False,
        unique_only: bool = False
    ) -> Union[List[str], List[object]]:
        """Finds and returns a list of matching data objects of type:
        `DataProcessingWorker` and `DataProcessorServer`.

        :py:attr:`worker_only` match only processors with worker status
        :py:attr:`server_only` match only processors with server status
        :py:attr:`docker_only` match only docker processors
        :py:attr:`native_only` match only native processors
        :py:attr:`str_only` returns the processor_name instead of data object
        :py:attr:`unique_only` remove duplicates from the matches

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

        # Find all matching objects of type:
        # DataProcessingWorker or DataProcessorServer
        matched_objects = []
        for data_host in self.data_hosts:
            if not server_only:
                for data_worker in data_host.network_agents_worker:
                    if data_worker.deploy_type == DeployType.NATIVE and docker_only:
                        continue
                    if data_worker.deploy_type == DeployType.DOCKER and native_only:
                        continue
                    matched_objects.append(data_worker)
            if not worker_only:
                for data_server in data_host.network_agents_server:
                    if data_server.deploy_type == DeployType.NATIVE and docker_only:
                        continue
                    if data_server.deploy_type == DeployType.DOCKER and native_only:
                        continue
                    matched_objects.append(data_server)
        if str_names_only:
            # gets only the processor names of the matched objects
            name_list = [match.processor_name for match in matched_objects]
            if unique_only:
                # removes the duplicates, if any
                return list(dict.fromkeys(name_list))
            return name_list
        return matched_objects

    def resolve_processor_server_url(self, processor_name) -> str:
        processor_server_url = ''
        for data_host in self.data_hosts:
            for data_server in data_host.network_agents_server:
                if data_server.processor_name == processor_name:
                    processor_server_url = f"http://{data_host.host}:{data_server.port}/"
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

    # TODO: No support for TCP version yet
    def start_unix_mets_server(self, mets_path: str) -> Path:
        log_file = get_mets_server_logging_file_path(mets_path=mets_path)
        mets_server_url = Path(config.OCRD_NETWORK_SOCKETS_ROOT_DIR, f"{safe_filename(mets_path)}.sock")

        if is_mets_server_running(mets_server_url=str(mets_server_url)):
            self.log.warning(f"The mets server for {mets_path} is already started: {mets_server_url}")
            return mets_server_url

        cwd = Path(mets_path).parent
        self.log.info(f'Starting UDS mets server: {mets_server_url}')
        sub_process = Popen(
            args=['nohup', 'ocrd', 'workspace', '--mets-server-url', f'{mets_server_url}',
                  '-d', f'{cwd}', 'server', 'start'],
            shell=False,
            stdout=open(file=log_file, mode='w'),
            stderr=open(file=log_file, mode='a'),
            cwd=cwd,
            universal_newlines=True
        )
        # Wait for the mets server to start
        sleep(2)
        self.mets_servers[mets_server_url] = sub_process.pid
        return mets_server_url

    def stop_unix_mets_server(self, mets_server_url: str) -> None:
        self.log.info(f'Stopping UDS mets server: {mets_server_url}')
        if Path(mets_server_url) in self.mets_servers:
            mets_server_pid = self.mets_servers[Path(mets_server_url)]
        else:
            msg = f"Mets server not found at URL: {mets_server_url}"
            self.log.exception(msg)
            raise Exception(msg)

        '''
        subprocess.run(
            args=['kill', '-s', 'SIGINT', f'{mets_server_pid}'],
            shell=False,
            universal_newlines=True
        )
        '''

        # TODO: Reconsider this again
        #  Not having this sleep here causes connection errors
        #  on the last request processed by the processing worker.
        #  Sometimes 3 seconds is enough, sometimes not.
        sleep(5)
        stop_mets_server(mets_server_url=mets_server_url)
