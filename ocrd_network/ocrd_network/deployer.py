"""
Abstraction of the deployment functionality for processors.

The Processing Server provides the configuration parameters to the Deployer agent.
The Deployer agent runs the RabbitMQ Server, MongoDB and the Processing Hosts.
Each Processing Host may have several Processing Workers.
Each Processing Worker is an instance of an OCR-D processor.
"""
from __future__ import annotations
from typing import Dict, List, Union
from re import search as re_search
from pathlib import Path
import subprocess
from time import sleep

from ocrd_utils import config, getLogger, safe_filename

from .constants import NETWORK_AGENT_SERVER, NETWORK_AGENT_WORKER
from .deployment_utils import (
    create_docker_client,
    DeployType,
    verify_mongodb_available,
    verify_rabbitmq_available,
)
from .logging import get_mets_server_logging_file_path
from .runtime_data import (
    DataHost,
    DataMongoDB,
    DataProcessingWorker,
    DataProcessorServer,
    DataRabbitMQ
)
from .utils import (
    is_mets_server_running,
    stop_mets_server,
    validate_and_load_config
)


class Deployer:
    def __init__(self, config_path: str) -> None:
        self.log = getLogger('ocrd_network.deployer')
        config = validate_and_load_config(config_path)

        self.data_mongo: DataMongoDB = DataMongoDB(config['database'])
        self.data_queue: DataRabbitMQ = DataRabbitMQ(config['process_queue'])
        self.data_hosts: List[DataHost] = []
        self.internal_callback_url = config.get('internal_callback_url', None)
        for config_host in config['hosts']:
            self.data_hosts.append(DataHost(config_host))
        self.mets_servers: Dict = {}  # {"mets_server_url": "mets_server_pid"}

    # TODO: Reconsider this.
    def find_matching_processors(
            self,
            worker_only: bool = False,
            server_only: bool = False,
            docker_only: bool = False,
            native_only: bool = False,
            str_names_only: bool = False,
            unique_only: bool = False
    ) -> Union[List[str], List[object]]:
        """Finds and returns a list of matching data objects of type:
        `DataProcessingWorker` and `DataProcessorServer`.

        :py:attr:`worker_only` match only processors with worker status
        :py:attr:`server_only` match only processors with server status
        :py:attr:`docker_only` match only docker processors
        :py:attr:`native_only` match only native processors
        :py:attr:`str_only` returns the processor_name instead of data object
        :py:attr:`unique_only` remove duplicates from the matches

        `worker_only` and `server_only` are mutually exclusive to each other
        `docker_only` and `native_only` are mutually exclusive to each other
        `unique_only` is allowed only together with `str_names_only`
        """

        if worker_only and server_only:
            raise ValueError(f"Only 'worker_only' or 'server_only' is allowed, not both.")
        if docker_only and native_only:
            raise ValueError(f"Only 'docker_only' or 'native_only' is allowed, not both.")
        if not str_names_only and unique_only:
            raise ValueError(f"Value 'unique_only' is allowed only together with 'str_names_only'")

        # Find all matching objects of type:
        # DataProcessingWorker or DataProcessorServer
        matched_objects = []
        for data_host in self.data_hosts:
            if not server_only:
                for data_worker in data_host.data_workers:
                    if data_worker.deploy_type == DeployType.NATIVE and docker_only:
                        continue
                    if data_worker.deploy_type == DeployType.DOCKER and native_only:
                        continue
                    matched_objects.append(data_worker)
            if not worker_only:
                for data_server in data_host.data_servers:
                    if data_server.deploy_type == DeployType.NATIVE and docker_only:
                        continue
                    if data_server.deploy_type == DeployType.DOCKER and native_only:
                        continue
                    matched_objects.append(data_server)
        if str_names_only:
            # gets only the processor names of the matched objects
            name_list = [match.processor_name for match in matched_objects]
            if unique_only:
                # removes the duplicates, if any
                return list(dict.fromkeys(name_list))
            return name_list
        return matched_objects

    def resolve_processor_server_url(self, processor_name) -> str:
        processor_server_url = ''
        for data_host in self.data_hosts:
            for data_server in data_host.data_servers:
                if data_server.processor_name == processor_name:
                    processor_server_url = f'http://{data_host.address}:{data_server.port}/'
        return processor_server_url

    def kill_all(self) -> None:
        """ kill all started services: hosts, database, queue

        The order of killing is important to optimize graceful shutdown in the future. If RabbitMQ
        server is killed before killing Processing Workers, that may have bad outcome and leave
        Processing Workers in an unpredictable state
        """
        self.kill_hosts()
        self.kill_mongodb()
        self.kill_rabbitmq()

    def deploy_hosts(
            self,
            mongodb_url: str,
            rabbitmq_url: str
    ) -> None:
        for host_data in self.data_hosts:
            if host_data.needs_ssh:
                host_data.create_client(client_type='ssh')
                assert host_data.ssh_client
            if host_data.needs_docker:
                host_data.create_client(client_type='docker')
                assert host_data.docker_client

            self.log.debug(f'Deploying processing workers on host: {host_data.address}')
            for data_worker in host_data.data_workers:
                self._deploy_processing_worker(
                    mongodb_url,
                    rabbitmq_url,
                    host_data,
                    data_worker
                )

            self.log.debug(f'Deploying processor servers on host: {host_data.address}')
            for data_server in host_data.data_servers:
                self._deploy_processor_server(
                    mongodb_url,
                    host_data,
                    data_server
                )

            if host_data.ssh_client:
                host_data.ssh_client.close()
                host_data.ssh_client = None
            if host_data.docker_client:
                host_data.docker_client.close()
                host_data.docker_client = None

    def _deploy_processing_worker(
            self,
            mongodb_url: str,
            rabbitmq_url: str,
            host_data: DataHost,
            data_worker: DataProcessingWorker
    ) -> None:
        self.log.debug(f"Deploying processing worker, "
                       f"environment: '{data_worker.deploy_type}', "
                       f"name: '{data_worker.processor_name}', "
                       f"address: '{host_data.address}'")

        if data_worker.deploy_type == DeployType.NATIVE:
            assert host_data.ssh_client  # to satisfy mypy
            pid = self.start_native_processor(
                ssh_client=host_data.ssh_client,
                processor_name=data_worker.processor_name,
                queue_url=rabbitmq_url,
                database_url=mongodb_url,
            )
            data_worker.pid = pid
        elif data_worker.deploy_type == DeployType.DOCKER:
            assert host_data.docker_client  # to satisfy mypy
            pid = self.start_docker_processor(
                docker_client=host_data.docker_client,
                processor_name=data_worker.processor_name,
                _queue_url=rabbitmq_url,
                _database_url=mongodb_url
            )
            data_worker.pid = pid
        sleep(0.2)

    # TODO: Revisit this to remove code duplications of deploy_* methods
    def _deploy_processor_server(
            self,
            mongodb_url: str,
            host_data: DataHost,
            data_server: DataProcessorServer,
    ) -> None:
        self.log.debug(f"Deploying processing worker, "
                       f"environment: '{data_server.deploy_type}', "
                       f"name: '{data_server.processor_name}', "
                       f"address: '{data_server.host}:{data_server.port}'")

        if data_server.deploy_type == DeployType.NATIVE:
            assert host_data.ssh_client
            pid = self.start_native_processor_server(
                ssh_client=host_data.ssh_client,
                processor_name=data_server.processor_name,
                agent_address=f'{data_server.host}:{data_server.port}',
                database_url=mongodb_url,
            )
            data_server.pid = pid

            if data_server.processor_name in host_data.server_ports:
                name = data_server.processor_name
                port = data_server.port
                if host_data.server_ports[name]:
                    host_data.server_ports[name] = host_data.server_ports[name].append(port)
                else:
                    host_data.server_ports[name] = [port]
            else:
                host_data.server_ports[data_server.processor_name] = [data_server.port]
        elif data_server.deploy_type == DeployType.DOCKER:
            raise Exception("Deploying docker processor server is not supported yet!")

    def deploy_rabbitmq(
            self,
            image: str,
            detach: bool,
            remove: bool,
            ports_mapping: Union[Dict, None] = None
    ) -> str:
        if self.data_queue.skip_deployment:
            self.log.debug(f"RabbitMQ is externaly managed. Skipping deployment")
            verify_rabbitmq_available(
                self.data_queue.address,
                self.data_queue.port,
                self.data_queue.vhost,
                self.data_queue.username,
                self.data_queue.password
            )
            return self.data_queue.url
        self.log.debug(f"Trying to deploy '{image}', with modes: "
                       f"detach='{detach}', remove='{remove}'")

        if not self.data_queue or not self.data_queue.address:
            raise ValueError('Deploying RabbitMQ has failed - missing configuration.')

        client = create_docker_client(
            self.data_queue.address,
            self.data_queue.ssh_username,
            self.data_queue.ssh_password,
            self.data_queue.ssh_keypath
        )
        if not ports_mapping:
            # 5672, 5671 - used by AMQP 0-9-1 and AMQP 1.0 clients without and with TLS
            # 15672, 15671: HTTP API clients, management UI and rabbitmq admin, without and with TLS
            # 25672: used for internode and CLI tools communication and is allocated from
            # a dynamic range (limited to a single port by default, computed as AMQP port + 20000)
            ports_mapping = {
                5672: self.data_queue.port,
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
                f'RABBITMQ_DEFAULT_USER={self.data_queue.username}',
                f'RABBITMQ_DEFAULT_PASS={self.data_queue.password}'
            ]
        )
        assert res and res.id, \
            f'Failed to start RabbitMQ docker container on host: {self.data_queue.address}'
        self.data_queue.pid = res.id
        client.close()

        rmq_host = self.data_queue.address
        rmq_port = int(self.data_queue.port)
        rmq_vhost = '/'

        verify_rabbitmq_available(
            host=rmq_host,
            port=rmq_port,
            vhost=rmq_vhost,
            username=self.data_queue.username,
            password=self.data_queue.password
        )
        self.log.info(f'The RabbitMQ server was deployed on URL: '
                      f'{rmq_host}:{rmq_port}{rmq_vhost}')
        return self.data_queue.url

    def deploy_mongodb(
            self,
            image: str,
            detach: bool,
            remove: bool,
            ports_mapping: Union[Dict, None] = None
    ) -> str:
        if self.data_mongo.skip_deployment:
            self.log.debug('MongoDB is externaly managed. Skipping deployment')
            verify_mongodb_available(self.data_mongo.url)
            return self.data_mongo.url

        self.log.debug(f"Trying to deploy '{image}', with modes: "
                       f"detach='{detach}', remove='{remove}'")

        if not self.data_mongo or not self.data_mongo.address:
            raise ValueError('Deploying MongoDB has failed - missing configuration.')

        client = create_docker_client(
            self.data_mongo.address,
            self.data_mongo.ssh_username,
            self.data_mongo.ssh_password,
            self.data_mongo.ssh_keypath
        )
        if not ports_mapping:
            ports_mapping = {
                27017: self.data_mongo.port
            }
        if self.data_mongo.username:
            environment = [
                f'MONGO_INITDB_ROOT_USERNAME={self.data_mongo.username}',
                f'MONGO_INITDB_ROOT_PASSWORD={self.data_mongo.password}'
            ]
        else:
            environment = []

        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports_mapping,
            environment=environment
        )
        if not res or not res.id:
            raise RuntimeError('Failed to start MongoDB docker container on host: '
                               f'{self.data_mongo.address}')
        self.data_mongo.pid = res.id
        client.close()

        mongodb_hostinfo = f'{self.data_mongo.address}:{self.data_mongo.port}'
        self.log.info(f'The MongoDB was deployed on host: {mongodb_hostinfo}')
        return self.data_mongo.url

    def kill_rabbitmq(self) -> None:
        if self.data_queue.skip_deployment:
            return
        elif not self.data_queue.pid:
            self.log.warning('No running RabbitMQ instance found')
            return
        client = create_docker_client(
            self.data_queue.address,
            self.data_queue.ssh_username,
            self.data_queue.ssh_password,
            self.data_queue.ssh_keypath
        )
        client.containers.get(self.data_queue.pid).stop()
        self.data_queue.pid = None
        client.close()
        self.log.info('The RabbitMQ is stopped')

    def kill_mongodb(self) -> None:
        if self.data_mongo.skip_deployment:
            return
        elif not self.data_mongo.pid:
            self.log.warning('No running MongoDB instance found')
            return
        client = create_docker_client(
            self.data_mongo.address,
            self.data_mongo.ssh_username,
            self.data_mongo.ssh_password,
            self.data_mongo.ssh_keypath
        )
        client.containers.get(self.data_mongo.pid).stop()
        self.data_mongo.pid = None
        client.close()
        self.log.info('The MongoDB is stopped')

    def kill_hosts(self) -> None:
        self.log.debug('Starting to kill/stop hosts')
        # Kill processing hosts
        for host_data in self.data_hosts:
            if host_data.needs_ssh:
                host_data.create_client(client_type='ssh')
                assert host_data.ssh_client
            if host_data.needs_docker:
                host_data.create_client(client_type='docker')
                assert host_data.docker_client

            self.log.debug(f'Killing/Stopping processing workers on host: {host_data.address}')
            self.kill_processing_workers(host_data)

            self.log.debug(f'Killing/Stopping processor servers on host: {host_data.address}')
            self.kill_processor_servers(host_data)

            if host_data.ssh_client:
                host_data.ssh_client.close()
                host_data.ssh_client = None
            if host_data.docker_client:
                host_data.docker_client.close()
                host_data.docker_client = None

    # TODO: Optimize the code duplication from start_* and kill_* methods
    def kill_processing_workers(self, host_data: DataHost) -> None:
        amount = len(host_data.data_workers)
        if not amount:
            self.log.info(f'No active processing workers to be stopped.')
            return
        self.log.info(f"Trying to stop {amount} processing workers:")
        for worker in host_data.data_workers:
            if not worker.pid:
                continue
            if worker.deploy_type == DeployType.NATIVE:
                host_data.ssh_client.exec_command(f'kill {worker.pid}')
                self.log.info(f"Stopped native worker with pid: '{worker.pid}'")
            elif worker.deploy_type == DeployType.DOCKER:
                host_data.docker_client.containers.get(worker.pid).stop()
                self.log.info(f"Stopped docker worker with container id: '{worker.pid}'")
        host_data.data_workers = []

    def kill_processor_servers(self, host_data: DataHost) -> None:
        amount = len(host_data.data_servers)
        if not amount:
            self.log.info(f'No active processor servers to be stopped.')
            return
        self.log.info(f"Trying to stop {amount} processing workers:")
        for server in host_data.data_servers:
            if not server.pid:
                continue
            if server.deploy_type == DeployType.NATIVE:
                host_data.ssh_client.exec_command(f'kill {server.pid}')
                self.log.info(f"Stopped native server with pid: '{server.pid}'")
            elif server.deploy_type == DeployType.DOCKER:
                host_data.docker_client.containers.get(server.pid).stop()
                self.log.info(f"Stopped docker server with container id: '{server.pid}'")
        host_data.data_servers = []

    def start_native_processor(
            self,
            ssh_client,
            processor_name: str,
            queue_url: str,
            database_url: str
    ) -> str:
        """ start a processor natively on a host via ssh

        Args:
            ssh_client:         paramiko SSHClient to execute commands on a host
            processor_name:     name of processor to run
            queue_url:          url to rabbitmq
            database_url:       url to database

        Returns:
            str: pid of running process
        """
        self.log.info(f'Starting native processing worker: {processor_name}')
        channel = ssh_client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        cmd = f'{processor_name} {NETWORK_AGENT_WORKER} --database {database_url} --queue {queue_url} &'
        # the only way (I could find) to make it work to start a process in the background and
        # return early is this construction. The pid of the last started background process is
        # printed with `echo $!` but it is printed inbetween other output. Because of that I added
        # `xyz` before and after the code to easily be able to filter out the pid via regex when
        # returning from the function

        self.log.debug(f'About to execute command: {cmd}')
        stdin.write(f'{cmd}\n')
        stdin.write('echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        return re_search(r'xyz([0-9]+)xyz', output).group(1)  # type: ignore

    def start_docker_processor(
            self,
            docker_client,
            processor_name: str,
            _queue_url: str,
            _database_url: str
    ) -> str:
        # TODO: Raise an exception here as well?
        #  raise Exception("Deploying docker processing worker is not supported yet!")

        self.log.info(f'Starting docker container processor: {processor_name}')
        # TODO: add real command here to start processing server in docker here
        res = docker_client.containers.run('debian', 'sleep 500s', detach=True, remove=True)
        assert res and res.id, f'Running processor: {processor_name} in docker-container failed'
        return res.id

    # TODO: Just a copy of the above start_native_processor() method.
    #  Far from being great... But should be good as a starting point
    def start_native_processor_server(
            self,
            ssh_client,
            processor_name: str,
            agent_address: str,
            database_url: str
    ) -> str:
        self.log.info(f"Starting native processor server: {processor_name} on {agent_address}")
        channel = ssh_client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        cmd = f'{processor_name} {NETWORK_AGENT_SERVER} --address {agent_address} --database {database_url} &'
        self.log.debug(f'About to execute command: {cmd}')
        stdin.write(f'{cmd}\n')
        stdin.write('echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        return re_search(r'xyz([0-9]+)xyz', output).group(1)  # type: ignore

    # TODO: No support for TCP version yet
    def start_unix_mets_server(self, mets_path: str) -> Path:
        log_file = get_mets_server_logging_file_path(mets_path=mets_path)
        mets_server_url = Path(config.OCRD_NETWORK_SOCKETS_ROOT_DIR, f"{safe_filename(mets_path)}.sock")

        if is_mets_server_running(mets_server_url=str(mets_server_url)):
            self.log.info(f"The mets server is already started: {mets_server_url}")
            return mets_server_url

        cwd = Path(mets_path).parent
        self.log.info(f'Starting UDS mets server: {mets_server_url}')
        sub_process = subprocess.Popen(
            args=['nohup', 'ocrd', 'workspace', '--mets-server-url', f'{mets_server_url}',
                  '-d', f'{cwd}', 'server', 'start'],
            shell=False,
            stdout=open(file=log_file, mode='w'),
            stderr=open(file=log_file, mode='a'),
            cwd=cwd,
            universal_newlines=True
        )
        # Wait for the mets server to start
        sleep(2)
        self.mets_servers[mets_server_url] = sub_process.pid
        return mets_server_url

    def stop_unix_mets_server(self, mets_server_url: str) -> None:
        self.log.info(f'Stopping UDS mets server: {mets_server_url}')
        if Path(mets_server_url) in self.mets_servers:
            mets_server_pid = self.mets_servers[Path(mets_server_url)]
        else:
            raise Exception(f"Mets server not found: {mets_server_url}")

        '''
        subprocess.run(
            args=['kill', '-s', 'SIGINT', f'{mets_server_pid}'],
            shell=False,
            universal_newlines=True
        )
        '''

        # TODO: Reconsider this again
        #  Not having this sleep here causes connection errors
        #  on the last request processed by the processing worker.
        #  Sometimes 3 seconds is enough, sometimes not.
        sleep(5)
        stop_mets_server(mets_server_url=mets_server_url)
