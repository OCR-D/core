from enum import Enum
from logging import Logger
from typing import Any

from re import search as re_search


class DeployType(Enum):
    # Deployed by the Processing Server config file
    DOCKER = "docker"
    NATIVE = "native"
    # Deployed through a registration endpoint of the Processing Server
    EXTERNAL = "external"


class NetworkAgentType(Enum):
    PROCESSING_WORKER = "worker"
    PROCESSOR_SERVER = "server"


def deploy_agent_native_get_pid_hack(logger: Logger, ssh_client, start_cmd: str):
    channel = ssh_client.invoke_shell()
    stdin, stdout = channel.makefile("wb"), channel.makefile("rb")
    logger.debug(f"About to execute start up command: {start_cmd}")

    # TODO: This hack should still be fixed
    #   Note left from @joschrew
    #   the only way (I could find) to make it work to start a process in the background and
    #   return early is this construction. The pid of the last started background process is
    #   printed with `echo $!` but it is printed inbetween other output. Because of that I added
    #   `xyz` before and after the code to easily be able to filter out the pid via regex when
    #   returning from the function

    stdin.write(f"{start_cmd}\n")
    stdin.write("echo xyz$!xyz \n exit \n")
    output = stdout.read().decode("utf-8")
    stdout.close()
    stdin.close()
    return re_search(r"xyz([0-9]+)xyz", output).group(1)  # type: ignore


def deploy_agent_docker_template(logger: Logger, docker_client, start_cmd: str):
    logger.debug(f"About to execute start up command: {start_cmd}")
    res = docker_client.containers.run("debian", "sleep 500s", detach=True, remove=True)
    assert res and res.id, f"Starting docker network agent has failed with command: {start_cmd}"
    return res.id


class DataNetworkAgent:
    def __init__(
        self,
        processor_name: str,
        deploy_type: DeployType,
        agent_type: NetworkAgentType,
        host: str,
        init_by_config: bool,
        pid: Any = None
    ) -> None:
        self.processor_name = processor_name
        self.deploy_type = deploy_type
        self.host = host
        self.deployed_by_config = init_by_config
        self.agent_type = agent_type
        # The id is assigned when the agent is deployed
        self.pid = pid

    def stop_native_instance(self):
        if self.deploy_type == DeployType.DOCKER:
            raise RuntimeError(f"Mismatch of deploy type when stopping network agent: {self.processor_name}")

    def stop_docker_instance(self):
        if self.deploy_type == DeployType.NATIVE:
            raise RuntimeError(f"Mismatch of deploy type when stopping network agent: {self.processor_name}")


class DataProcessingWorker(DataNetworkAgent):
    def __init__(
        self,
        processor_name: str,
        deploy_type: DeployType,
        host: str,
        init_by_config: bool,
        pid: Any = None
    ) -> None:
        super().__init__(
            processor_name=processor_name,
            host=host,
            deploy_type=deploy_type,
            agent_type=NetworkAgentType.PROCESSING_WORKER,
            init_by_config=init_by_config,
            pid=pid
        )

    def deploy_network_agent(self, logger: Logger, connector_client, database_url, queue_url):
        if self.deploy_type == DeployType.NATIVE:
            self.pid = self.__start_native_instance(logger, connector_client, database_url, queue_url)
            return self.pid
        if self.deploy_type == DeployType.DOCKER:
            self.pid = self.__start_docker_instance(logger, connector_client, database_url, queue_url)
            return self.pid

    def __start_native_instance(self, logger: Logger, ssh_client, database_url: str, queue_url: str):
        if self.deploy_type == DeployType.DOCKER:
            raise RuntimeError(f"Mismatch of deploy type when starting network agent: {self.processor_name}")
        logger.info(f"Starting native Processing Worker: {self.processor_name}")
        start_cmd = f"{self.processor_name} {self.agent_type} --database {database_url} --queue {queue_url} &"
        agent_pid = deploy_agent_native_get_pid_hack(logger=logger, ssh_client=ssh_client, start_cmd=start_cmd)
        return agent_pid

    def __start_docker_instance(self, logger: Logger, docker_client, database_url: str, queue_url: str) -> str:
        if self.deploy_type == DeployType.NATIVE:
            raise RuntimeError(f"Mismatch of deploy type when starting network agent: {self.processor_name}")
        logger.info(f"Starting docker Processing Worker: {self.processor_name}")
        # TODO: add real command to start processing server in docker here
        start_cmd = f""
        agent_pid = deploy_agent_docker_template(logger=logger, docker_client=docker_client, start_cmd=start_cmd)
        return agent_pid


class DataProcessorServer(DataNetworkAgent):
    def __init__(
        self,
        processor_name: str,
        deploy_type: DeployType,
        host: str,
        port: int,
        init_by_config: bool,
        pid: Any = None
    ) -> None:
        super().__init__(host, deploy_type, NetworkAgentType.PROCESSOR_SERVER, processor_name, init_by_config, pid)
        self.port = port

    def deploy_network_agent(self, logger: Logger, connector_client, database_url, agent_address):
        if self.deploy_type == DeployType.NATIVE:
            self.pid = self.__start_native_instance(logger, connector_client, database_url, agent_address)
            return self.pid
        if self.deploy_type == DeployType.DOCKER:
            self.pid = self.__start_docker_instance(logger, connector_client, database_url, agent_address)
            return self.pid

    def __start_native_instance(self, logger: Logger, ssh_client, database_url: str, agent_address: str) -> str:
        if self.deploy_type == DeployType.DOCKER:
            raise RuntimeError(f"Mismatch of deploy type when starting network agent: {self.processor_name}")
        logger.info(f"Starting native Processor Server: {self.processor_name}")
        start_cmd = f"{self.processor_name} {self.agent_type} --address {agent_address} --database {database_url} &"
        agent_pid = deploy_agent_native_get_pid_hack(logger=logger, ssh_client=ssh_client, start_cmd=start_cmd)
        return agent_pid

    def __start_docker_instance(self, logger: Logger, docker_client, database_url: str, agent_address: str) -> str:
        if self.deploy_type == DeployType.NATIVE:
            raise RuntimeError(f"Mismatch of deploy type when starting network agent: {self.processor_name}")
        logger.info(f"Starting docker Processing Worker: {self.processor_name}")
        # TODO: add real command to start processing server in docker here
        start_cmd = f""
        agent_pid = deploy_agent_docker_template(logger=logger, docker_client=docker_client, start_cmd=start_cmd)
        return agent_pid
