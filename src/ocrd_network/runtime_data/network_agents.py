from logging import Logger
from typing import Any

from re import search as re_search
from ..constants import AgentType, DeployType


# TODO: Find appropriate replacement for the hack
def deploy_agent_native_get_pid_hack(logger: Logger, ssh_client, start_cmd: str):
    channel = ssh_client.invoke_shell()
    stdin, stdout = channel.makefile("wb"), channel.makefile("rb")
    logger.debug(f"Executing command: {start_cmd}")

    # TODO: This hack should still be fixed
    #   Note left from @joschrew
    #   the only way (I could find) to make it work to start a process in the background and
    #   return early is this construction. The pid of the last started background process is
    #   printed with `echo $!` but it is printed between other output. Because of that I added
    #   `xyz` before and after the code to easily be able to filter out the pid via regex when
    #   returning from the function

    stdin.write(f"{start_cmd}\n")
    stdin.write("echo xyz$!xyz \n exit \n")
    output = stdout.read().decode("utf-8")
    stdout.close()
    stdin.close()
    return re_search(r"xyz([0-9]+)xyz", output).group(1)  # type: ignore


# TODO: Implement the actual method that is missing
def deploy_agent_docker_template(logger: Logger, docker_client, start_cmd: str):
    """
    logger.debug(f"Executing command: {start_cmd}")
    res = docker_client.containers.run("debian", "sleep 500s", detach=True, remove=True)
    assert res and res.id, f"Starting docker network agent has failed with command: {start_cmd}"
    return res.id
    """
    raise Exception("Deploying docker type agents is not supported yet!")


class DataNetworkAgent:
    def __init__(
        self, processor_name: str, deploy_type: DeployType, agent_type: AgentType,
        host: str, init_by_config: bool, pid: Any = None
    ) -> None:
        self.processor_name = processor_name
        self.deploy_type = deploy_type
        self.host = host
        self.deployed_by_config = init_by_config
        self.agent_type = agent_type
        # The id is assigned when the agent is deployed
        self.pid = pid

    def _start_native_instance(self, logger: Logger, ssh_client, start_cmd: str):
        if self.deploy_type != DeployType.NATIVE:
            raise RuntimeError(f"Mismatch of deploy type when starting network agent: {self.processor_name}")
        agent_pid = deploy_agent_native_get_pid_hack(logger=logger, ssh_client=ssh_client, start_cmd=start_cmd)
        return agent_pid

    def _start_docker_instance(self, logger: Logger, docker_client, start_cmd: str):
        if self.deploy_type != DeployType.DOCKER:
            raise RuntimeError(f"Mismatch of deploy type when starting network agent: {self.processor_name}")
        agent_pid = deploy_agent_docker_template(logger=logger, docker_client=docker_client, start_cmd=start_cmd)
        return agent_pid


class DataProcessingWorker(DataNetworkAgent):
    def __init__(
        self, processor_name: str, deploy_type: DeployType, host: str, init_by_config: bool, pid: Any = None
    ) -> None:
        super().__init__(
            processor_name=processor_name, host=host, deploy_type=deploy_type, agent_type=AgentType.PROCESSING_WORKER,
            init_by_config=init_by_config, pid=pid
        )

    def deploy_network_agent(self, logger: Logger, connector_client, database_url: str, queue_url: str):
        if self.deploy_type == DeployType.NATIVE:
            start_cmd = f"{self.processor_name} {self.agent_type} --database {database_url} --queue {queue_url} &"
            self.pid = self._start_native_instance(logger, connector_client, start_cmd)
            return self.pid
        if self.deploy_type == DeployType.DOCKER:
            # TODO: add real command to start processing worker in docker here
            start_cmd = f""
            self.pid = self._start_docker_instance(logger, connector_client, start_cmd)
            return self.pid
        raise RuntimeError(f"Unknown deploy type of {self.__dict__}")


class DataProcessorServer(DataNetworkAgent):
    def __init__(
        self, processor_name: str, deploy_type: DeployType, host: str, port: int, init_by_config: bool, pid: Any = None
    ) -> None:
        super().__init__(
            processor_name=processor_name, host=host, deploy_type=deploy_type, agent_type=AgentType.PROCESSOR_SERVER,
            init_by_config=init_by_config, pid=pid
        )
        self.port = port

    def deploy_network_agent(self, logger: Logger, connector_client, database_url: str):
        agent_address = f"{self.host}:{self.port}"
        if self.deploy_type == DeployType.NATIVE:
            start_cmd = f"{self.processor_name} {self.agent_type} --address {agent_address} --database {database_url} &"
            self.pid = self._start_native_instance(logger, connector_client, start_cmd)
            return self.pid
        if self.deploy_type == DeployType.DOCKER:
            # TODO: add real command to start processor server in docker here
            start_cmd = f""
            self.pid = self._start_docker_instance(logger, connector_client, start_cmd)
            return self.pid
        raise RuntimeError(f"Unknown deploy type of {self.__dict__}")
