"""
Abstraction of the deployment functionality for processors.

The Processing Server provides the configuration parameters to the Deployer agent.
The Deployer agent runs the RabbitMQ Server, MongoDB and the Processing Hosts.
Each Processing Host may have several Processing Workers.
Each Processing Worker is an instance of an OCR-D processor.
"""

from __future__ import annotations
from typing import Dict, Union
from paramiko import SSHClient
from re import search as re_search
from os import getpid
from time import sleep


from ocrd_utils import getLogger
from .deployment_config import *
from .deployment_utils import (
    create_docker_client,
    create_ssh_client,
    CustomDockerClient,
    DeployType,
    HostData,
)
from .rabbitmq_utils import RMQPublisher


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

            # TODO: This is not optimal - the entire method should be refactored!
            if (any(s.deploy_type == DeployType.native for s in host.config.servers)
                    and not host.ssh_client):
                host.ssh_client = create_ssh_client(
                    host.config.address,
                    host.config.username,
                    host.config.password,
                    host.config.keypath
                )
            if (any(s.deploy_type == DeployType.docker for s in host.config.servers)
                    and not host.docker_client):
                host.docker_client = create_docker_client(
                    host.config.address,
                    host.config.username,
                    host.config.password,
                    host.config.keypath
                )

            for server in host.config.servers:
                self._deploy_processor_server(server, host, mongodb_url)

            if host.ssh_client:
                host.ssh_client.close()
            if host.docker_client:
                host.docker_client.close()

    def _deploy_processing_worker(self, processor: WorkerConfig, host: HostData,
                                  rabbitmq_url: str, mongodb_url: str) -> None:
        self.log.debug(f"deploy '{processor.deploy_type}' processing worker: '{processor.name}' on '{host.config.address}'")

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

    # TODO: Revisit this to remove code duplications of deploy_* methods
    def _deploy_processor_server(self, server: ProcessorServerConfig, host: HostData, mongodb_url: str) -> None:
        self.log.debug(f"deploy '{server.deploy_type}' processor server: '{server.name}' on '{host.config.address}'")
        if server.deploy_type == DeployType.native:
            assert host.ssh_client
            pid = self.start_native_processor_server(
                client=host.ssh_client,
                processor_name=server.name,
                agent_address=f'{host.config.address}:{server.port}',
                database_url=mongodb_url,
            )
            host.processor_server_pids_native.append(pid)

            if server.name in host.processor_server_ports:
                if host.processor_server_ports[server.name]:
                    host.processor_server_ports[server.name] = host.processor_server_ports[server.name].append(server.port)
                else:
                    host.processor_server_ports[server.name] = [server.port]
            else:
                host.processor_server_ports[server.name] = [server.port]
        else:
            raise Exception("Deploying docker processor server is not supported yet!")

    def deploy_rabbitmq(self, image: str, detach: bool, remove: bool,
                        ports_mapping: Union[Dict, None] = None) -> str:
        """Start docker-container with rabbitmq

        This method deploys the RabbitMQ Server. Handling of creation of queues, submitting messages
        to queues, and receiving messages from queues is part of the RabbitMQ Library which is part
        of the OCR-D WebAPI implementation.
        """
        self.log.debug(f"Trying to deploy '{image}', with modes: "
                       f"detach='{detach}', remove='{remove}'")

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
            # The default credentials to be used by the processing workers
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
                # TODO: Disconnect the dummy_publisher here before returning...
                return
        raise RuntimeError('Error waiting for queue startup: timeout exceeded')

    def deploy_mongodb(self, image: str, detach: bool, remove: bool,
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

        mongodb_hostinfo = f'{self.config.mongo.address}:{self.config.mongo.port}'
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
            self.kill_processing_workers(host)

            # Kill deployed Processor Server instances on this host
            self.kill_processor_servers(host)

    # TODO: Optimize the code duplication from start_* and kill_* methods
    def kill_processing_workers(self, host: HostData) -> None:
        amount = len(host.pids_native)
        if amount:
            self.log.info(f"Trying to kill/stop {amount} native processing workers:")
            for pid in host.pids_native:
                self.log.info(f"Native with PID: '{pid}'")
                host.ssh_client.exec_command(f'kill {pid}')
            host.pids_native = []
        amount = len(host.pids_docker)
        if amount:
            self.log.info(f"Trying to kill/stop {amount} docker processing workers:")
            for pid in host.pids_docker:
                self.log.info(f"Docker with PID: '{pid}'")
                host.docker_client.containers.get(pid).stop()
            host.pids_docker = []

    def kill_processor_servers(self, host: HostData) -> None:
        amount = len(host.processor_server_pids_native)
        if amount:
            self.log.info(f"Trying to kill/stop {amount} native processor servers:")
            for pid in host.processor_server_pids_native:
                self.log.info(f"Native with PID: '{pid}'")
                host.ssh_client.exec_command(f'kill {pid}')
            host.processor_server_pids_native = []
        amount = len(host.processor_server_pids_docker)
        if amount:
            self.log.info(f"Trying to kill/stop {amount} docker processor servers:")
            for pid in host.processor_server_pids_docker:
                self.log.info(f"Docker with PID: '{pid}'")
                host.docker_client.containers.get(pid).stop()
            host.processor_server_pids_docker = []

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
        self.log.info(f'Starting native processing worker: {processor_name}')
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        cmd = f'{processor_name} --agent_type worker --database {database_url} --queue {queue_url}'
        # the only way (I could find) to make it work to start a process in the background and
        # return early is this construction. The pid of the last started background process is
        # printed with `echo $!` but it is printed inbetween other output. Because of that I added
        # `xyz` before and after the code to easily be able to filter out the pid via regex when
        # returning from the function
        logpath = '/tmp/ocrd-processing-server-startup.log'
        stdin.write(f"echo starting processing worker with '{cmd}' >> '{logpath}'\n")
        stdin.write(f'{cmd} >> {logpath} 2>&1 &\n')
        stdin.write('echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        return re_search(r'xyz([0-9]+)xyz', output).group(1)  # type: ignore

    def start_docker_processor(self, client: CustomDockerClient, processor_name: str,
                               queue_url: str, database_url: str) -> str:

        # TODO: Raise an exception here as well?
        #  raise Exception("Deploying docker processing worker is not supported yet!")

        self.log.info(f'Starting docker container processor: {processor_name}')
        # TODO: add real command here to start processing server in docker here
        res = client.containers.run('debian', 'sleep 500s', detach=True, remove=True)
        assert res and res.id, f'Running processor: {processor_name} in docker-container failed'
        return res.id

    # TODO: Just a copy of the above start_native_processor() method.
    #  Far from being great... But should be good as a starting point
    def start_native_processor_server(self, client: SSHClient, processor_name: str, agent_address: str, database_url: str) -> str:
        self.log.info(f"Starting native processor server: {processor_name} on {agent_address}")
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        cmd = f'{processor_name} --agent_type server --agent_address {agent_address} --database {database_url}'
        port = agent_address.split(':')[1]
        logpath = f'/tmp/server_{processor_name}_{port}_{getpid()}.log'
        # TODO: This entire stdin/stdout thing is broken with servers!
        stdin.write(f"echo starting processor server with '{cmd}' >> '{logpath}'\n")
        stdin.write(f'{cmd} >> {logpath} 2>&1 &\n')
        stdin.write('echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        return re_search(r'xyz([0-9]+)xyz', output).group(1)  # type: ignore
        pass
