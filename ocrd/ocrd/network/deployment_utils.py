from __future__ import annotations
from enum import Enum
from typing import Union

from docker import APIClient, DockerClient
from docker.transport import SSHHTTPAdapter
from paramiko import AutoAddPolicy, SSHClient
import urllib.parse

from ocrd_utils import getLogger


def create_ssh_client(address: str, username: str, password: Union[str, None],
                      keypath: Union[str, None]) -> SSHClient:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    log = getLogger(__name__)
    log.debug(f'creating ssh-client with username: "{username}", keypath: "{keypath}". '
              f'host: {address}')
    # TODO: connecting could easily fail here: wrong password, wrong path to keyfile etc. Maybe
    #       would be better to use except and try to give custom error message when failing
    client.connect(hostname=address, username=username, password=password, key_filename=keypath)
    return client


def create_docker_client(address: str, username: str, password: Union[str, None],
                         keypath: Union[str, None]) -> CustomDockerClient:
    return CustomDockerClient(username, address, password=password, keypath=keypath)


class CustomDockerClient(DockerClient):
    """Wrapper for docker.DockerClient to use an own SshHttpAdapter.

    This makes it possible to use provided password/keyfile for connecting with
    python-docker-sdk, which otherwise only allows to use ~/.ssh/config for
    login

    XXX: inspired by https://github.com/docker/docker-py/issues/2416 . Should be replaced when
    docker-sdk provides its own way to make it possible to use custom SSH Credentials. Possible
    Problems: APIClient must be given the API-version because it cannot connect prior to read it. I
    could imagine this could cause Problems
    """

    def __init__(self, user: str, host: str, **kwargs) -> None:
        # TODO: Call to the super class __init__ is missing here,
        #  may this potentially become an issue?
        if not user or not host:
            raise ValueError('Missing argument: user and host must both be provided')
        if not 'password' in kwargs and not 'keypath' in kwargs:
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
                raise Exception('either "password" or "keypath" must be provided')
            super().__init__(base_url)

        def _create_paramiko_client(self, base_url: str) -> None:
            """
            this method is called in the superclass constructor. Overwriting allows to set
            password/keypath for internal paramiko-client
            """
            self.ssh_client = SSHClient()
            parsed_base_url = urllib.parse.urlparse(base_url)
            self.ssh_params = {
                'hostname': parsed_base_url.hostname,
                'port': parsed_base_url.port,
                'username': parsed_base_url.username,
            }
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
