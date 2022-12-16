
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
from typing import List


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
                self._deploy_native_processor(p, host)
            self._close_clients(host)

    def kill(self):
        self._kill_queue()
        for host in self.hosts:
            if not hasattr(host, "ssh_client") or not host.ssh_client:
                host.ssh_client = self._create_ssh_client(host.address, host.username,
                                                          host.password, host.keypath)
            for p in host.processors_native:
                for pid in p.pids:
                    host.ssh_client.exec_command(f"kill {pid}")
                p.pids = []

    def _deploy_native_processor(self, processor, host):
        """
        - client erstellen fals er nicht existiert (lazy)
        - start_native_processor aufrufen
        """
        assert not processor.pids, "processors already deployed. Pids are present. Host: " \
            "{host.__dict__}. Processor: {processor.__dict__}"
        if not hasattr(host, "ssh_client") or not host.ssh_client:
            host.ssh_client = self._create_ssh_client(host.address, host.username, host.password,
                                                      host.keypath)
        for _ in range(processor.count):
            pid = self._start_native_processor(host.ssh_client, processor.name, None, None)
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

    def _create_ssh_client(self, host, user, password, keypath):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        assert password or keypath, "password or keypath missing. Should have already been ensured"
        self.log.debug(f"creating ssh-client with username: '{user}', keypath: '{keypath}'. "
                       f"host: {host}")
        assert bool(password) is not bool(keypath), "expecting either password or keypath " \
            "provided, not both"
        client.connect(hostname=host, username=user, password=password, key_filename=keypath)
        # TODO: connecting could easily fail here: wrong password or wrong path to keyfile. Maybe it
        #       is better to use except and try to give custom error message

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
            self.log.debug("kill_queue: no queue running")
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
        self.password = config.password
        self.keypath = config.path_to_privkey
        self.processors_native = []
        self.processors_docker = []
        for x in config.deploy_processors:
            if x.deploy_type == DeployType.native:
                self.processors_native.append(
                    self.Processor(x.name, x.number_of_instance, DeployType.native)
                )
            else:
                self.processors_docker.append(
                    self.Processor(x.name, x.number_of_instance, DeployType.docker)
                )

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


class Config:
    """
    Class to hold the configuration for the ProcessingBroker

    The purpose of this class and its inner classes is to load the config and make its values
    accessible. This class and its attributes map 1:1 to the yaml-Config file
    """
    def __init__(self, config_path):
        with open(config_path) as fin:
            config = yaml.safe_load(fin)
        self.message_queue = Config.MessageQueue(**config["message_queue"])
        self.mongo_db = Config.MongoDb(**config["mongo_db"])
        self.hosts = []
        for d in config.get("hosts", []):
            self.hosts.append(Config.ConfigHost(**d))

    class MessageQueue:
        def __init__(self, address, port, credentials, ssh):
            self.address = address
            self.port = port
            if credentials:
                self.username = credentials["username"]
                self.password = credentials["password"]
            if ssh:
                self.username = ssh["username"]
                self.password = str(ssh["password"]) if "password" in ssh else None
                self.path_to_privkey = ssh.get("path_to_privkey", None)

    class MongoDb:
        def __init__(self, address, port, credentials, ssh):
            self.address = address
            self.port = port
            if credentials:
                self.username = credentials["username"]
                self.password = credentials["password"]
            if ssh:
                self.username = ssh["username"]
                self.password = str(ssh["password"]) if "password" in ssh else None
                self.path_to_privkey = ssh.get("path_to_privkey", None)

    class ConfigHost:
        def __init__(self, address, username, password=None, path_to_privkey=None,
                     deploy_processors=[]):
            self.address = address
            self.username = username
            self.password = str(password) if password is not None else None
            self.path_to_privkey = path_to_privkey
            self.deploy_processors = [
                self.__class__.ConfigDeployProcessor(**x) for x in deploy_processors
            ]

        class ConfigDeployProcessor:
            def __init__(self, name, deploy_type, number_of_instance=1):
                self.name = name
                self.number_of_instance = number_of_instance
                self.deploy_type = DeployType.from_str(deploy_type)


class DeployType(Enum):
    """
    Deploy-Type of the processing server. It can be started native or with docker
    """
    docker = 1
    native = 2

    @staticmethod
    def from_str(label: str):
        return DeployType[label.lower()]
