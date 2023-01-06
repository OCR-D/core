from enum import Enum
from ocrd_utils import (
    getLogger
)
from ocrd.network.deployment_utils import (
    close_clients,
    create_docker_client,
    create_ssh_client
)
from ocrd.network.processing_worker import ProcessingWorker

# Abstraction of the Deployment functionality
# The Deployer agent is in the middle between
# the ProcessingBroker agent and the ProcessingWorker agents
# ProcessingBroker provides the configuration file to the Deployer agent
# The Deployer agent creates the ProcessingWorker agents.

# TODO:
# Ideally, the interaction among the agents should happen through
# the defined API calls of the objects to stay loyal to the OOP paradigm
# This would also increase the readability and maintainability of the source code.


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
        self.log = getLogger(__name__)
        self.log.debug('Deployer-init()')
        self.mongo_data = MongoData(config['mongo_db'])
        self.mq_data = QueueData(config['message_queue'])
        self.hosts = HostData.from_config(config)

    def deploy_all(self):
        """ Deploy the message queue and all processors defined in the config-file
        """
        # Ideally, this should return the address of the RabbitMQ Server
        rabbitmq_address = self._deploy_queue()
        # Ideally, this should return the address of the MongoDB
        mongodb_address = self._deploy_mongodb()
        self._deploy_processing_workers(self.hosts, rabbitmq_address, mongodb_address)

    def kill_all(self):
        self._kill_queue()
        self._kill_mongodb()
        self._kill_processing_workers()

    def _deploy_processing_workers(self, hosts, rabbitmq_address, mongodb_address):
        for host in hosts:
            for p in host.processors_native:
                # Ideally, pass the rabbitmq server and mongodb addresses here
                self._deploy_processing_worker(p, host, DeployType.native, rabbitmq_address, mongodb_address)
            for p in host.processors_docker:
                # Ideally, pass the rabbitmq server and mongodb addresses here
                self._deploy_processing_worker(p, host, DeployType.docker, rabbitmq_address, mongodb_address)
            close_clients(host)

    def _deploy_processing_worker(self, processor, host, deploy_type, rabbitmq_server=None, mongodb=None):
        self.log.debug(f'deploy "{deploy_type}" processor: "{processor}" on "{host.address}"')
        assert not processor.pids, 'processors already deployed. Pids are present. Host: ' \
                                   '{host.__dict__}. Processor: {processor.__dict__}'

        # Create the specific RabbitMQ queue here based on the OCR-D processor name (processor.name)
        # self.rmq_publisher.create_queue(queue_name=processor.name)

        if deploy_type == DeployType.native:
            if not host.ssh_client:
                host.ssh_client = create_ssh_client(host)
        else:
            if not host.docker_client:
                host.docker_client = create_docker_client(host)
        for _ in range(processor.count):
            if deploy_type == DeployType.native:
                # This method should be rather part of the ProcessingWorker
                # The Processing Worker can just invoke a static method of ProcessingWorker
                # that creates an instance of the ProcessingWorker (Native instance)
                pid = ProcessingWorker.start_native_processor(
                    client=host.ssh_client,
                    name=processor.name,
                    _queue_address=rabbitmq_server,
                    _database_address=mongodb)
            else:
                # This method should be rather part of the ProcessingWorker
                # The Processing Worker can just invoke a static method of ProcessingWorker
                # that creates an instance of the ProcessingWorker (Docker instance)
                pid = ProcessingWorker.start_docker_processor(
                    client=host.docker_client,
                    name=processor.name,
                    _queue_address=rabbitmq_server,
                    _database_address=mongodb)
            processor.add_started_pid(pid)

    def _deploy_queue(self, image='rabbitmq', detach=True, remove=True, ports=None):
        # This method deploys the RabbitMQ Server.
        # Handling of creation of queues, submitting messages to queues,
        # and receiving messages from queues is part of the RabbitMQ Library
        # Which is part of the OCR-D WebAPI implementation.

        client = create_docker_client(self.mq_data)
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
        assert res and res.id, 'starting message queue failed'
        self.mq_data.pid = res.id
        client.close()
        self.log.debug('deployed queue')

        # Not implemented yet
        # Note: The queue address is not just the IP address
        queue_address = 'RabbitMQ Server address'
        return queue_address

    def _deploy_mongodb(self, image='mongo', detach=True, remove=True, ports=None):
        if not self.mongo_data or not self.mongo_data.address:
            self.log.debug('canceled mongo-deploy: no mongo_db in config')
            return
        client = create_docker_client(self.mongo_data)
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
        assert res and res.id, 'starting mongodb failed'
        self.mongo_data.pid = res.id
        client.close()
        self.log.debug('deployed mongodb')

        # Not implemented yet
        # Note: The mongodb address is not just the IP address
        mongodb_address = 'MongoDB Address'
        return mongodb_address

    def _kill_queue(self):
        if not self.mq_data.pid:
            self.log.debug('kill_queue: queue not running')
            return
        else:
            self.log.debug(f'trying to kill queue with id: {self.mq_data.pid} now')

        client = create_docker_client(self.mq_data)
        client.containers.get(self.mq_data.pid).stop()
        self.mq_data.pid = None
        client.close()
        self.log.debug('stopped queue')

    def _kill_mongodb(self):
        if not self.mongo_data or not self.mongo_data.pid:
            self.log.debug('kill_mongdb: mongodb not running')
            return
        else:
            self.log.debug(f'trying to kill mongdb with id: {self.mongo_data.pid} now')

        client = create_docker_client(self.mongo_data)
        client.containers.get(self.mongo_data.pid).stop()
        self.mongo_data.pid = None
        client.close()
        self.log.debug('stopped mongodb')

    def _kill_processing_workers(self):
        for host in self.hosts:
            if host.ssh_client:
                host.ssh_client = create_ssh_client(host)
            if host.docker_client:
                host.docker_client = create_docker_client(host)
            for p in host.processors_native:
                for pid in p.pids:
                    host.ssh_client.exec_command(f'kill {pid}')
                p.pids = []
            for p in host.processors_docker:
                for pid in p.pids:
                    self.log.debug(f'trying to kill docker container: {pid}')
                    # TODO: think about timeout.
                    #       think about using threads to kill parallelized to reduce waiting time
                    host.docker_client.containers.get(pid).stop()
                p.pids = []

    # May be good to have more flexibility here
    # TODO: Support that functionality as well.
    #  Then _kill_processing_workers should just call this method in a loop
    def _kill_processing_worker(self):
        pass


# TODO: These should be separated from the Deployer logic
# TODO: Moreover, some of these classes must be just @dataclasses
class HostData:
    """Class to wrap information for all processing-server-hosts.

    Config information and runtime information is stored here. This class
    should not do much but hold config information and runtime information. I
    hope to make the code better understandable this way. Deployer should still
    be the class who does things and this class here should be mostly passive
    """

    def __init__(self, config):
        self.address = config['address']
        self.username = config['username']
        self.password = config.get('password', None)
        self.keypath = config.get('path_to_privkey', None)
        assert self.password or self.keypath, 'Host in configfile with neither password nor keyfile'
        self.processors_native = []
        self.processors_docker = []
        for x in config['deploy_processors']:
            if x['deploy_type'] == 'native':
                self.processors_native.append(
                    self.Processor(x['name'], x['number_of_instance'], DeployType.native)
                )
            elif x['deploy_type'] == 'docker':
                self.processors_docker.append(
                    self.Processor(x['name'], x['number_of_instance'], DeployType.docker)
                )
            else:
                assert False, f'unknown deploy_type: "{x.deploy_type}"'
        self.ssh_client = None
        self.docker_client = None

    @classmethod
    def from_config(cls, config):
        res = []
        for x in config['hosts']:
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
        self.address = config['address']
        self.port = int(config['port'])
        self.username = config['ssh']['username']
        self.keypath = config['ssh'].get('path_to_privkey', None)
        self.password = config['ssh'].get('password', None)
        self.credentials = (config['credentials']['username'], config['credentials']['password'])
        self.pid = None


class QueueData:
    """ Class to hold information for RabbitMQ-Docker container
    """

    def __init__(self, config):
        self.address = config['address']
        self.port = int(config['port'])
        self.username = config['ssh']['username']
        self.keypath = config['ssh'].get('path_to_privkey', None)
        self.password = config['ssh'].get('password', None)
        self.credentials = (config['credentials']['username'], config['credentials']['password'])
        self.pid = None


class DeployType(Enum):
    """ Deploy-Type of the processing server.
    """
    docker = 1
    native = 2

    @staticmethod
    def from_str(label: str):
        return DeployType[label.lower()]
