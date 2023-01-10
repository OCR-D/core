# TODO: this probably breaks python 3.6. Think about whether we really want to use this
from __future__ import annotations
from ocrd.network.deployment_utils import DeployType
from typing import List, Dict

__all__ = [
    'HostConfig',
    'ProcessorConfig',
    'MongoConfig',
    'QueueConfig',
]


class HostConfig:
    """Class to wrap information for all processing-server-hosts.

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
        self.processors = []
        for processor in config['deploy_processors']:
            deploy_type = DeployType.from_str(processor['deploy_type'])
            self.processors.append(
                ProcessorConfig(processor['name'], processor['number_of_instance'], deploy_type)
            )
        self.ssh_client = None
        self.docker_client = None

    @staticmethod
    def from_config(config: Dict) -> List:
        res = []
        for host in config['hosts']:
            res.append(HostConfig(host))
        return res


class ProcessorConfig:
    """ Class wrapping information from config file for a Processing-Server/Worker
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
