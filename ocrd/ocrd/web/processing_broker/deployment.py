import docker
from docker.transport import SSHHTTPAdapter
import paramiko
import re
from enum import Enum
from ocrd_utils import (
    getLogger
)
import urllib.parse


# TODO: remove debug log statements before beta, their purpose is development only
class Deployer:
    """ Class to wrap the deployment-functionality of the OCR-D Processing-Servers

    Deployer is the one acting. Config is for representation of the config-file only. DeployHost is
    for managing information, not for actually doing things.
    """

    def __init__(self, config):
        """
        Args:
            config (Config): values from config file wrapped into class `Config`
        """
        self.log = getLogger("ocrd.processingbroker")
        self.log.debug("Deployer-init()")
        self.mongo_data = MongoData(config["mongo_db"])
        self.mq_data = QueueData(config["message_queue"])
        self.hosts = HostData.from_config(config)

    def deploy(self):
        """ Deploy the message queue and all processors defined in the config-file
        """
        # Ideally, this should return the address of the RabbitMQ Server
        rabbitmq_address = self._deploy_queue()
        # Ideally, this should return the address of the MongoDB
        mongodb_address = self._deploy_mongodb()
        for host in self.hosts:
            for p in host.processors_native:
                # Ideally, pass the rabbitmq server and mongodb addresses here
                self._deploy_processor(p, host, DeployType.native, rabbitmq_address, mongodb_address)
            for p in host.processors_docker:
                # Ideally, pass the rabbitmq server and mongodb addresses here
                self._deploy_processor(p, host, DeployType.docker, rabbitmq_address, mongodb_address)
            self._close_clients(host)

    def kill(self):
        self._kill_queue()
        self._kill_mongodb()
        for host in self.hosts:
            if host.ssh_client:
                host.ssh_client = self._create_ssh_client(host)
            if host.docker_client:
                host.docker_client = self._create_docker_client(host)
            for p in host.processors_native:
                for pid in p.pids:
                    host.ssh_client.exec_command(f"kill {pid}")
                p.pids = []
            for p in host.processors_docker:
                for pid in p.pids:
                    self.log.debug(f"trying to kill docker container: {pid}")
                    # TODO: think about timeout.
                    #       think about using threads to kill parallelized to reduce waiting time
                    host.docker_client.containers.get(pid).stop()
                p.pids = []

    def _deploy_processor(self, processor, host, deploy_type, rabbitmq_server=None, mongodb=None):
        self.log.debug(f"deploy '{deploy_type}' processor: '{processor}' on '{host.address}'")
        assert not processor.pids, "processors already deployed. Pids are present. Host: " \
                                   "{host.__dict__}. Processor: {processor.__dict__}"

        # Create the specific RabbitMQ queue here based on the OCR-D processor name (processor.name)
        # self.rmq_publisher.create_queue(queue_name=processor.name)

        if deploy_type == DeployType.native:
            if not host.ssh_client:
                host.ssh_client = self._create_ssh_client(host)
        else:
            if not host.docker_client:
                host.docker_client = self._create_docker_client(host)
        for _ in range(processor.count):
            if deploy_type == DeployType.native:
                # This method should be rather part of the ProcessingWorker
                # The Processing Worker can just invoke a static method of ProcessingWorker
                # that creates an instance of the ProcessingWorker (Native instance)
                pid = self._start_native_processor(
                    client=host.ssh_client,
                    name=processor.name,
                    _queue_address=rabbitmq_server,
                    _database_address=mongodb)
            else:
                # This method should be rather part of the ProcessingWorker
                # The Processing Worker can just invoke a static method of ProcessingWorker
                # that creates an instance of the ProcessingWorker (Docker instance)
                pid = self._start_docker_processor(
                    client=host.docker_client,
                    name=processor.name,
                    _queue_address=rabbitmq_server,
                    _database_address=mongodb)
            processor.add_started_pid(pid)

    # Should be part of the ProcessingWorker class
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
        # What does this return and is supposed to return?
        # Putting some comments when using patterns is always appreciated
        # Since the docker version returns PID, this should also return PID for consistency
        return re.search(r"xyz([0-9]+)xyz", output).group(1)

    # Should be part of the ProcessingWorker class
    def _start_docker_processor(self, client, name, _queue_address, _database_address):
        self.log.debug(f"start docker processor: {name}")
        # TODO: add real command here to start processing server here
        res = client.containers.run("debian", "sleep 31", detach=True, remove=True)
        assert res and res.id, "run docker container failed"
        return res.id

    def _create_ssh_client(self, obj):
        address, username, password, keypath = obj.address, obj.username, obj.password, obj.keypath
        assert address and username, "address and username are mandatory"
        assert bool(password) is not bool(keypath), "expecting either password or keypath, not both"

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.log.debug(f"creating ssh-client with username: '{username}', keypath: '{keypath}'. "
                       f"host: {address}")
        # TODO: connecting could easily fail here: wrong password, wrong path to keyfile etc. Maybe
        #       would be better to use except and try to give custom error message when failing
        client.connect(hostname=address, username=username, password=password, key_filename=keypath)
        return client

    def _create_docker_client(self, obj):
        address, username, password, keypath = obj.address, obj.username, obj.password, obj.keypath
        assert address and username, "address and username are mandatory"
        assert bool(password) is not bool(keypath), "expecting either password or keypath " \
                                                    "provided, not both"
        return CustomDockerClient(username, address, password=password, keypath=keypath)

    def _close_clients(self, *args):
        for client in args:
            if hasattr(client, "close") and callable(client.close):
                client.close()

    def _deploy_queue(self, image="rabbitmq", detach=True, remove=True, ports=None):
        # This method deploys the RabbitMQ Server.
        # Handling of creation of queues, submitting messages to queues,
        # and receiving messages from queues is part of the RabbitMQ Library
        # Which is part of the OCR-D WebAPI implementation.

        client = self._create_docker_client(self.mq_data)
        if ports is None:
            # 5672, 5671 - used by AMQP 0-9-1 and AMQP 1.0 clients without and with TLS
            # 15672, 15671: HTTP API clients, management UI and rabbitmqadmin, without and with TLS
            # 25672: used for internode and CLI tools communication and is allocated from
            # a dynamic range (limited to a single port by default, computed as AMQP port + 20000)
            ports = {
                5672: self.mq_data.port,
                15672: 15672,
                25672: 25672
            }
        # TODO: use rm here or not? Should queues be reused?
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports
        )
        assert res and res.id, "starting message queue failed"
        self.mq_data.pid = res.id
        client.close()
        self.log.debug("deployed queue")

        # Not implemented yet
        # Note: The queue address is not just the IP address
        queue_address = "RabbitMQ Server address"
        return queue_address

    def _deploy_mongodb(self, image="mongo", detach=True, remove=True, ports=None):
        if not self.mongo_data or not self.mongo_data.address:
            self.log.debug("canceled mongo-deploy: no mongo_db in config")
            return
        client = self._create_docker_client(self.mongo_data)
        if ports is None:
            ports = {
                27017: self.mongo_data.port
            }
        # TODO: use rm here or not? Should the mongodb be reused?
        # TODO: what about the data-dir? Must data be preserved?
        res = client.containers.run(
            image=image,
            detach=detach,
            remove=remove,
            ports=ports
        )
        assert res and res.id, "starting mongodb failed"
        self.mongo_data.pid = res.id
        client.close()
        self.log.debug("deployed mongodb")

        # Not implemented yet
        # Note: The mongodb address is not just the IP address
        mongodb_address = "MongoDB Address"
        return mongodb_address

    def _kill_queue(self):
        if not self.mq_data.pid:
            self.log.debug("kill_queue: queue not running")
            return
        else:
            self.log.debug(f"trying to kill queue with id: {self.mq_data.pid} now")

        client = self._create_docker_client(self.mq_data)
        client.containers.get(self.mq_data.pid).stop()
        self.mq_data.pid = None
        client.close()
        self.log.debug("stopped queue")

    def _kill_mongodb(self):
        if not self.mongo_data or not self.mongo_data.pid:
            self.log.debug("kill_mongdb: mongodb not running")
            return
        else:
            self.log.debug(f"trying to kill mongdb with id: {self.mongo_data.pid} now")

        client = self._create_docker_client(self.mongo_data)
        client.containers.get(self.mongo_data.pid).stop()
        self.mongo_data.pid = None
        client.close()
        self.log.debug("stopped mongodb")


class HostData:
    """Class to wrap information for all processing-server-hosts.

    Config information and runtime information is stored here. This class
    should not do much but hold config information and runtime information. I
    hope to make the code better understandable this way. Deployer should still
    be the class who does things and this class here should be mostly passive
    """

    def __init__(self, config):
        self.address = config["address"]
        self.username = config["username"]
        self.password = config.get("password", None)
        self.keypath = config.get("path_to_privkey", None)
        assert self.password or self.keypath, "Host in configfile with neither password nor keyfile"
        self.processors_native = []
        self.processors_docker = []
        for x in config["deploy_processors"]:
            if x["deploy_type"] == 'native':
                self.processors_native.append(
                    self.Processor(x["name"], x["number_of_instance"], DeployType.native)
                )
            elif x["deploy_type"] == 'docker':
                self.processors_docker.append(
                    self.Processor(x["name"], x["number_of_instance"], DeployType.docker)
                )
            else:
                assert False, f"unknown deploy_type: '{x.deploy_type}'"
        self.ssh_client = None
        self.docker_client = None

    @classmethod
    def from_config(cls, config):
        res = []
        for x in config["hosts"]:
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


class MongoData:
    """ Class to hold information for Mongodb-Docker container
    """

    def __init__(self, config):
        self.address = config["address"]
        self.port = int(config["port"])
        self.username = config["ssh"]["username"]
        self.keypath = config["ssh"].get("path_to_privkey", None)
        self.password = config["ssh"].get("password", None)
        self.credentials = (config["credentials"]["username"], config["credentials"]["password"])
        self.pid = None


class QueueData:
    """ Class to hold information for RabbitMQ-Docker container
    """

    def __init__(self, config):
        self.address = config["address"]
        self.port = int(config["port"])
        self.username = config["ssh"]["username"]
        self.keypath = config["ssh"].get("path_to_privkey", None)
        self.password = config["ssh"].get("password", None)
        self.credentials = (config["credentials"]["username"], config["credentials"]["password"])
        self.pid = None


class DeployType(Enum):
    """ Deploy-Type of the processing server.
    """
    docker = 1
    native = 2

    @staticmethod
    def from_str(label: str):
        return DeployType[label.lower()]


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
