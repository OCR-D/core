from logging import Logger
from time import sleep
from typing import Dict, List

from .network_agents import DeployType, DataProcessingWorker, DataProcessorServer
from .connection_wrappers import create_docker_client, create_ssh_client


class DataHost:
    def __init__(self, config: Dict) -> None:
        self.host = config["address"]
        self.username = config["username"]
        self.password = config.get("password", None)
        self.keypath = config.get("path_to_privkey", None)

        self.wait_between_agent_deploys: float = 0.3

        self.config_workers = config.get("workers", [])
        self.config_servers = config.get("servers", [])

        # These flags are used to track whether a connection
        # of the specified type will be required
        self.needs_ssh: bool = False
        self.needs_docker: bool = False

        self.ssh_client = None
        self.docker_client = None

        # Lists for accessing agents data
        self.network_agents_docker = []
        self.network_agents_native = []
        self.network_agents_worker = []
        self.network_agents_server = []

        # Used for caching deployed Processor Servers' ports on the host
        # Key: processor_name, Value: list of ports
        self.processor_servers_ports: dict = {}

    def __read_network_agents_from_config(self, processing_workers: List, processor_servers: List) -> None:
        for worker in processing_workers:
            worker_data = DataProcessingWorker(
                processor_name=worker["name"],
                deploy_type=worker["deploy_type"],
                host=self.host,
                init_by_config=True,
                pid=None
            )
            for _ in range(int(worker["number_of_instance"])):
                if worker_data.deploy_type == DeployType.NATIVE:
                    self.network_agents_native.append(worker_data)
                    self.needs_ssh = True
                if worker_data.deploy_type == DeployType.DOCKER:
                    self.network_agents_docker.append(worker_data)
                    self.needs_docker = True
                self.network_agents_worker.append(worker_data)

        for server in processor_servers:
            server_data = DataProcessorServer(
                processor_name=server["name"],
                deploy_type=server["deploy_type"],
                host=self.host,
                port=int(server["port"]),
                init_by_config=True,
                pid=None
            )
            if server_data.deploy_type == DeployType.NATIVE:
                self.network_agents_native.append(server_data)
                self.needs_ssh = True
            if server_data.deploy_type == DeployType.DOCKER:
                self.network_agents_docker.append(server_data)
                self.needs_docker = True
            self.network_agents_server.append(server_data)

    def __append_port_to_agent_server_name(self, processor_name: str, port: int):
        if processor_name not in self.processor_servers_ports:
            self.processor_servers_ports[processor_name] = [port]
            return
        self.processor_servers_ports[processor_name] = self.processor_servers_ports[processor_name].append(port)

    def create_connection_client(self, client_type: str):
        if client_type not in ['docker', 'ssh']:
            raise ValueError(f'Host client type cannot be of type: {client_type}')
        if client_type == 'ssh':
            if not self.ssh_client:
                self.ssh_client = create_ssh_client(self.host, self.username, self.password, self.keypath)
            return self.ssh_client
        if client_type == 'docker':
            if not self.docker_client:
                self.docker_client = create_docker_client(self.host, self.username, self.password, self.keypath)
            return self.docker_client

    def _deploy_network_agents_workers(self, logger: Logger, mongodb_url: str, rabbitmq_url: str, ) -> None:
        for data_worker in self.network_agents_worker:
            debug_message = f"""
                Deploying processing worker '{data_worker.processor_name}' in '{data_worker.deploy_type}' environment, 
                address: {self.host}
            """
            logger.debug(debug_message)
            if data_worker.deploy_type == DeployType.DOCKER:
                assert self.docker_client  # to satisfy mypy
                connector_client = self.docker_client
            else:  # data_worker.deploy_type == DeployType.NATIVE:
                assert self.ssh_client  # to satisfy mypy
                connector_client = self.ssh_client
            data_worker.deploy_network_agent(logger, connector_client, mongodb_url, rabbitmq_url)
            sleep(self.wait_between_agent_deploys)

    def _deploy_network_agents_servers(self, logger: Logger, mongodb_url: str):
        for data_server in self.network_agents_server:
            debug_message = f"""
                Deploying processor server '{data_server.processor_name}' in '{data_server.deploy_type}' environment, 
                address: {data_server.host}:{data_server.port}
                """
            logger.debug(debug_message)
            agent_address = f"{data_server.host}:{data_server.port}"
            if data_server.deploy_type == DeployType.DOCKER:
                assert self.docker_client  # to satisfy mypy
                connector_client = self.docker_client
                raise Exception("Deploying docker processor server is not supported yet!")
            else:  # data_server.deploy_type == DeployType.NATIVE:
                assert self.ssh_client  # to satisfy mypy
                connector_client = self.ssh_client
            data_server.deploy_network_agent(logger, connector_client, mongodb_url, agent_address)
            self.__append_port_to_agent_server_name(data_server.processor_name, data_server.port)
            sleep(self.wait_between_agent_deploys)

    def deploy_network_agents(self, logger: Logger, mongodb_url: str, rabbitmq_url: str) -> None:
        self.__read_network_agents_from_config(self.config_workers, self.config_servers)
        logger.info(f"{self.config_workers}")
        logger.info(f"{self.config_servers}")
        logger.info(f"{self.network_agents_worker}")
        logger.info(f"{self.network_agents_server}")
        if self.needs_ssh:
            logger.debug("Creating an ssh connector")
            self.create_connection_client(client_type="ssh")
            assert self.ssh_client
        if self.needs_docker:
            logger.debug("Creating a docker connector")
            self.create_connection_client(client_type="docker")
            assert self.docker_client
        logger.debug(f"Deploying processing workers on host: {self.host}")
        self._deploy_network_agents_workers(logger, mongodb_url, rabbitmq_url)
        logger.debug(f"Deploying processor servers on host: {self.host}")
        self._deploy_network_agents_servers(logger, mongodb_url)
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None

    def _stop_host_agents_processing_workers(self, logger: Logger):
        amount_workers = len(self.network_agents_worker)
        if not amount_workers:
            logger.warning(f"No active processing workers to be stopped.")
        for worker in self.network_agents_worker:
            if not worker.pid:
                continue
            if worker.deploy_type == DeployType.NATIVE:
                self.ssh_client.exec_command(f"kill {worker.pid}")
            elif worker.deploy_type == DeployType.DOCKER:
                self.docker_client.containers.get(worker.pid).stop()
            logger.info(f"""
                Stopped {worker.deploy_type} processing worker with '{worker.processor_name}' with pid '{worker.pid}'"
            """)
        self.network_agents_worker = []

    def _stop_host_agents_processor_servers(self, logger: Logger):
        amount_servers = len(self.network_agents_server)
        if not amount_servers:
            logger.warning(f"No active processor servers to be stopped.")
        for server in self.network_agents_server:
            if not server.pid:
                continue
            if server.deploy_type == DeployType.NATIVE:
                self.ssh_client.exec_command(f"kill {server.pid}")
            elif server.deploy_type == DeployType.DOCKER:
                self.docker_client.containers.get(server.pid).stop()
            logger.info(f"""
                Stopped {server.deploy_type} processor server with '{server.processor_name}' with pid '{server.pid}'"
            """)
        self.network_agents_server = []

    def stop_network_agents(self, logger: Logger):
        if self.needs_ssh:
            self.create_connection_client(client_type="ssh")
        assert self.ssh_client
        if self.needs_docker:
            self.create_connection_client(client_type="docker")
        assert self.docker_client
        logger.info(f"Stopping processing workers on host: {self.host}")
        self._stop_host_agents_processing_workers(logger)
        logger.info(f"Stopping processor servers on host: {self.host}")
        self._stop_host_agents_processor_servers(logger)
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None
