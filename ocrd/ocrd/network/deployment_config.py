# TODO: this probably breaks python 3.6. Think about whether we really want to use this
from __future__ import annotations
from typing import List, Dict

from ocrd.network.deployment_utils import DeployType

__all__ = [
    'ProcessingBrokerConfig',
    'HostConfig',
    'WorkerConfig',
    'MongoConfig',
    'QueueConfig',
]


class ProcessingBrokerConfig:
    def __init__(self, config: dict) -> None:
        self.mongo_config = MongoConfig(config['database'])
        self.queue_config = QueueConfig(config['process_queue'])
        self.hosts_config = []
        for host in config['hosts']:
            self.hosts_config.append(HostConfig(host))


class HostConfig:
    """Class to wrap information for all processing-worker-hosts.

    Config information and runtime information is stored here. This class
    should not do much but hold config information and runtime information. I
    hope to make the code better understandable this way. Deployer should still
    be the class who does things and this class here should be mostly passive
    """

    def __init__(self, config: dict) -> None:
        self.address = config['address']
        self.username = config['username']
        self.password = config.get('password', None)
        self.keypath = config.get('path_to_privkey', None)
        # TODO: this is only for testing. Remove here and from config.schema.yml after test/development-phase
        self.binpath = config.get('path_to_bin_dir', None)
        self.processors = []
        for worker in config['workers']:
            deploy_type = DeployType.from_str(worker['deploy_type'])
            self.processors.append(
                WorkerConfig(worker['name'], worker['number_of_instance'], deploy_type)
            )
        self.ssh_client = None
        self.docker_client = None


class WorkerConfig:
    """
    Class wrapping information from config file for an OCR-D processor
    """
    def __init__(self, name: str, count: int, deploy_type: DeployType) -> None:
        self.name = name
        self.count = count
        self.deploy_type = deploy_type
        self.pids: List = []

    def add_started_pid(self, pid) -> None:
        self.pids.append(pid)


class MongoConfig:
    """ Class to hold information for Mongodb-Docker container
    """

    def __init__(self, config: Dict) -> None:
        self.address = config['address']
        self.port = int(config['port'])
        self.username = config['ssh']['username']
        self.keypath = config['ssh'].get('path_to_privkey', None)
        self.password = config['ssh'].get('password', None)
        self.credentials = (config['credentials']['username'], config['credentials']['password'])
        self.pid = None


class QueueConfig:
    """ Class to hold information for RabbitMQ-Docker container
    """

    def __init__(self, config: Dict) -> None:
        self.address = config['address']
        self.port = int(config['port'])
        self.username = config['ssh']['username']
        self.keypath = config['ssh'].get('path_to_privkey', None)
        self.password = config['ssh'].get('password', None)
        self.credentials = (config['credentials']['username'], config['credentials']['password'])
        self.pid = None
