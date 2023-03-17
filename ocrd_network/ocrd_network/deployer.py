"""
Abstraction of the deployment functionality for processors.

The Processing Server provides the configuration parameters to the Deployer agent.
The Deployer agent runs the RabbitMQ Server, MongoDB and the Processing Hosts.
Each Processing Host may have several Processing Workers.
Each Processing Worker is an instance of an OCR-D processor.
"""

from __future__ import annotations
from typing import Dict, Union, Optional
from paramiko import SSHClient
from pathlib import Path
from re import search as re_search
from time import sleep


from ocrd_utils import getLogger
from ocrd_network.deployment_config import *
from ocrd_network.deployment_utils import (
    create_docker_client,
    create_ssh_client,
    CustomDockerClient,
    DeployType,
    HostData,
    is_bashlib_processor,
)
from ocrd_network.rabbitmq_utils import RMQPublisher


class Deployer:
    """Wraps the deployment functionality of the Processing Server

    Deployer is the one acting.
    :py:attr:`config` is for representation of the config file only.
    :py:attr:`hosts` is for managing processor information, not for actually processing.
    """

    def __init__(self, config: ProcessingServerConfig) -> None:
        """
        Args:
            config (:py:class:`ProcessingServerConfig`): parsed configuration of the Processing Server
        """
        self.log = getLogger(__name__)
        self.config = config
        self.hosts = HostData.from_config(config.hosts)
        self.mongo_pid = None
        self.mq_pid = None

    def kill_all(self) -> None:
        """ kill all started services: workers, database, queue

        The order of killing is important to optimize graceful shutdown in the future. If RabbitMQ
        server is killed before killing Processing Workers, that may have bad outcome and leave
        Processing Workers in an unpredictable state
        """
        self.kill_hosts()
        self.kill_mongodb()
        self.kill_rabbitmq()

    def deploy_hosts(self, rabbitmq_url: str, mongodb_url: str) -> None:
        for host in self.hosts:
            self.log.debug(f'Deploying processing workers on host: {host.config.address}')

            if (any(p.deploy_type == DeployType.native for p in host.config.processors)
                    and not host.ssh_client):
                host.ssh_client = create_ssh_client(
                    host.config.address,
                    host.config.username,
                    host.config.password,
                    host.config.keypath
                )
            if (any(p.deploy_type == DeployType.docker for p in host.config.processors)
                    and not host.docker_client):
                host.docker_client = create_docker_client(
                    host.config.address,
                    host.config.username,
                    host.config.password,
                    host.config.keypath
                )

            for processor in host.config.processors:
                self._deploy_processing_worker(processor, host, rabbitmq_url, mongodb_url)

            if host.ssh_client:
                host.ssh_client.close()
            if host.docker_client:
                host.docker_client.close()

    def _deploy_processing_worker(self, processor: WorkerConfig, host: HostData,
                                  rabbitmq_url: str, mongodb_url: str) -> None:

        self.log.debug(f"deploy '{processor.deploy_type}' processor: '{processor}' on '{host.config.address}'")

        for _ in range(processor.count):
            if processor.deploy_type == DeployType.native:
                assert host.ssh_client  # to satisfy mypy
                pid = self.start_native_processor(
                    client=host.ssh_client,
                    processor_name=processor.name,
                    queue_url=rabbitmq_url,
                    database_url=mongodb_url,
                )
                host.pids_native.append(pid)
            else:
                assert processor.deploy_type == DeployType.docker
                assert host.docker_client  # to satisfy mypy
                pid = self.start_docker_processor(
                    client=host.docker_client,
                    processor_name=processor.name,
                    queue_url=rabbitmq_url,
                    database_url=mongodb_url
                )
                host.pids_docker.append(pid)
            sleep(0.1)

    def deploy_rabbitmq(self, image: str = 'rabbitmq:3-management', detach: bool = True,
                        remove: bool = True, ports_mapping: Union[Dict, None] = None) -> str:
        """Start docker-container with rabbitmq

        This method deploys the RabbitMQ Server. Handling of creation of queues, submitting messages
        to queues, and receiving messages from queues is part of the RabbitMQ Library which is part
        of the OCR-D WebAPI implementation.
        """
        self.log.debug(f'Trying to deploy image[{image}], '
                       f'with modes: detach[{detach}], remove[{remove}]')

        if not self.config or not self.config.queue.address:
            raise ValueError('Deploying RabbitMQ has failed - missing configuration.')

        client = create_docker_client(self.config.queue.address, self.config.queue.username,
                                      self.config.queue.password, self.config.queue.keypath)
        if not ports_mapping:
            # 5672, 5671 - used by AMQP 0-9-1 and AMQP 1.0 clients without and with TLS
            # 15672, 15671: HTTP API clients, management UI and rabbitmq admin, without and with TLS
            # 25672: used for internode and CLI tools communication and is allocated from
            # a dynamic range (limited to a single port by default, computed as AMQP port + 20000)
            ports_mapping = {
                5672: self.config.queue.port,
                15672: 15672,
                25672: 25672
            }
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping,
            environment=[
                f'RABBITMQ_DEFAULT_USER={self.config.queue.credentials[0]}',
                f'RABBITMQ_DEFAULT_PASS={self.config.queue.credentials[1]}'
            ]
        )
        assert res and res.id, \
            f'Failed to start RabbitMQ docker container on host: {self.config.mongo.address}'
        self.mq_pid = res.id
        client.close()

        # Build the RabbitMQ Server URL to return
        rmq_host = self.config.queue.address
        # note, integer validation is already performed
        rmq_port = int(self.config.queue.port)
        # the default virtual host since no field is
        # provided in the processing server config.yml
        rmq_vhost = '/'

        self.wait_for_rabbitmq_availability(rmq_host, rmq_port, rmq_vhost,
                                            self.config.queue.credentials[0],
                                            self.config.queue.credentials[1])

        rabbitmq_hostinfo = f'{rmq_host}:{rmq_port}{rmq_vhost}'
        self.log.info(f'The RabbitMQ server was deployed on host: {rabbitmq_hostinfo}')
        return rabbitmq_hostinfo

    def wait_for_rabbitmq_availability(self, host: str, port: int, vhost: str, username: str,
                                       password: str) -> None:
        max_waiting_steps = 15
        while max_waiting_steps > 0:
            try:
                dummy_publisher = RMQPublisher(host=host, port=port, vhost=vhost)
                dummy_publisher.authenticate_and_connect(username=username, password=password)
            except Exception:
                max_waiting_steps -= 1
                sleep(2)
            else:
                return
        raise RuntimeError('Error waiting for queue startup: timeout exceeded')

    def deploy_mongodb(self, image: str = 'mongo', detach: bool = True, remove: bool = True,
                       ports_mapping: Union[Dict, None] = None) -> str:
        """ Start mongodb in docker
        """
        self.log.debug(f"Trying to deploy '{image}', with modes: "
                       f"detach='{detach}', remove='{remove}'")

        if not self.config or not self.config.mongo.address:
            raise ValueError('Deploying MongoDB has failed - missing configuration.')

        client = create_docker_client(self.config.mongo.address, self.config.mongo.username,
                                      self.config.mongo.password, self.config.mongo.keypath)
        if not ports_mapping:
            ports_mapping = {
                27017: self.config.mongo.port
            }
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping
        )
        if not res or not res.id:
            raise RuntimeError('Failed to start MongoDB docker container on host: '
                               f'{self.config.mongo.address}')
        self.mongo_pid = res.id
        client.close()

        mongodb_host = self.config.mongo.address
        mongodb_port = self.config.mongo.port
        mongodb_hostinfo = f'{mongodb_host}:{mongodb_port}'
        self.log.info(f'The MongoDB was deployed on host: {mongodb_hostinfo}')
        return mongodb_hostinfo

    def kill_rabbitmq(self) -> None:
        if not self.mq_pid:
            self.log.warning('No running RabbitMQ instance found')
            return
        client = create_docker_client(self.config.queue.address, self.config.queue.username,
                                      self.config.queue.password, self.config.queue.keypath)
        client.containers.get(self.mq_pid).stop()
        self.mq_pid = None
        client.close()
        self.log.info('The RabbitMQ is stopped')

    def kill_mongodb(self) -> None:
        if not self.mongo_pid:
            self.log.warning('No running MongoDB instance found')
            return
        client = create_docker_client(self.config.mongo.address, self.config.mongo.username,
                                      self.config.mongo.password, self.config.mongo.keypath)
        client.containers.get(self.mongo_pid).stop()
        self.mongo_pid = None
        client.close()
        self.log.info('The MongoDB is stopped')

    def kill_hosts(self) -> None:
        self.log.debug('Starting to kill/stop hosts')
        # Kill processing hosts
        for host in self.hosts:
            self.log.debug(f'Killing/Stopping processing workers on host: {host.config.address}')
            if host.ssh_client:
                host.ssh_client = create_ssh_client(host.config.address, host.config.username,
                                                    host.config.password, host.config.keypath)
            if host.docker_client:
                host.docker_client = create_docker_client(host.config.address, host.config.username,
                                                          host.config.password, host.config.keypath)
            # Kill deployed OCR-D processor instances on this Processing worker host
            self.kill_processing_worker(host)

    def kill_processing_worker(self, host: HostData) -> None:
        for pid in host.pids_native:
            self.log.debug(f"Trying to kill/stop native processor: with PID: '{pid}'")
            host.ssh_client.exec_command(f'kill {pid}')
        host.pids_native = []

        for pid in host.pids_docker:
            self.log.debug(f"Trying to kill/stop docker container with PID: '{pid}'")
            host.docker_client.containers.get(pid).stop()
        host.pids_docker = []

    def start_native_processor(self, client: SSHClient, processor_name: str, queue_url: str,
                               database_url: str) -> str:
        """ start a processor natively on a host via ssh

        Args:
            client:             paramiko SSHClient to execute commands on a host
            processor_name:     name of processor to run
            queue_url:          url to rabbitmq
            database_url:       url to database

        Returns:
            str: pid of running process
        """
        self.log.info(f'Starting native processor: {processor_name}')
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        if is_bashlib_processor(processor_name):
            cmd = f'ocrd processing-worker {processor_name} --database {database_url} ' \
                f'--queue {queue_url}'
        else:
            cmd = f'{processor_name} --database {database_url} --queue {queue_url}'
        # the only way (I could find) to make it work to start a process in the background and
        # return early is this construction. The pid of the last started background process is
        # printed with `echo $!` but it is printed inbetween other output. Because of that I added
        # `xyz` before and after the code to easily be able to filter out the pid via regex when
        # returning from the function
        logpath = '/tmp/ocrd-processing-server-startup.log'
        stdin.write(f"echo starting processor with '{cmd}' >> '{logpath}'\n")
        stdin.write(f'{cmd} >> {logpath} 2>&1 &\n')
        stdin.write('echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        return re_search(r'xyz([0-9]+)xyz', output).group(1)  # type: ignore

    def start_docker_processor(self, client: CustomDockerClient, processor_name: str,
                               queue_url: str, database_url: str) -> str:
        self.log.info(f'Starting docker container processor: {processor_name}')
        # TODO: add real command here to start processing server in docker here
        res = client.containers.run('debian', 'sleep 500s', detach=True, remove=True)
        assert res and res.id, f'Running processor: {processor_name} in docker-container failed'
        return res.id
