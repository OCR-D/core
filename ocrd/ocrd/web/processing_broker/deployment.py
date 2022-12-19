
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
        self.log.debug("deploy native processor: '{processor}' on '{host.address}'")
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
