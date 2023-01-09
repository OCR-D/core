from __future__ import annotations
import docker
from docker.transport import SSHHTTPAdapter
from frozendict import frozendict
from functools import lru_cache, wraps
import paramiko
import urllib.parse
from ocrd_utils import (
    getLogger
)
from typing import Callable, Union, Any


# Method adopted from Triet's implementation
# https://github.com/OCR-D/core/pull/884/files#diff-8b69cb85b5ffcfb93a053791dec62a2f909a0669ae33d8a2412f246c3b01f1a3R260
def freeze_args(func: Callable) -> Callable:
    """
    Transform mutable dictionary into immutable. Useful to be compatible with cache
    Code taken from `this post <https://stackoverflow.com/a/53394430/1814420>`_
    """

    @wraps(func)
    def wrapped(*args, **kwargs) -> Callable:
        args = tuple([frozendict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


# Method adopted from Triet's implementation
# https://github.com/OCR-D/core/pull/884/files#diff-8b69cb85b5ffcfb93a053791dec62a2f909a0669ae33d8a2412f246c3b01f1a3R260
@freeze_args
@lru_cache(maxsize=32)
def get_processor(parameter: dict, processor_class: type) -> Union[type, None]:
    """
    Call this function to get back an instance of a processor. The results are cached based on the parameters.
    Args:
        parameter (dict): a dictionary of parameters.
        processor_class: the concrete `:py:class:~ocrd.Processor` class.
    Returns:
        When the concrete class of the processor is unknown, `None` is returned. Otherwise, an instance of the
        `:py:class:~ocrd.Processor` is returned.
    """
    if processor_class:
        dict_params = dict(parameter) if parameter else None
        return processor_class(workspace=None, parameter=dict_params)
    return None


def create_ssh_client(address: str, username: str, password: Union[str, None],
                      keypath: Union[str, None]) -> paramiko.SSHClient:
    assert address and username, 'address and username are mandatory'
    assert bool(password) is not bool(keypath), 'expecting either password or keypath, not both'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    log = getLogger(__name__)
    log.debug(f'creating ssh-client with username: "{username}", keypath: "{keypath}". '
              f'host: {address}')
    # TODO: connecting could easily fail here: wrong password, wrong path to keyfile etc. Maybe
    #       would be better to use except and try to give custom error message when failing
    client.connect(hostname=address, username=username, password=password, key_filename=keypath)
    return client


def create_docker_client(address: str, username: str, password: Union[str, None],
                         keypath: Union[str, None]) -> CustomDockerClient:
    assert address and username, 'address and username are mandatory'
    assert bool(password) is not bool(keypath), 'expecting either password or keypath ' \
                                                'provided, not both'
    return CustomDockerClient(username, address, password=password, keypath=keypath)


def close_clients(*args) -> None:
    for client in args:
        if hasattr(client, 'close') and callable(client.close):
            client.close()


class CustomDockerClient(docker.DockerClient):
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
        assert user and host, 'user and host must be set'
        assert 'password' in kwargs or 'keypath' in kwargs, 'one of password and keyfile is needed'
        self.api = docker.APIClient(f'ssh://{host}', use_ssh_client=True, version='1.41')
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
            self.ssh_client = paramiko.SSHClient()
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
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
