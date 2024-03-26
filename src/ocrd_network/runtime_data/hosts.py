from logging import Logger
from time import sleep
from typing import Dict, List, Union

from .connection_clients import create_docker_client, create_ssh_client
from .network_agents import AgentType, DataNetworkAgent, DataProcessingWorker, DataProcessorServer, DeployType


class DataHost:
    def __init__(
        self, host: str, username: str, password: str, keypath: str, workers: List[Dict], servers: List[Dict]
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.keypath = keypath

        # These flags are used to track whether a connection of the specified
        # type should be created based on the received config file
        self.needs_ssh_connector: bool = False
        self.needs_docker_connector: bool = False

        # Connection clients, ssh for native deployment, docker for docker deployment
        self.ssh_client = None
        self.docker_client = None

        # Time to wait between deploying agents
        self.wait_between_agent_deploys: float = 0.3

        # Lists of network agents based on their agent and deployment type
        self.network_agents_worker_native = []
        self.network_agents_worker_docker = []
        self.network_agents_server_native = []
        self.network_agents_server_docker = []

        if not workers:
            workers = []
        if not servers:
            servers = []

        self.__parse_network_agents_workers(processing_workers=workers)
        self.__parse_network_agents_servers(processor_servers=servers)

        # Used for caching deployed Processor Servers' ports on the current host
        # Key: processor_name, Value: list of ports
        self.processor_servers_ports: dict = {}

    def __add_deployed_agent_server_port_to_cache(self, processor_name: str, port: int) -> None:
        if processor_name not in self.processor_servers_ports:
            self.processor_servers_ports[processor_name] = [port]
            return
        self.processor_servers_ports[processor_name] = self.processor_servers_ports[processor_name].append(port)

    def __append_network_agent_to_lists(self, agent_data: DataNetworkAgent) -> None:
        if agent_data.deploy_type != DeployType.DOCKER and agent_data.deploy_type != DeployType.NATIVE:
            raise ValueError(f"Network agent deploy type is unknown: {agent_data.deploy_type}")
        if agent_data.agent_type != AgentType.PROCESSING_WORKER and agent_data.agent_type != AgentType.PROCESSOR_SERVER:
            raise ValueError(f"Network agent type is unknown: {agent_data.agent_type}")

        if agent_data.deploy_type == DeployType.NATIVE:
            self.needs_ssh_connector = True
            if agent_data.agent_type == AgentType.PROCESSING_WORKER:
                self.network_agents_worker_native.append(agent_data)
            if agent_data.agent_type == AgentType.PROCESSOR_SERVER:
                self.network_agents_server_native.append(agent_data)
        if agent_data.deploy_type == DeployType.DOCKER:
            self.needs_docker_connector = True
            if agent_data.agent_type == AgentType.PROCESSING_WORKER:
                self.network_agents_worker_docker.append(agent_data)
            if agent_data.agent_type == AgentType.PROCESSOR_SERVER:
                self.network_agents_server_docker.append(agent_data)

    def __parse_network_agents_servers(self, processor_servers: List[Dict]):
        for server in processor_servers:
            server_data = DataProcessorServer(
                processor_name=server["name"], deploy_type=server["deploy_type"], host=self.host,
                port=int(server["port"]), init_by_config=True, pid=None
            )
            self.__append_network_agent_to_lists(agent_data=server_data)

    def __parse_network_agents_workers(self, processing_workers: List[Dict]):
        for worker in processing_workers:
            worker_data = DataProcessingWorker(
                processor_name=worker["name"], deploy_type=worker["deploy_type"], host=self.host,
                init_by_config=True, pid=None
            )
            for _ in range(int(worker["number_of_instance"])):
                self.__append_network_agent_to_lists(agent_data=worker_data)

    def create_connection_client(self, client_type: str):
        if client_type not in ["docker", "ssh"]:
            raise ValueError(f"Host client type cannot be of type: {client_type}")
        if client_type == "ssh":
            self.ssh_client = create_ssh_client(self.host, self.username, self.password, self.keypath)
            return self.ssh_client
        if client_type == "docker":
            self.docker_client = create_docker_client(self.host, self.username, self.password, self.keypath)
            return self.docker_client

    def __deploy_network_agent(
        self, logger: Logger, agent_data: Union[DataProcessorServer, DataProcessingWorker],
        mongodb_url: str, rabbitmq_url: str
    ) -> None:
        deploy_type = agent_data.deploy_type
        agent_type = agent_data.agent_type
        name = agent_data.processor_name
        agent_info = f"network agent: {agent_type}, deploy: {deploy_type}, name: {name}, host: {self.host}"
        logger.info(f"Deploying {agent_info}")

        connection_client = None
        if deploy_type == DeployType.NATIVE:
            assert self.ssh_client, f"SSH client connection missing."
            connection_client = self.ssh_client
        if deploy_type == DeployType.DOCKER:
            assert self.docker_client, f"Docker client connection missing."
            connection_client = self.docker_client

        if agent_type == AgentType.PROCESSING_WORKER:
            agent_data.deploy_network_agent(logger, connection_client, mongodb_url, rabbitmq_url)
        if agent_type == AgentType.PROCESSOR_SERVER:
            agent_data.deploy_network_agent(logger, connection_client, mongodb_url)

        sleep(self.wait_between_agent_deploys)

    def __deploy_network_agents_workers(self, logger: Logger, mongodb_url: str, rabbitmq_url: str):
        logger.info(f"Deploying processing workers on host: {self.host}")
        amount_workers = len(self.network_agents_worker_native) + len(self.network_agents_worker_docker)
        if not amount_workers:
            logger.info(f"No processing workers found to be deployed")
        for data_worker in self.network_agents_worker_native:
            self.__deploy_network_agent(logger, data_worker, mongodb_url, rabbitmq_url)
        for data_worker in self.network_agents_worker_docker:
            self.__deploy_network_agent(logger, data_worker, mongodb_url, rabbitmq_url)

    def __deploy_network_agents_servers(self, logger: Logger, mongodb_url: str, rabbitmq_url: str):
        logger.info(f"Deploying processor servers on host: {self.host}")
        amount_servers = len(self.network_agents_server_native) + len(self.network_agents_server_docker)
        if not amount_servers:
            logger.info(f"No processor servers found to be deployed")
        for data_server in self.network_agents_server_native:
            self.__deploy_network_agent(logger, data_server, mongodb_url, rabbitmq_url)
            self.__add_deployed_agent_server_port_to_cache(data_server.processor_name, data_server.port)
        for data_server in self.network_agents_server_docker:
            self.__deploy_network_agent(logger, data_server, mongodb_url, rabbitmq_url)
            self.__add_deployed_agent_server_port_to_cache(data_server.processor_name, data_server.port)

    def deploy_network_agents(self, logger: Logger, mongodb_url: str, rabbitmq_url: str) -> None:
        if self.needs_ssh_connector and not self.ssh_client:
            logger.debug("Creating missing ssh connector before deploying")
            self.ssh_client = self.create_connection_client(client_type="ssh")
        if self.needs_docker_connector:
            logger.debug("Creating missing docker connector before deploying")
            self.docker_client = self.create_connection_client(client_type="docker")
        self.__deploy_network_agents_workers(logger=logger, mongodb_url=mongodb_url, rabbitmq_url=rabbitmq_url)
        self.__deploy_network_agents_servers(logger=logger, mongodb_url=mongodb_url, rabbitmq_url=rabbitmq_url)
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None

    def __stop_network_agent(self, logger: Logger, name: str, deploy_type: DeployType, agent_type: AgentType, pid: str):
        agent_info = f"network agent: {agent_type}, deploy: {deploy_type}, name: {name}"
        if not pid:
            logger.warning(f"No pid was passed for {agent_info}")
            return
        agent_info += f", pid: {pid}"
        logger.info(f"Stopping {agent_info}")
        if deploy_type == DeployType.NATIVE:
            assert self.ssh_client, f"SSH client connection missing"
            self.ssh_client.exec_command(f"kill {pid}")
        if deploy_type == DeployType.DOCKER:
            assert self.docker_client, f"Docker client connection missing"
            self.docker_client.containers.get(pid).stop()

    def __stop_network_agents_workers(self, logger: Logger):
        logger.info(f"Stopping processing workers on host: {self.host}")
        amount_workers = len(self.network_agents_worker_native) + len(self.network_agents_worker_docker)
        if not amount_workers:
            logger.warning(f"No active processing workers to be stopped.")
        for worker in self.network_agents_worker_native:
            self.__stop_network_agent(logger, worker.processor_name, worker.deploy_type, worker.agent_type, worker.pid)
        self.network_agents_worker_native = []
        for worker in self.network_agents_worker_docker:
            self.__stop_network_agent(logger, worker.processor_name, worker.deploy_type, worker.agent_type, worker.pid)
        self.network_agents_worker_docker = []

    def __stop_network_agents_servers(self, logger: Logger):
        logger.info(f"Stopping processor servers on host: {self.host}")
        amount_servers = len(self.network_agents_server_native) + len(self.network_agents_server_docker)
        if not amount_servers:
            logger.warning(f"No active processor servers to be stopped.")
        for server in self.network_agents_server_native:
            self.__stop_network_agent(logger, server.processor_name, server.deploy_type, server.agent_type, server.pid)
        self.network_agents_server_native = []
        for server in self.network_agents_server_docker:
            self.__stop_network_agent(logger, server.processor_name, server.deploy_type, server.agent_type, server.pid)
        self.network_agents_server_docker = []

    def stop_network_agents(self, logger: Logger):
        if self.needs_ssh_connector and not self.ssh_client:
            logger.debug("Creating missing ssh connector before stopping")
            self.ssh_client = self.create_connection_client(client_type="ssh")
        if self.needs_docker_connector and not self.docker_client:
            logger.debug("Creating missing docker connector before stopping")
            self.docker_client = self.create_connection_client(client_type="docker")
        self.__stop_network_agents_workers(logger=logger)
        self.__stop_network_agents_servers(logger=logger)
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None

    def resolve_processor_server_url(self, processor_name: str) -> str:
        processor_server_url = ''
        for data_server in self.network_agents_server_docker:
            if data_server.processor_name == processor_name:
                processor_server_url = f"http://{self.host}:{data_server.port}/"
        for data_server in self.network_agents_server_native:
            if data_server.processor_name == processor_name:
                processor_server_url = f"http://{self.host}:{data_server.port}/"
        return processor_server_url
