
import uvicorn
import yaml
from fastapi import FastAPI
import docker
import paramiko
import re
import os
from typing import List
import re
from enum import Enum
from dataclasses import dataclass
from ocrd_utils import (
    getLogger
)


class Deployer:
    """
    Class to wrap the deployment-functionality of the OCR-D Processing-Servers
    """

    def __init__(self, config):
        self.log = getLogger("ocrd.processingbroker")
        self.log.info("Deployer-init()")
        self.config = config
        self._started_processing_servers = {}
        self._message_queue_id = None

    def _create_docker_client_for_host(self, host_config):
        """
        Create a client for the specified host to do the docker deployment. Only if host contains
        processors to be deployed with docker

        Returns:
            Ready to use docker.DockerClient if host contains processing servers to be
            docker-deploed, None otherwise
        """
        if not any(x.type == Ptype.docker for x in host_config.processors):
            return None
        username = host_config.username
        hostname = host_config.address
        return self._create_docker_client(username, hostname)

    def _create_docker_client(self, username, hostname):
        docker_client = docker.DockerClient(base_url=f"ssh://{username}@{hostname}")
        return docker_client

    def _create_ssh_client(self, host, user, password, keypath):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        if password:
            client.connect(hostname=host, username=user, password=password)
        elif keypath:
            client.connect(hostname=host, username=user, key_filename=keypath)
        else:
            # TODO: think about using ~/.ssh/config or leave it like it is and remove this comment
            raise Exception("Deploy message queue: password or path_to_privkey must be provided")
        return client

    def _close_clients(self, *args):
        for client in args:
            if hasattr(client, "close") and callable(client.close):
                client.close()

    def _deploy_queue(self):
        # TODO: use docker-sdk here later
        client = self._create_ssh_client(
            self.config.message_queue.address, self.config.message_queue.username,
            self.config.message_queue.password, self.config.message_queue.path_to_privkey
        )
        port = self.config.message_queue.port

        # TODO: use rm here or not? Should queues be reused?
        _, stdout, _ = client.exec_command(f"docker run --rm -d -p {port}:5672 rabbitmq")
        container_id = stdout.read().decode('utf-8').strip()
        self._message_queue_id = container_id
        client.close()
        self.log.debug("deployed queue")

    def _kill_queue(self):
        if not self._message_queue_id:
            return

        client = self._create_ssh_client(
            self.config.message_queue.address, self.config.message_queue.username,
            self.config.message_queue.password, self.config.message_queue.path_to_privkey
        )
        # stopping container might take up to 10 Seconds
        client.exec_command(f"docker stop {self._message_queue_id}")
        self._message_queue_id = None
        client.close()
        self.log.debug("killed queue")

    def deploy(self):
        """
        Deploy the message queue and all processors defined in the config-file
        """
        if self._started_processing_servers or self._message_queue_id:
            raise Exception("The services have already been deployed")
        self._deploy_queue()
        for host in self.config.hosts:
            ssh_client = self._create_ssh_client(host.address, host.username, host.password,
                                                 host.path_to_privkey)
            for processor in [x for x in host.processors if x.type is Ptype.native]:
                count = processor.number_of_instance
                for _ in range(count):
                    res = self._start_native_processor(ssh_client, processor)
                    self._add_started_processing_server(host, res)
            self._close_clients(ssh_client)

    def kill(self):
        for host in self._started_processing_servers:
            services = self._started_processing_servers[host]
            ssh_client = self._create_ssh_client(
                services[0].address, services[0].username, services[0].password,
                services[0].path_to_privkey)
            for service in services:
                if service.type is Ptype.native:
                    self._kill_native_processor(ssh_client, service)
        self._kill_queue()
        self._started_processing_servers = {}

    def _add_started_processing_server(self, host, ps_infos):
        """
        add infos for a started processing server to the "reminder"
        """
        storage = self._started_processing_servers.setdefault(host.name, [])
        storage.append(RunningService(host.address, host.username, host.password,
                                      host.path_to_privkey, *ps_infos))

    def _start_native_processor(self, client, processor):
        self.log.debug(f"start native processor: {processor.__dict__}")
        assert processor.type == Ptype.native, "expected processor type to be 'native'"
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        # TODO: add real command to start processing server here
        cmd = "sleep 23s"
        stdin.write(f"{cmd} & \n echo xyz$!xyz \n exit \n")
        output = stdout.read().decode("utf-8")
        stdout.close()
        stdin.close()
        pid = re.search(r"xyz([0-9]+)xyz", output).group(1)
        return Ptype.native, pid

    def _kill_native_processor(self, client, running_service):
        assert running_service.type == Ptype.native, "expected processor type to be 'native'"
        client.exec_command(f"kill {running_service.identifier}")


class Config:
    """
    Class to hold the configuration for the ProcessingBroker

    The purpose of this class and its inner classes is to load the config and make its values
    accessible
    """
    def __init__(self, config_path):
        with open(config_path) as fin:
            config = yaml.safe_load(fin)
        self.message_queue = Config.MessageQueue(**config["message_queue"])
        self.hosts = []
        for d in config.get("hosts", []):
            assert len(d.items()) == 1
            for k, v in d.items():
                self.hosts.append(Config.Host(k, **v))

    class MessageQueue:
        def __init__(self, address, port, ssh):
            self.address = address
            self.port = port
            if ssh:
                self.username = ssh["username"]
                self.password = str(ssh["password"]) if "password" in ssh else None
                self.path_to_privkey = ssh.get("path_to_privkey", None)

    class Host:
        def __init__(self, name, address, username, password=None, path_to_privkey=None,
                     deploy_processors=[]):
            self.name = name
            self.address = address
            self.username = username
            self.password = str(password) if password is not None else None
            self.path_to_privkey = path_to_privkey
            self.processors = [self.__class__.Processor(**x) for x in deploy_processors]

        class Processor:
            def __init__(self, name, type, number_of_instance=1):
                self.name = name
                self.number_of_instance = number_of_instance
                self.type = Ptype.from_str(type)


class Ptype(Enum):
    """
    Type of the processing server. It can be started native or with docker
    """
    docker = 1
    native = 2

    @staticmethod
    def from_str(label: str):
        return Ptype[label.lower()]


@dataclass(eq=True, frozen=True)
class RunningService:
    """
    (Data-)Class to store all necessary information about a started processing server. Information
    is used to stop it later
    """
    address: str
    username: str
    password: str
    path_to_privkey: str
    type: Ptype
    identifier: str
