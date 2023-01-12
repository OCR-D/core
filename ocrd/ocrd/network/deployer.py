from __future__ import annotations
from typing import List, Dict, Union

from ocrd_utils import getLogger

from ocrd.network.deployment_config import *
from ocrd.network.deployment_utils import (
    create_docker_client,
    create_ssh_client,
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

    def deploy_all(self) -> None:
        """ Deploy the message queue and all processors defined in the config-file
        """
        # The order of deploying may be important to recover from previous state

        # Ideally, this should return the address of the RabbitMQ Server
        rabbitmq_address = self._deploy_rabbitmq()
        # Ideally, this should return the address of the MongoDB
        mongodb_address = self._deploy_mongodb()
        self._deploy_processing_workers(self.hosts, rabbitmq_address, mongodb_address)

    def kill_all(self) -> None:
        # The order of killing is important to optimize graceful shutdown in the future
        # If RabbitMQ server is killed before killing Processing Workers, that may have
        # bad outcome and leave Processing Workers in an unpredictable state

        # First kill the active Processing Workers
        # They may still want to update something in the db before closing
        # They may still want to nack the currently processed messages back to the RabbitMQ Server
        self._kill_processing_workers()

        # Second kill the MongoDB
        self._kill_mongodb()

        # Third kill the RabbitMQ Server
        self._kill_rabbitmq()

    def _deploy_processing_workers(self, hosts: List[HostConfig], rabbitmq_address: str,
                                   mongodb_address: str) -> None:
        for host in hosts:
            for processor in host.processors:
                self._deploy_processing_worker(processor, host, rabbitmq_address, mongodb_address)
            if host.ssh_client:
                host.ssh_client.close()
            if host.docker_client:
                host.docker_client.close()

    def _deploy_processing_worker(self, processor: ProcessorConfig, host: HostConfig,
                                  rabbitmq_server: str = '', mongodb: str = '') -> None:

        self.log.debug(f'deploy "{processor.deploy_type}" processor: "{processor}" on'
                       f'"{host.address}"')
        assert not processor.pids, 'processors already deployed. Pids are present. Host: ' \
                                   '{host.__dict__}. Processor: {processor.__dict__}'

        # Create the specific RabbitMQ queue here based on the OCR-D processor name (processor.name)
        # self.rmq_publisher.create_queue(queue_name=processor.name)

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
                pid = ProcessingWorker.start_native_processor(
                    client=host.ssh_client,
                    name=processor.name,
                    _queue_address=rabbitmq_server,
                    _database_address=mongodb)
                processor.add_started_pid(pid)
            elif processor.deploy_type == DeployType.docker:
                assert host.docker_client  # to satisfy mypy
                pid = ProcessingWorker.start_docker_processor(
                    client=host.docker_client,
                    name=processor.name,
                    _queue_address=rabbitmq_server,
                    _database_address=mongodb)
                processor.add_started_pid(pid)
            else:
                # Error case, should never enter here. Handle error cases here (if needed)
                self.log.error(f"Deploy type of {processor.name} is neither of the allowed types")
                pass

    def _deploy_rabbitmq(self, image: str = 'rabbitmq', detach: bool = True, remove: bool = True,
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

        # TODO: Not implemented yet
        #  Note: The queue address is not just the IP address
        queue_address = 'RabbitMQ Server address'
        return queue_address

    def _deploy_mongodb(self, image: str = 'mongo', detach: bool = True, remove: bool = True,
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

        # TODO: Not implemented yet
        #  Note: The mongodb address is not just the IP address
        mongodb_address = 'MongoDB Address'
        return mongodb_address

    def _kill_rabbitmq(self) -> None:
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

    def _kill_mongodb(self) -> None:
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

    def _kill_processing_workers(self) -> None:
        # Kill processing worker hosts
        for host in self.hosts:
            if host.ssh_client:
                host.ssh_client = create_ssh_client(host.address, host.username, host.password, host.keypath)
            if host.docker_client:
                host.docker_client = create_docker_client(host.address, host.username, host.password, host.keypath)
            # Kill deployed OCR-D processor instances on this Processing worker host
            self._kill_processing_worker(host)

    def _kill_processing_worker(self, host: HostConfig) -> None:
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
