from __future__ import annotations
from enum import Enum
from typing import Union, List
from distutils.spawn import find_executable as which
import re

from docker import APIClient, DockerClient
from docker.transport import SSHHTTPAdapter
from paramiko import AutoAddPolicy, SSHClient

from ocrd_utils import getLogger
from .deployment_config import *

__all__ = [
    'create_docker_client',
    'create_ssh_client',
    'CustomDockerClient',
    'DeployType',
    'HostData'
]


def create_ssh_client(address: str, username: str, password: Union[str, None],
                      keypath: Union[str, None]) -> SSHClient:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        client.connect(hostname=address, username=username, password=password, key_filename=keypath)
    except Exception:
        getLogger(__name__).error(f"Error creating SSHClient for host: '{address}'")
        raise
    return client


def create_docker_client(address: str, username: str, password: Union[str, None],
                         keypath: Union[str, None]) -> CustomDockerClient:
    return CustomDockerClient(username, address, password=password, keypath=keypath)


class HostData:
    """class to store runtime information for a host
    """
    def __init__(self, config: HostConfig) -> None:
        self.config = config
        self.ssh_client: Union[SSHClient, None] = None
        self.docker_client: Union[CustomDockerClient, None] = None
        self.pids_native: List[str] = []
        self.pids_docker: List[str] = []
        # TODO: Revisit this, currently just mimicking the old impl
        self.processor_server_pids_native: List[str] = []
        self.processor_server_pids_docker: List[str] = []
        # Key: processor_name, Value: list of ports
        self.processor_server_ports: dict = {}

    @staticmethod
    def from_config(config: List[HostConfig]) -> List[HostData]:
        res = []
        for host_config in config:
            res.append(HostData(host_config))
        return res


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
        if not user or not host:
            raise ValueError('Missing argument: user and host must both be provided')
        if 'password' not in kwargs and 'keypath' not in kwargs:
            raise ValueError('Missing argument: one of password and keyfile is needed')
        self.api = APIClient(f'ssh://{host}', use_ssh_client=True, version='1.41')
        ssh_adapter = self.CustomSshHttpAdapter(f'ssh://{user}@{host}:22', **kwargs)
        self.api.mount('http+docker://ssh', ssh_adapter)

    class CustomSshHttpAdapter(SSHHTTPAdapter):
        def __init__(self, base_url, password: Union[str, None] = None,
                     keypath: Union[str, None] = None) -> None:
            self.password = password
            self.keypath = keypath
            if not self.password and not self.keypath:
                raise Exception("either 'password' or 'keypath' must be provided")
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


class DeployType(Enum):
    """ Deploy-Type of the processing server.
    """
    docker = 1
    native = 2

    @staticmethod
    def from_str(label: str) -> DeployType:
        return DeployType[label.lower()]

    def is_native(self) -> bool:
        return self == DeployType.native

    def is_docker(self) -> bool:
        return self == DeployType.docker
