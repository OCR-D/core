from logging import Logger
from time import sleep
from typing import Dict, List, Union

from .connection_clients import create_docker_client, create_ssh_client
from .network_agents import AgentType, DataNetworkAgent, DataProcessingWorker, DataProcessorServer, DeployType


class DataHost:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        keypath: str,
        workers: List[Dict],
        servers: List[Dict]
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

        # Lists of network agents based on their deployment type
        self.network_agents_docker = []
        self.network_agents_native = []
        # Lists of network agents based on their agent type
        self.network_agents_worker = []
        self.network_agents_server = []

        if not workers:
            workers = []
        if not servers:
            servers = []

        self.__parse_network_agents(processing_workers=workers, processor_servers=servers)

        # Used for caching deployed Processor Servers' ports on the current host
        # Key: processor_name, Value: list of ports
        self.processor_servers_ports: dict = {}

    def __add_deployed_agent_server_port_to_cache(self, processor_name: str, port: int):
        if processor_name not in self.processor_servers_ports:
            self.processor_servers_ports[processor_name] = [port]
            return
        self.processor_servers_ports[processor_name] = self.processor_servers_ports[processor_name].append(port)

    def __append_network_agent_to_lists(self, agent_data: DataNetworkAgent):
        if agent_data.deploy_type == DeployType.NATIVE:
            self.needs_ssh_connector = True
            self.network_agents_native.append(agent_data)
        elif agent_data.deploy_type == DeployType.DOCKER:
            self.needs_docker_connector = True
            self.network_agents_docker.append(agent_data)
        else:
            raise ValueError(f"Network agent deploy type is unknown: {agent_data.deploy_type}")

        if agent_data.agent_type == AgentType.PROCESSING_WORKER:
            self.network_agents_worker.append(agent_data)
        elif agent_data.agent_type == AgentType.PROCESSOR_SERVER:
            self.network_agents_server.append(agent_data)
        else:
            raise ValueError(f"Network agent type is unknown: {agent_data.agent_type}")

    def __parse_network_agents(self, processing_workers: List[Dict], processor_servers: List[Dict]):
        for worker in processing_workers:
            worker_data = DataProcessingWorker(
                processor_name=worker["name"],
                deploy_type=worker["deploy_type"],
                host=self.host,
                init_by_config=True,
                pid=None
            )
            for _ in range(int(worker["number_of_instance"])):
                self.__append_network_agent_to_lists(agent_data=worker_data)
        for server in processor_servers:
            server_data = DataProcessorServer(
                processor_name=server["name"],
                deploy_type=server["deploy_type"],
                host=self.host,
                port=int(server["port"]),
                init_by_config=True,
                pid=None
            )
            self.__append_network_agent_to_lists(agent_data=server_data)

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
        self,
        logger: Logger,
        agent_data: Union[DataProcessorServer, DataProcessingWorker],
        mongodb_url: str,
        rabbitmq_url: str
    ):
        deploy_type = agent_data.deploy_type
        agent_type = agent_data.agent_type
        name = agent_data.processor_name
        agent_info = f"network agent: {agent_type}, deploy: {deploy_type}, name: {name}, host: {self.host}"
        logger.info(f"Deploying {agent_info}")

        if deploy_type == DeployType.NATIVE:
            assert self.ssh_client, f"SSH client connection missing."
            if agent_type == AgentType.PROCESSING_WORKER:
                agent_data.deploy_network_agent(logger, self.ssh_client, mongodb_url, rabbitmq_url)
            if agent_type == AgentType.PROCESSOR_SERVER:
                agent_data.deploy_network_agent(logger, self.ssh_client, mongodb_url)

        if deploy_type == DeployType.DOCKER:
            assert self.docker_client, f"Docker client connection missing."
            if agent_type == AgentType.PROCESSING_WORKER:
                raise Exception("Deploying Processing worker of docker type is not supported yet!")
            if agent_type == AgentType.PROCESSOR_SERVER:
                raise Exception("Deploying Processor Server of docker type is not supported yet!")
        sleep(self.wait_between_agent_deploys)

    def deploy_network_agents(self, logger: Logger, mongodb_url: str, rabbitmq_url: str) -> None:
        if self.needs_ssh_connector and not self.ssh_client:
            logger.debug("Creating missing ssh connector before deploying")
            self.ssh_client = self.create_connection_client(client_type="ssh")
        if self.needs_docker_connector:
            logger.debug("Creating missing docker connector before deploying")
            self.docker_client = self.create_connection_client(client_type="docker")

        logger.info(f"Deploying processing workers on host: {self.host}")
        amount_workers = len(self.network_agents_worker)
        if not amount_workers:
            logger.info(f"No processing workers found to be deployed")
        for data_worker in self.network_agents_worker:
            self.__deploy_network_agent(logger, data_worker, mongodb_url, rabbitmq_url)

        logger.info(f"Deploying processor servers on host: {self.host}")
        amount_processors = len(self.network_agents_server)
        if not amount_processors:
            logger.info(f"No processor servers found to be deployed")
        for data_server in self.network_agents_server:
            self.__deploy_network_agent(logger, data_server, mongodb_url, rabbitmq_url)
            self.__add_deployed_agent_server_port_to_cache(data_server.processor_name, data_server.port)

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

    def stop_network_agents(self, logger: Logger):
        if self.needs_ssh_connector and not self.ssh_client:
            logger.debug("Creating missing ssh connector before stopping")
            self.ssh_client = self.create_connection_client(client_type="ssh")
        if self.needs_docker_connector and not self.docker_client:
            logger.debug("Creating missing docker connector before stopping")
            self.docker_client = self.create_connection_client(client_type="docker")

        logger.info(f"Stopping processing workers on host: {self.host}")
        amount_workers = len(self.network_agents_worker)
        if not amount_workers:
            logger.warning(f"No active processing workers to be stopped.")
        for worker in self.network_agents_worker:
            self.__stop_network_agent(logger, worker.processor_name, worker.deploy_type, worker.agent_type, worker.pid)
        self.network_agents_worker = []

        logger.info(f"Stopping processor servers on host: {self.host}")
        amount_servers = len(self.network_agents_server)
        if not amount_servers:
            logger.warning(f"No active processor servers to be stopped.")
        for server in self.network_agents_server:
            self.__stop_network_agent(logger, server.processor_name, server.deploy_type, server.agent_type, server.pid)
        self.network_agents_server = []

        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None
