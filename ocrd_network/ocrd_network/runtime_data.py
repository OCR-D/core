from __future__ import annotations
from typing import Dict, List

from .deployment_utils import (
    create_docker_client,
    create_ssh_client,
    DeployType
)

__all__ = [
    'DataHost',
    'DataMongoDB',
    'DataProcessingWorker',
    'DataProcessorServer',
    'DataRabbitMQ'
]


class DataHost:
    def __init__(self, config: Dict) -> None:
        self.address = config['address']
        self.username = config['username']
        self.password = config.get('password', None)
        self.keypath = config.get('path_to_privkey', None)

        # These flags are used to track whether a connection
        # of the specified type will be required
        self.needs_ssh: bool = False
        self.needs_docker: bool = False

        self.ssh_client = None
        self.docker_client = None

        # TODO: Not sure this is DS is ideal, seems off
        self.data_workers: List[DataProcessingWorker] = []
        self.data_servers: List[DataProcessorServer] = []

        for worker in config.get('workers', []):
            name = worker['name']
            count = worker['number_of_instance']
            deploy_type = DeployType.DOCKER if worker.get('deploy_type', None) == 'docker' else DeployType.NATIVE
            if not self.needs_ssh and deploy_type == DeployType.NATIVE:
                self.needs_ssh = True
            if not self.needs_docker and deploy_type == DeployType.DOCKER:
                self.needs_docker = True
            for _ in range(count):
                self.data_workers.append(DataProcessingWorker(self.address, deploy_type, name))

        for server in config.get('servers', []):
            name = server['name']
            port = server['port']
            deploy_type = DeployType.DOCKER if server.get('deploy_type', None) == 'docker' else DeployType.NATIVE
            if not self.needs_ssh and deploy_type == DeployType.NATIVE:
                self.needs_ssh = True
            if not self.needs_docker and deploy_type == DeployType.DOCKER:
                self.needs_docker = True
            self.data_servers.append(DataProcessorServer(self.address, port, deploy_type, name))

        # Key: processor_name, Value: list of ports
        self.server_ports: dict = {}

    def create_client(self, client_type: str):
        if client_type not in ['docker', 'ssh']:
            raise ValueError(f'Host client type cannot be of type: {client_type}')
        if client_type == 'ssh':
            if not self.ssh_client:
                self.ssh_client = create_ssh_client(
                    self.address, self.username, self.password, self.keypath)
            return self.ssh_client
        if client_type == 'docker':
            if not self.docker_client:
                self.docker_client = create_docker_client(
                    self.address, self.username, self.password, self.keypath
                )
            return self.docker_client


class DataProcessingWorker:
    def __init__(self, host: str, deploy_type: DeployType, processor_name: str) -> None:
        self.host = host
        self.deploy_type = deploy_type
        self.processor_name = processor_name
        # Assigned when deployed
        self.pid = None


class DataProcessorServer:
    def __init__(self, host: str, port: int, deploy_type: DeployType, processor_name: str) -> None:
        self.host = host
        self.port = port
        self.deploy_type = deploy_type
        self.processor_name = processor_name
        # Assigned when deployed
        self.pid = None


class DataMongoDB:
    def __init__(self, config: Dict) -> None:
        self.address = config['address']
        self.port = int(config['port'])
        if 'ssh' in config:
            self.ssh_username = config['ssh']['username']
            self.ssh_keypath = config['ssh'].get('path_to_privkey', None)
            self.ssh_password = config['ssh'].get('password', None)
        else:
            self.ssh_username = None
            self.ssh_keypath = None
            self.ssh_password = None

        if 'credentials' in config:
            self.username = config['credentials']['username']
            self.password = config['credentials']['password']
            self.url = f'mongodb://{self.username}:{self.password}@{self.address}:{self.port}'
        else:
            self.username = None
            self.password = None
            self.url = f'mongodb://{self.address}:{self.port}'
        self.skip_deployment = config.get('skip_deployment', False)
        # Assigned when deployed
        self.pid = None


class DataRabbitMQ:
    def __init__(self, config: Dict) -> None:
        self.address = config['address']
        self.port = int(config['port'])
        if 'ssh' in config:
            self.ssh_username = config['ssh']['username']
            self.ssh_keypath = config['ssh'].get('path_to_privkey', None)
            self.ssh_password = config['ssh'].get('password', None)
        else:
            self.ssh_username = None
            self.ssh_keypath = None
            self.ssh_password = None

        self.vhost = '/'
        self.username = config['credentials']['username']
        self.password = config['credentials']['password']
        self.url = f'amqp://{self.username}:{self.password}@{self.address}:{self.port}{self.vhost}'
        self.skip_deployment = config.get('skip_deployment', False)
        # Assigned when deployed
        self.pid = None
