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
        self.log.debug('Deployer-init()')
        self.mongo_data = mongo_config
        self.mq_data = queue_config
        self.hosts = hosts_config

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
        self.log.debug("Killing all deployed agents")
        # The order of killing is important to optimize graceful shutdown in the future
        # If RabbitMQ server is killed before killing Processing Workers, that may have
        # bad outcome and leave Processing Workers in an unpredictable state

        # First kill the active Processing Workers on Processing Hosts
        # They may still want to update something in the db before closing
        # They may still want to nack the currently processed messages back to the RabbitMQ Server
        self.kill_hosts()
        self.log.debug("Killed deployed agents")

        # Second kill the MongoDB
        self.kill_mongodb()

        # Third kill the RabbitMQ Server
        self.kill_rabbitmq()

    def deploy_hosts(self, hosts: List[HostConfig], rabbitmq_url: str, mongodb_url: str) -> None:
        self.log.debug("Deploying hosts")
        for host in hosts:
            for processor in host.processors:
                self._deploy_processing_worker(processor, host, rabbitmq_url, mongodb_url)
            if host.ssh_client:
                host.ssh_client.close()
            if host.docker_client:
                host.docker_client.close()
        self.log.debug("Hosts deployed")

    def _deploy_processing_worker(self, processor: ProcessorConfig, host: HostConfig,
                                  rabbitmq_url: str, mongodb_url: str) -> None:

        self.log.debug(f'deploy "{processor.deploy_type}" processor: "{processor}" on'
                       f'"{host.address}"')
        assert not processor.pids, 'processors already deployed. Pids are present. Host: ' \
                                   '{host.__dict__}. Processor: {processor.__dict__}'

        if processor.deploy_type == DeployType.native:
            if not host.ssh_client:
                host.ssh_client = create_ssh_client(host.address, host.username, host.password, host.keypath)
        elif processor.deploy_type == DeployType.docker:
            if not host.docker_client:
                host.docker_client = create_docker_client(host.address, host.username, host.password, host.keypath)
        else:
            # Error case, should never enter here. Handle error cases here (if needed)
            self.log.error(f"Deploy type of {processor.name} is neither of the allowed types")
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
                # Error case, should never enter here. Handle error cases here (if needed)
                self.log.error(f"Deploy type of {processor.name} is neither of the allowed types")
                pass

    def deploy_rabbitmq(self, image: str = 'rabbitmq', detach: bool = True, remove: bool = True,
                         ports_mapping: Union[Dict, None] = None) -> str:
        # This method deploys the RabbitMQ Server.
        # Handling of creation of queues, submitting messages to queues,
        # and receiving messages from queues is part of the RabbitMQ Library
        # Which is part of the OCR-D WebAPI implementation.

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
        # TODO: use rm here or not? Should queues be reused?
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping
        )
        assert res and res.id, 'starting rabbitmq failed'
        self.mq_data.pid = res.id
        client.close()
        self.log.debug('deployed rabbitmq')

        # Build the RabbitMQ Server URL to return
        rmq_host = self.mq_data.address
        rmq_port = self.mq_data.port
        rmq_vhost = "/"  # the default virtual host

        rabbitmq_url = f"{rmq_host}:{rmq_port}{rmq_vhost}"
        return rabbitmq_url

    def deploy_mongodb(self, image: str = 'mongo', detach: bool = True, remove: bool = True,
                        ports_mapping: Union[Dict, None] = None) -> str:
        if not self.mongo_data or not self.mongo_data.address:
            self.log.debug('canceled mongo-deploy: no mongo_db in config')
            return ""
        client = create_docker_client(self.mongo_data.address, self.mongo_data.username,
                                      self.mongo_data.password, self.mongo_data.keypath)
        if not ports_mapping:
            ports_mapping = {
                27017: self.mongo_data.port
            }
        # TODO: use rm here or not? Should the mongodb be reused?
        # TODO: what about the data-dir? Must data be preserved?
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping
        )
        assert res and res.id, 'starting mongodb failed'
        self.mongo_data.pid = res.id
        client.close()
        self.log.debug('deployed mongodb')

        # Build the MongoDB URL to return
        mongodb_prefix = "mongodb://"
        mongodb_host = self.mongo_data.address
        mongodb_port = self.mongo_data.port
        mongodb_url = f"{mongodb_prefix}{mongodb_host}:{mongodb_port}"
        return mongodb_url

    def kill_rabbitmq(self) -> None:
        if not self.mq_data.pid:
            self.log.debug('kill_rabbitmq: rabbitmq server is not running')
            return
        else:
            self.log.debug(f'trying to kill rabbitmq with id: {self.mq_data.pid} now')

        client = create_docker_client(self.mq_data.address, self.mq_data.username,
                                      self.mq_data.password, self.mq_data.keypath)
        client.containers.get(self.mq_data.pid).stop()
        self.mq_data.pid = None
        client.close()
        self.log.debug('stopped rabbitmq')

    def kill_mongodb(self) -> None:
        if not self.mongo_data or not self.mongo_data.pid:
            self.log.debug('kill_mongdb: mongodb not running')
            return
        else:
            self.log.debug(f'trying to kill mongdb with id: {self.mongo_data.pid} now')

        client = create_docker_client(self.mongo_data.address, self.mongo_data.username,
                                      self.mongo_data.password, self.mongo_data.keypath)
        client.containers.get(self.mongo_data.pid).stop()
        self.mongo_data.pid = None
        client.close()
        self.log.debug('stopped mongodb')

    def kill_hosts(self) -> None:
        # Kill processing hosts
        for host in self.hosts:
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
                    host.ssh_client.exec_command(f'kill {pid}')
            elif processor.deploy_type.is_docker():
                for pid in processor.pids:
                    self.log.debug(f'trying to kill docker container: {pid}')
                    # TODO: think about timeout.
                    #       think about using threads to kill parallelized to reduce waiting time
                    host.docker_client.containers.get(pid).stop()
            else:
                # Error case, should never enter here. Handle error cases here (if needed)
                self.log.error(f"Deploy type of {processor.name} is neither of the allowed types")
                pass
            processor.pids = []


    # TODO: queue_address and _database_address are prefixed with underscore because they are not
    # needed yet (otherwise flak8 complains). But they will be needed once the real
    # processing_worker is called here. Then they should be renamed
    @staticmethod
    def start_native_processor(client: SSHClient, processor_name: str, _queue_url: str,
                               _database_url: str) -> str:
        log = getLogger(__name__)
        log.debug(f'start native processor: {processor_name}')
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

    # TODO: queue_address and _database_address are prefixed with underscore because they are not
    # needed yet (otherwise flak8 complains). But they will be needed once the real
    # processing_worker is called here. Then they should be renamed
    @staticmethod
    def start_docker_processor(client: CustomDockerClient, processor_name: str, _queue_url: str,
                               _database_url: str) -> str:
        log = getLogger(__name__)
        log.debug(f'start docker processor: {processor_name}')
        # TODO: add real command here to start processing server here
        res = client.containers.run('debian', 'sleep 500', detach=True, remove=True)
        assert res and res.id, 'run processor in docker-container failed'
        return res.id
