import yaml
import docker
from docker.transport import SSHHTTPAdapter
import paramiko
import re
from enum import Enum
from ocrd_utils import (
    getLogger
)
import urllib.parse


class Deployer:
    """
    Class to wrap the deployment-functionality of the OCR-D Processing-Servers

    Deployer is the one acting. Config is for represantation of the config-file only. DeployHost is
    for managing information, not for actually doing things.
    """

    def __init__(self, config):
        self.log = getLogger("ocrd.processingbroker")
        self.log.info("Deployer-init()")
        self.config = config
        self.hosts = Host.from_config(config)
        self._message_queue_id = None

    def deploy(self):
        """
        Deploy the message queue and all processors defined in the config-file
        """
        self._deploy_queue()
        for host in self.hosts:
            for p in host.processors_native:
                self._deploy_processor(p, host, DeployType.native)
            for p in host.processors_docker:
                self._deploy_processor(p, host, DeployType.docker)
            self._close_clients(host)

    def kill(self):
        self._kill_queue()
        for host in self.hosts:
            # TODO: provide function in host that does that so it is shorter and better to read
            if not hasattr(host, "ssh_client") or not host.ssh_client:
                host.ssh_client = self._create_ssh_client(host.address, host.username,
                                                          host.password, host.keypath)

            # TODO: provide function in host that does that so it is shorter and better to read
            if not hasattr(host, "docker_client") or not host.docker_client:
                host.docker_client = self._create_docker_client(host.address, host.username,
                                                                host.password, host.keypath)
            for p in host.processors_native:
                for pid in p.pids:
                    host.ssh_client.exec_command(f"kill {pid}")
                p.pids = []
            for p in host.processors_docker:
                for pid in p.pids:
                    self.log.debug(f"trying to kill docker container: {pid}")
                    # TODO: think about timeout. think about using threads to kill parallelize waiting time
                    host.docker_client.containers.get(pid).stop()
                p.pids = []

    def _deploy_processor(self, processor, host, deploy_type):
        self.log.debug(f"deploy '{deploy_type}' processor: '{processor}' on '{host.address}'")
        assert not processor.pids, "processors already deployed. Pids are present. Host: " \
            "{host.__dict__}. Processor: {processor.__dict__}"
        if deploy_type == DeployType.native:
            # TODO: provide function in host that does that so it is shorter and better to read
            if not hasattr(host, "ssh_client") or not host.ssh_client:
                # TODO: add function to host to get params as dict, then `**host.login_dict()`
                host.ssh_client = self._create_ssh_client(host.address, host.username,
                                                          host.password, host.keypath)
        else:
            # TODO: provide function in host that does that so it is shorter and better to read
            if not hasattr(host, "docker_client") or not host.docker_client:
                host.docker_client = self._create_docker_client(host.address, host.username,
                                                                host.password, host.keypath)
        for _ in range(processor.count):
            if deploy_type == DeployType.native:
                pid = self._start_native_processor(host.ssh_client, processor.name, None, None)
            else:
                pid = self._start_docker_processor(host.docker_client, processor.name, None, None)
            processor.add_started_pid(pid)

    def _start_native_processor(self, client, name, _queue_address, _database_address):
        self.log.debug(f"start native processor: {name}")
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        # TODO: add real command here to start processing server here
        cmd = "sleep 23s"
        stdin.write(f"{cmd} & \n echo xyz$!xyz \n exit \n")
        output = stdout.read().decode("utf-8")
        stdout.close()
        stdin.close()
        return re.search(r"xyz([0-9]+)xyz", output).group(1)

    def _start_docker_processor(self, client, name, _queue_address, _database_address):
        self.log.debug(f"start docker processor: {name}")
        # TODO: add real command here to start processing server here
        res = client.containers.run("debian", "sleep 31", detach=True, remove=True)
        assert res and res.id, "run docker container failed"
        return res.id

    def _create_ssh_client(self, address, user, password, keypath):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        assert password or keypath, "password or keypath missing. Should have already been ensured"
        self.log.debug(f"creating ssh-client with username: '{user}', keypath: '{keypath}'. "
                       f"host: {address}")
        assert bool(password) is not bool(keypath), "expecting either password or keypath " \
            "provided, not both"
        client.connect(hostname=address, username=user, password=password, key_filename=keypath)
        # TODO: connecting could easily fail here: wrong password or wrong path to keyfile. Maybe it
        #       is better to use except and try to give custom error message

        return client

    def _create_docker_client(self, address, user, password=None, keypath=None):
        assert bool(password) is not bool(keypath), "expecting either password or keypath " \
            "provided, not both"
        return CustomDockerClient(user, address, password=password, keypath=keypath)

    def _close_clients(self, *args):
        for client in args:
            if hasattr(client, "close") and callable(client.close):
                client.close()

    def _deploy_queue(self):
        # TODO: use docker-sdk here later
        mq_conf = self.config.message_queue
        client = self._create_ssh_client(
            mq_conf.address, mq_conf.ssh.username,
            mq_conf.ssh.password if hasattr(mq_conf.ssh, "password") else None,
            mq_conf.ssh.path_to_privkey if hasattr(mq_conf.ssh, "path_to_privkey") else None,
        )

        # TODO: use rm here or not? Should queues be reused?
        _, stdout, _ = client.exec_command(f"docker run --rm -d -p {mq_conf.port}:5672 rabbitmq")
        container_id = stdout.read().decode('utf-8').strip()
        self._message_queue_id = container_id
        client.close()
        self.log.debug("deployed queue")

    def _kill_queue(self):
        if not self._message_queue_id:
            self.log.debug("kill_queue: no queue running")
            return
        else:
            self.log.debug(f"trying to kill queue with id: {self._message_queue_id} now")

        # TODO: use docker sdk here later
        # TODO: code occures twice. dry
        mq_conf = self.config.message_queue
        client = self._create_ssh_client(
            mq_conf.address, mq_conf.ssh.username,
            mq_conf.ssh.password if hasattr(mq_conf.ssh, "password") else None,
            mq_conf.ssh.path_to_privkey if hasattr(mq_conf.ssh, "path_to_privkey") else None,
        )

        # stopping container might take up to 10 Seconds
        client.exec_command(f"docker stop {self._message_queue_id}")
        self._message_queue_id = None
        client.close()
        self.log.debug("killed queue")


class Host:
    """
    Class to wrap functionality and information to deploy processors to one Host.

    Class Config is for reading/storing the config only. Objects from DeployHost are build from the
    config and provide functionality to deploy the containers alongside the config-information

    This class should not do much but hold config information and runtime information. I hope to
    make the code better understandable this way. Deployer should still be the class who does things
    and this class here should be mostly passive
    """
    def __init__(self, config):
        self.address = config.address
        self.username = config.username
        self.password = config.password if hasattr(config, "password") else None
        self.keypath = config.path_to_privkey if hasattr(config, "path_to_privkey") else None
        assert self.password or self.keypath, "Host in configfile with neither password nor keyfile"
        self.processors_native = []
        self.processors_docker = []
        for x in config.deploy_processors:
            if x.deploy_type == 'native':
                self.processors_native.append(
                    self.Processor(x.name, x.number_of_instance, DeployType.native)
                )
            elif x.deploy_type == 'docker':
                self.processors_docker.append(
                    self.Processor(x.name, x.number_of_instance, DeployType.docker)
                )
            else:
                assert False, f"unknown deploy_type: '{x.deploy_type}'"

    @classmethod
    def from_config(cls, config):
        res = []
        for x in config.hosts:
            res.append(cls(x))
        return res

    class Processor:
        def __init__(self, name, count, deploy_type):
            self.name = name
            self.count = count
            self.deploy_type = deploy_type
            self.pids = []

        def add_started_pid(self, pid):
            self.pids.append(pid)


class Config():
    def __init__(self, d):
        """
        Class-represantation of the configuration-file for the ProcessingBroker
        """
        for k, v in d.items():
            if isinstance(v, dict):
                setattr(self, k, Config(v))
            elif isinstance(v, list) and len(v) and isinstance(v[0], dict):
                setattr(self, k, [Config(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, v)

    @classmethod
    def from_configfile(cls, path):
        with open(path) as fin:
            x = yaml.safe_load(fin)
        return cls(x)


class DeployType(Enum):
    """
    Deploy-Type of the processing server. It can be started native or with docker
    """
    docker = 1
    native = 2

    @staticmethod
    def from_str(label: str):
        return DeployType[label.lower()]


class CustomDockerClient(docker.DockerClient):
    """
    Wrapper for docker.DockerClient to use an own SshHttpAdapter. This makes it possible to use
    provided password/keyfile for connecting with python-docker-sdk, which otherwise only allows to
    use ~/.ssh/config for login

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
