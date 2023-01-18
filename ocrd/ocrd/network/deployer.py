from __future__ import annotations
from typing import List, Dict, Union
from paramiko import SSHClient
from re import search as re_search

from ocrd_utils import getLogger

from ocrd.network.deployment_config import *
from ocrd.network.deployment_utils import (
    create_docker_client,
    create_ssh_client,
    CustomDockerClient,
    DeployType,
)
from ocrd.network.processing_worker import ProcessingWorker

# Abstraction of the Deployment functionality
# The ProcessingServer (currently still called Broker) provides the configuration parameters to the Deployer agent.
# The Deployer agent deploys the RabbitMQ Server, MongoDB and the Processing Hosts.
# Each Processing Host may have several Processing Workers.
# Each Processing Worker is an instance of an OCR-D processor.

# TODO:
# Ideally, the interaction among the agents should happen through
# the defined API calls of the objects to stay loyal to the OOP paradigm
# This would also increase the readability and maintainability of the source code.


# TODO: remove debug log statements before beta, their purpose is development only
class Deployer:
    """ Class to wrap the deployment-functionality of the OCR-D Processing-Servers

    Deployer is the one acting. Config is for representation of the config-file only. DeployHost is
    for managing information, not for actually doing things.
    """

    def __init__(self, queue_config: QueueConfig, mongo_config: MongoConfig, hosts_config: List[HostConfig]) -> None:
        """
        Args:
            queue_config: RabbitMQ related configuration
            mongo_config: MongoDB related configuration
            hosts_config: Processing Hosts related configurations
        """
        self.log = getLogger(__name__)
        self.log.debug('The Deployer of the ProcessingServer was invoked')
        self.mongo_data = mongo_config
        self.mq_data = queue_config
        self.hosts = hosts_config

        # TODO: We should have a data structure here to manage the connections and PIDs:
        #  - RabbitMQ - (host address, pid on that host)
        #  - MongoDB - (host address, pid on that host)
        #  - Processing Hosts - (host address)
        #    - Processing Workers - (pid on that host address)
        #  The PIDs are stored for future usage - i.e. for killing them forcefully/gracefully.
        #  Currently, the connections (ssh_client, docker_client) and
        #  the PIDs are stored inside the config data classes

    # Avoid using this method
    # TODO: Should be removed
    def deploy_all(self) -> None:
        """ Deploy the message queue and all processors defined in the config-file
        """
        # The order of deploying may be important to recover from previous state
        rabbitmq_url = self.deploy_rabbitmq()
        mongodb_url = self.deploy_mongodb()
        self.deploy_hosts(self.hosts, rabbitmq_url, mongodb_url)

    def kill_all(self) -> None:
        # The order of killing is important to optimize graceful shutdown in the future
        # If RabbitMQ server is killed before killing Processing Workers, that may have
        # bad outcome and leave Processing Workers in an unpredictable state

        # First kill the active Processing Workers on Processing Hosts
        # They may still want to update something in the db before closing
        # They may still want to nack the currently processed messages back to the RabbitMQ Server
        self.kill_hosts()

        # Second kill the MongoDB
        self.kill_mongodb()

        # Third kill the RabbitMQ Server
        self.kill_rabbitmq()

    def deploy_hosts(self, hosts: List[HostConfig], rabbitmq_url: str, mongodb_url: str) -> None:
        self.log.debug("Starting to deploy hosts")
        for host in hosts:
            self.log.debug(f"Deploying processing workers on host: {host.address}")
            for processor in host.processors:
                self._deploy_processing_worker(processor, host, rabbitmq_url, mongodb_url)
            # TODO: These connections, just like the PIDs, should not be kept in the config data classes
            #  The connections are correctly closed on host level, but created on processing worker level?
            if host.ssh_client:
                host.ssh_client.close()
            if host.docker_client:
                host.docker_client.close()

    # TODO: Creating connections if missing should probably occur when deploying hosts not when
    #  deploying processing workers. The deploy_type checks and opening connections creates duplicate code.
    def _deploy_processing_worker(self, processor: ProcessorConfig, host: HostConfig,
                                  rabbitmq_url: str, mongodb_url: str) -> None:

        self.log.debug(f'deploy "{processor.deploy_type}" processor: "{processor}" on'
                       f'"{host.address}"')
        assert not processor.pids, 'processors already deployed. Pids are present. Host: ' \
                                   '{host.__dict__}. Processor: {processor.__dict__}'

        # TODO: The check for available ssh or docker connections should probably happen inside `deploy_hosts`
        if processor.deploy_type == DeployType.native:
            if not host.ssh_client:
                host.ssh_client = create_ssh_client(host.address, host.username, host.password, host.keypath)
        elif processor.deploy_type == DeployType.docker:
            if not host.docker_client:
                host.docker_client = create_docker_client(host.address, host.username, host.password, host.keypath)
        else:
            # Error case, should never enter here. Handle error cases here (if needed)
            self.log.error(f"Failed to deploy: {processor.name}. The deploy type is unknown.")
            pass

        for _ in range(processor.count):
            if processor.deploy_type == DeployType.native:
                assert host.ssh_client  # to satisfy mypy
                pid = self.start_native_processor(
                    client=host.ssh_client,
                    processor_name=processor.name,
                    _queue_url=rabbitmq_url,
                    _database_url=mongodb_url)
                processor.add_started_pid(pid)
            elif processor.deploy_type == DeployType.docker:
                assert host.docker_client  # to satisfy mypy
                pid = self.start_docker_processor(
                    client=host.docker_client,
                    processor_name=processor.name,
                    _queue_url=rabbitmq_url,
                    _database_url=mongodb_url)
                processor.add_started_pid(pid)
            else:
                # TODO: Weirdly there is a duplication of code inside this method
                # Error case, should never enter here. Handle error cases here (if needed)
                self.log.error(f"Failed to deploy: {processor.name}. The deploy type is unknown.")
                pass

    def deploy_rabbitmq(self, image: str = 'rabbitmq', detach: bool = True, remove: bool = True,
                         ports_mapping: Union[Dict, None] = None) -> str:
        # Note for a peer
        # This method deploys the RabbitMQ Server.
        # Handling of creation of queues, submitting messages to queues,
        # and receiving messages from queues is part of the RabbitMQ Library
        # Which is part of the OCR-D WebAPI implementation.
        self.log.debug(f"Trying to deploy image[{image}], with modes: detach[{detach}], remove[{remove}]")

        if not self.mongo_data or not self.mongo_data.address:
            self.log.error(f"Deploying RabbitMQ has failed - missing configuration.")
            # TODO: Raise an error instead of silently ignoring it
            return ""

        client = create_docker_client(self.mq_data.address, self.mq_data.username,
                                      self.mq_data.password, self.mq_data.keypath)
        if not ports_mapping:
            # 5672, 5671 - used by AMQP 0-9-1 and AMQP 1.0 clients without and with TLS
            # 15672, 15671: HTTP API clients, management UI and rabbitmqadmin, without and with TLS
            # 25672: used for internode and CLI tools communication and is allocated from
            # a dynamic range (limited to a single port by default, computed as AMQP port + 20000)
            ports_mapping = {
                5672: self.mq_data.port,
                15672: 15672,
                25672: 25672
            }
        self.log.debug(f"Ports mapping: {ports_mapping}")
        # TODO: use rm here or not? Should queues be reused?
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping
        )
        assert res and res.id, \
            f'Failed to start RabbitMQ docker container on host: {self.mq_data.address}'
        self.mq_data.pid = res.id
        client.close()

        # Build the RabbitMQ Server URL to return
        rmq_host = self.mq_data.address
        rmq_port = self.mq_data.port
        rmq_vhost = "/"  # the default virtual host

        rabbitmq_url = f"{rmq_host}:{rmq_port}{rmq_vhost}"
        self.log.debug(f"The RabbitMQ server was deployed on url: {rabbitmq_url}")
        return rabbitmq_url

    def deploy_mongodb(self, image: str = 'mongo', detach: bool = True, remove: bool = True,
                        ports_mapping: Union[Dict, None] = None) -> str:
        self.log.debug(f"Trying to deploy image[{image}], with modes: detach[{detach}], remove[{remove}]")

        if not self.mongo_data or not self.mongo_data.address:
            self.log.error(f"Deploying MongoDB has failed - missing configuration.")
            # TODO: Raise an error instead of silently ignoring it
            return ""

        client = create_docker_client(self.mongo_data.address, self.mongo_data.username,
                                      self.mongo_data.password, self.mongo_data.keypath)
        if not ports_mapping:
            ports_mapping = {
                27017: self.mongo_data.port
            }
        self.log.debug(f"Ports mapping: {ports_mapping}")
        # TODO: use rm here or not? Should the mongodb be reused?
        # TODO: what about the data-dir? Must data be preserved?
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping
        )
        assert res and res.id, \
            f'Failed to start MongoDB docker container on host: {self.mongo_data.address}'
        self.mongo_data.pid = res.id
        client.close()

        # Build the MongoDB URL to return
        mongodb_prefix = "mongodb://"
        mongodb_host = self.mongo_data.address
        mongodb_port = self.mongo_data.port
        mongodb_url = f"{mongodb_prefix}{mongodb_host}:{mongodb_port}"
        self.log.debug(f"The MongoDB was deployed on url: {mongodb_url}")
        return mongodb_url

    def kill_rabbitmq(self) -> None:
        # TODO: The PID must not be stored in the configuration `mq_data`.
        if not self.mq_data or not self.mq_data.pid:
            self.log.warning(f"No running RabbitMQ instance found")
            # TODO: Ignoring this silently is problematic in the future
            return
        self.log.debug(f"Trying to stop the deployed RabbitMQ with PID: {self.mq_data.pid}")

        client = create_docker_client(self.mq_data.address, self.mq_data.username,
                                      self.mq_data.password, self.mq_data.keypath)
        client.containers.get(self.mq_data.pid).stop()
        self.mq_data.pid = None
        client.close()
        self.log.debug('The RabbitMQ is stopped')

    def kill_mongodb(self) -> None:
        # TODO: The PID must not be stored in the configuration `mongo_data`.
        if not self.mongo_data or not self.mongo_data.pid:
            self.log.warning(f"No running MongoDB instance found")
            # TODO: Ignoring this silently is problematic in the future
            return
        self.log.debug(f"Trying to stop the deployed MongoDB with PID: {self.mongo_data.pid}")

        client = create_docker_client(self.mongo_data.address, self.mongo_data.username,
                                      self.mongo_data.password, self.mongo_data.keypath)
        client.containers.get(self.mongo_data.pid).stop()
        self.mongo_data.pid = None
        client.close()
        self.log.debug('The MongoDB is stopped')

    def kill_hosts(self) -> None:
        self.log.debug("Starting to kill/stop hosts")
        # Kill processing hosts
        for host in self.hosts:
            self.log.debug(f"Killing/Stopping processing workers on host: {host.address}")
            if host.ssh_client:
                host.ssh_client = create_ssh_client(host.address, host.username, host.password, host.keypath)
            if host.docker_client:
                host.docker_client = create_docker_client(host.address, host.username, host.password, host.keypath)
            # Kill deployed OCR-D processor instances on this Processing worker host
            self.kill_processing_worker(host)

    def kill_processing_worker(self, host: HostConfig) -> None:
        for processor in host.processors:
            if processor.deploy_type.is_native():
                for pid in processor.pids:
                    self.log.debug(f'Trying to kill/stop native processor: {processor.name}, with PID: {pid}')
                    # TODO: For graceful shutdown we may want to send additional parameters to kill
                    host.ssh_client.exec_command(f'kill {pid}')
            elif processor.deploy_type.is_docker():
                for pid in processor.pids:
                    self.log.debug(f'Trying to kill/stop docker container processor: {processor.name}, with PID: {pid}')
                    # TODO: think about timeout.
                    #       think about using threads to kill parallelized to reduce waiting time
                    host.docker_client.containers.get(pid).stop()
            else:
                # Error case, should never enter here. Handle error cases here (if needed)
                self.log.error(f"Failed to kill: {processor.name}. The deploy type is unknown.")
                pass
            processor.pids = []

    # TODO: This method may not fit anymore. Should be further investigated.
    @staticmethod
    def start_native_processor(client: SSHClient, processor_name: str, _queue_url: str,
                               _database_url: str) -> str:
        log = getLogger(__name__)
        log.debug(f'Starting native processor: {processor_name}')
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        # TODO: add real command here to start processing server here
        cmd = 'sleep 23s'
        # the only way to make it work to start a process in the background and return early is
        # this construction. The pid of the last started background process is printed with
        # `echo $!` but it is printed inbetween other output. Because of that I added `xyz` before
        # and after the code to easily be able to filter out the pid via regex when returning from
        # the function
        stdin.write(f'{cmd} & \n echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        # What does this return and is supposed to return?
        # Putting some comments when using patterns is always appreciated
        # Since the docker version returns PID, this should also return PID for consistency
        # TODO: mypy error: ignore or fix. Problem: re.search returns Optional (can be None, causes
        #       error if try to call)
        return re_search(r'xyz([0-9]+)xyz', output).group(1)

    # TODO: This method may not fit anymore. Should be further investigated.
    @staticmethod
    def start_docker_processor(client: CustomDockerClient, processor_name: str, _queue_url: str,
                               _database_url: str) -> str:
        log = getLogger(__name__)
        log.debug(f'Starting docker container processor: {processor_name}')
        # TODO: add real command here to start processing server here
        res = client.containers.run('debian', 'sleep 500s', detach=True, remove=True)
        assert res and res.id, 'run processor in docker-container failed'
        return res.id
