import docker
from docker.transport import SSHHTTPAdapter
import paramiko
import urllib.parse
from ocrd_utils import (
    getLogger
)


def create_ssh_client(obj):
    address, username, password, keypath = obj.address, obj.username, obj.password, obj.keypath
    assert address and username, "address and username are mandatory"
    assert bool(password) is not bool(keypath), "expecting either password or keypath, not both"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    log = getLogger("ocrd.create_ssh_client")
    log.debug(f"creating ssh-client with username: '{username}', keypath: '{keypath}'. "
              f"host: {address}")
    # TODO: connecting could easily fail here: wrong password, wrong path to keyfile etc. Maybe
    #       would be better to use except and try to give custom error message when failing
    client.connect(hostname=address, username=username, password=password, key_filename=keypath)
    return client


def create_docker_client(obj):
    address, username, password, keypath = obj.address, obj.username, obj.password, obj.keypath
    assert address and username, "address and username are mandatory"
    assert bool(password) is not bool(keypath), "expecting either password or keypath " \
                                                "provided, not both"
    return CustomDockerClient(username, address, password=password, keypath=keypath)


def close_clients(*args):
    for client in args:
        if hasattr(client, "close") and callable(client.close):
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

    def __init__(self, user, host, **kwargs):
        assert user and host, "user and host must be set"
        assert "password" in kwargs or "keypath" in kwargs, "one of password and keyfile is needed"
        self.api = docker.APIClient(f"ssh://{host}", use_ssh_client=True, version='1.41')
        ssh_adapter = self.CustomSshHttpAdapter(f"ssh://{user}@{host}:22", **kwargs)
        self.api.mount('http+docker://ssh', ssh_adapter)

    class CustomSshHttpAdapter(SSHHTTPAdapter):
        def __init__(self, base_url, password=None, keypath=None):
            self.password = password
            self.keypath = keypath
            if not self.password and not self.keypath:
                raise Exception("either 'password' or 'keypath' must be provided")
            super().__init__(base_url)

        def _create_paramiko_client(self, base_url):
            """
            this method is called in the superclass constructor. Overwriting allows to set
            password/keypath for internal paramiko-client
            """
            self.ssh_client = paramiko.SSHClient()
            base_url = urllib.parse.urlparse(base_url)
            self.ssh_params = {
                "hostname": base_url.hostname,
                "port": base_url.port,
                "username": base_url.username,
            }
            if self.password:
                self.ssh_params["password"] = self.password
            elif self.keypath:
                self.ssh_params["key_filename"] = self.keypath
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
