from __future__ import annotations
from enum import Enum
from docker import APIClient, DockerClient
from docker.transport import SSHHTTPAdapter
from paramiko import AutoAddPolicy, SSHClient
from time import sleep
import re

from .rabbitmq_utils import RMQPublisher
from pymongo import MongoClient

__all__ = [
    'create_docker_client',
    'create_ssh_client',
    'DeployType',
    'verify_mongodb_available',
    'verify_rabbitmq_available'
]


def create_ssh_client(address: str, username: str, password: str = "", keypath: str = "") -> SSHClient:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        client.connect(hostname=address, username=username, password=password, key_filename=keypath)
    except Exception as error:
        raise Exception(f"Error creating SSHClient of host '{address}', reason: {error}") from error
    return client


def create_docker_client(address: str, username: str, password: str = "", keypath: str = "") -> CustomDockerClient:
    return CustomDockerClient(username, address, password=password, keypath=keypath)


class CustomDockerClient(DockerClient):
    """Wrapper for docker.DockerClient to use an own SshHttpAdapter.

    This makes it possible to use provided password/keyfile for connecting with
    python-docker-sdk, which otherwise only allows to use ~/.ssh/config for
    login

    XXX: inspired by https://github.com/docker/docker-py/issues/2416 . Should be replaced when
    docker-sdk provides its own way to make it possible to use custom SSH Credentials. Possible
    Problems: APIClient must be given the API-version because it cannot connect prior to read it. I
    could imagine this could cause Problems. This is not a rushed implementation and was the only
    workaround I could find that allows password/keyfile to be used (by default only keyfile from
    ~/.ssh/config can be used to authenticate via ssh)

    XXX 2: Reasons to extend DockerClient: The code-changes regarding the connection should be in
    one place, so I decided to create `CustomSshHttpAdapter` as an inner class. The super
    constructor *must not* be called to make this workaround work. Otherwise, the APIClient
    constructor would be invoked without `version` and that would cause a connection-attempt before
    this workaround can be applied.
    """

    def __init__(self, user: str, host: str, **kwargs) -> None:
        # the super-constructor is not called on purpose: it solely instantiates the APIClient. The
        # missing `version` in that call would raise an error. APIClient is provided here as a
        # replacement for what the super-constructor does
        if not (user and host):
            raise ValueError('Missing argument: user and host must both be provided')
        if ('password' not in kwargs) != ('keypath' not in kwargs):
            raise ValueError('Missing argument: one of password and keyfile is needed')
        self.api = APIClient(f'ssh://{host}', use_ssh_client=True, version='1.41')
        ssh_adapter = self.CustomSshHttpAdapter(f'ssh://{user}@{host}:22', **kwargs)
        self.api.mount('http+docker://ssh', ssh_adapter)

    class CustomSshHttpAdapter(SSHHTTPAdapter):
        def __init__(self, base_url, password: str = "", keypath: str = "") -> None:
            self.password = password
            self.keypath = keypath
            if bool(self.password) == bool(self.keypath):
                raise Exception("Either 'password' or 'keypath' must be provided")
            super().__init__(base_url)

        def _create_paramiko_client(self, base_url: str) -> None:
            """
            this method is called in the superclass constructor. Overwriting allows to set
            password/keypath for the internal paramiko-client
            """
            super()._create_paramiko_client(base_url)
            if self.password:
                self.ssh_params['password'] = self.password
            elif self.keypath:
                self.ssh_params['key_filename'] = self.keypath
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy)


def verify_rabbitmq_available(
        host: str,
        port: int,
        vhost: str,
        username: str,
        password: str
) -> None:
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
    raise RuntimeError(f'Cannot connect to RabbitMQ host: {host}, port: {port}, '
                       f'vhost: {vhost}, username: {username}')


def verify_mongodb_available(mongo_url: str) -> None:
    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=1000.0)
        client.admin.command("ismaster")
    except Exception:
        raise RuntimeError(f'Cannot connect to MongoDB: {re.sub(r":[^@]+@", ":****@", mongo_url)}')


class DeployType(Enum):
    """ Deploy-Type of the processing worker/processor server.
    """
    DOCKER = 1
    NATIVE = 2
