from __future__ import annotations
from docker import APIClient, DockerClient
from docker.transport import SSHHTTPAdapter
from paramiko import AutoAddPolicy, SSHClient


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
        # The super-constructor is not called on purpose. It solely instantiates the APIClient.
        # Missing 'version' in that call would raise an error.
        # The APIClient is provided here as a replacement for what the super-constructor does
        if not (user and host):
            raise ValueError("Missing 'user' and 'host' - both must be provided")
        if ("password" in kwargs) and ("keypath" in kwargs):
            if kwargs["password"] and kwargs["keypath"]:
                raise ValueError("Both 'password' and 'keypath' provided - one must be provided")
        if ("password" not in kwargs) and ("keypath" not in kwargs):
            raise ValueError("Missing 'password' or 'keypath' - one must be provided")
        self.api = APIClient(base_url=f"ssh://{host}", use_ssh_client=True, version="1.41")
        self.api.mount(
            prefix="http+docker://ssh", adapter=self.CustomSshHttpAdapter(base_url=f"ssh://{user}@{host}:22", **kwargs)
        )

    class CustomSshHttpAdapter(SSHHTTPAdapter):
        def __init__(self, base_url, password: str = "", keypath: str = "") -> None:
            self.password = password
            self.keypath = keypath
            if not self.password and not self.keypath:
                raise Exception("Missing 'password' or 'keypath' - one must be provided")
            if self.password and self.keypath:
                raise Exception("Both 'password' and 'keypath' provided - one must be provided")
            super().__init__(base_url)

        def _create_paramiko_client(self, base_url: str) -> None:
            """
            this method is called in the superclass constructor. Overwriting allows to set
            password/keypath for the internal paramiko-client
            """
            super()._create_paramiko_client(base_url)
            if self.password:
                self.ssh_params["password"] = self.password
            elif self.keypath:
                self.ssh_params["key_filename"] = self.keypath
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy)


def create_docker_client(address: str, username: str, password: str = "", keypath: str = "") -> CustomDockerClient:
    return CustomDockerClient(username, address, password=password, keypath=keypath)


def create_ssh_client(address: str, username: str, password: str = "", keypath: str = "") -> SSHClient:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        client.connect(hostname=address, username=username, password=password, key_filename=keypath)
    except Exception as error:
        raise Exception(f"Error creating SSHClient of host '{address}', reason: {error}") from error
    return client
