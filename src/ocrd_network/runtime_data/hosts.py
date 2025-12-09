from logging import Logger
from typing import Dict, List, Optional

from docker import APIClient
from paramiko import SSHClient

from ..constants import RESOURCE_MANAGER_SERVER_PORT
from .connection_clients import CustomDockerClient, create_docker_client, create_ssh_client
from .network_agents import (
    DataProcessingWorker, DeployType, deploy_agent_native_get_pid_hack)


class DataHost:
    def __init__(
        self, host: str, username: str, password: str, keypath: str, workers: List[Dict], servers: List[Dict]
    ) -> None:
        self.host = host
        self.resource_manager_port = RESOURCE_MANAGER_SERVER_PORT
        self.resource_manager_pid = None
        self.username = username
        self.password = password
        self.keypath = keypath

        # These flags are used to track whether a connection of the specified
        # type should be created based on the received config file
        self.needs_ssh_connector: bool = False
        self.needs_docker_connector: bool = False

        # Connection clients, ssh for native deployment, docker for docker deployment
        self.ssh_client = None
        self.docker_client: Optional[CustomDockerClient] = None

        # Lists of network agents based on their agent and deployment type
        self.workers_native: List[DataProcessingWorker] = []
        self.workers_docker: List[DataProcessingWorker] = []

        if not workers:
            workers = []
        if not servers:
            servers = []

        self.__parse_workers(processing_workers=workers)

    def __append_workers_to_lists(self, worker_data: DataProcessingWorker) -> None:
        if worker_data.deploy_type != DeployType.DOCKER and worker_data.deploy_type != DeployType.NATIVE:
            raise ValueError(f"Processing Worker deploy type is unknown: {worker_data.deploy_type}")

        if worker_data.deploy_type == DeployType.NATIVE:
            self.needs_ssh_connector = True
            self.workers_native.append(worker_data)
        if worker_data.deploy_type == DeployType.DOCKER:
            self.needs_docker_connector = True
            self.workers_docker.append(worker_data)

    def __parse_workers(self, processing_workers: List[Dict]):
        for worker in processing_workers:
            worker_data = DataProcessingWorker(
                processor_name=worker["name"], deploy_type=worker.get("deploy_type", "native"),
                host=self.host, init_by_config=True, pid=None
            )
            for _ in range(int(worker["number_of_instance"])):
                self.__append_workers_to_lists(worker_data=worker_data)

    def create_connection_client(self, client_type: str):
        if client_type not in ["docker", "ssh"]:
            raise ValueError(f"Host client type cannot be of type: {client_type}")
        if client_type == "ssh":
            self.ssh_client = create_ssh_client(self.host, self.username, self.password, self.keypath)
            return self.ssh_client
        if client_type == "docker":
            self.docker_client = create_docker_client(self.host, self.username, self.password, self.keypath)
            return self.docker_client

    def __deploy_network_agent_resource_manager_server(self, logger: Logger):
        logger.info(f"Deploying resource manager server on host: {self.host}:{self.resource_manager_port}")
        start_cmd = f"ocrd network resmgr-server --address {self.host}:{self.resource_manager_port} &"
        pid = deploy_agent_native_get_pid_hack(logger, self.ssh_client, start_cmd)
        logger.info(f"Deployed: OCR-D Resource Manager Server [{pid}]: {self.host}:{self.resource_manager_port}")
        self.resource_manager_pid = pid

    def __deploy_single_worker(
        self, logger: Logger, worker_data: DataProcessingWorker,
        mongodb_url: str, rabbitmq_url: str
    ) -> None:
        deploy_type = worker_data.deploy_type
        name = worker_data.processor_name
        worker_info = f"Processing Worker, deploy: {deploy_type}, name: {name}, host: {self.host}"
        logger.info(f"Deploying {worker_info}")

        connection_client = None
        if deploy_type == DeployType.NATIVE:
            assert self.ssh_client, "SSH client connection missing."
            connection_client = self.ssh_client
        if deploy_type == DeployType.DOCKER:
            assert self.docker_client, "Docker client connection missing."
            connection_client = self.docker_client

        worker_data.deploy_network_agent(logger, connection_client, mongodb_url, rabbitmq_url)

    def __deploy_all_workers(self, logger: Logger, mongodb_url: str, rabbitmq_url: str):
        logger.info(f"Deploying processing workers on host: {self.host}")
        amount_workers = len(self.workers_native) + len(self.workers_docker)
        if not amount_workers:
            logger.info("No processing workers found to be deployed")
        for data_worker in self.workers_native:
            self.__deploy_single_worker(logger, data_worker, mongodb_url, rabbitmq_url)
            logger.info(f"Deployed: {data_worker}")
        for data_worker in self.workers_docker:
            self.__deploy_single_worker(logger, data_worker, mongodb_url, rabbitmq_url)
            logger.info(f"Deployed: {data_worker}")

    def deploy_workers(self, logger: Logger, mongodb_url: str, rabbitmq_url: str) -> None:
        if self.needs_ssh_connector and not self.ssh_client:
            logger.debug("Creating missing ssh connector before deploying")
            client = self.create_connection_client(client_type="ssh")
            assert isinstance(client, SSHClient)
            self.ssh_client = client
        if self.needs_docker_connector:
            logger.debug("Creating missing docker connector before deploying")
            client = self.create_connection_client(client_type="docker")
            assert isinstance(client, CustomDockerClient)
            self.docker_client = client

        self.__deploy_network_agent_resource_manager_server(logger)
        self.__deploy_all_workers(logger=logger, mongodb_url=mongodb_url, rabbitmq_url=rabbitmq_url)

        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None

    def __stop_network_agent_resource_manager_server(self, logger: Logger):
        logger.info(f"Stopping OCR-D Resource Manager Server [{self.resource_manager_pid}]: "
                    f"{self.host}:{self.resource_manager_port}")
        assert self.ssh_client, "SSH client connection missing"
        self.ssh_client.exec_command(f"kill {self.resource_manager_pid}")

    def __stop_worker(self, logger: Logger, name: str, deploy_type: DeployType, pid: str):
        worker_info = f"Processing Worker: deploy: {deploy_type}, name: {name}"
        if not pid:
            logger.warning(f"No pid was passed for {worker_info}")
            return
        worker_info += f", pid: {pid}"
        logger.info(f"Stopping {worker_info}")
        if deploy_type == DeployType.NATIVE:
            assert self.ssh_client, "SSH client connection missing"
            self.ssh_client.exec_command(f"kill {pid}")
        if deploy_type == DeployType.DOCKER:
            assert self.docker_client, "Docker client connection missing"
            self.docker_client.containers.get(pid).stop()

    def stop_workers(self, logger: Logger):
        if self.needs_ssh_connector and not self.ssh_client:
            logger.debug("Creating missing ssh connector before stopping")
            client = self.create_connection_client(client_type="ssh")
            assert isinstance(client, SSHClient)
            self.ssh_client = client
        if self.needs_docker_connector and not self.docker_client:
            logger.debug("Creating missing docker connector before stopping")
            client = self.create_connection_client(client_type="docker")
            assert isinstance(client, CustomDockerClient)
            self.docker_client = client
        self.__stop_network_agent_resource_manager_server(logger=logger)

        logger.info(f"Stopping processing workers on host: {self.host}")
        amount_workers = len(self.workers_native) + len(self.workers_docker)
        if not amount_workers:
            logger.warning("No active processing workers to be stopped.")
        for worker in self.workers_native:
            self.__stop_worker(logger, worker.processor_name, worker.deploy_type, worker.pid)
        self.workers_native = []
        for worker in self.workers_docker:
            self.__stop_worker(logger, worker.processor_name, worker.deploy_type, worker.pid)
        self.workers_docker = []

        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None
