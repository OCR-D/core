# Abstraction for the Processing Server unit in this arch:
# https://user-images.githubusercontent.com/7795705/203554094-62ce135a-b367-49ba-9960-ffe1b7d39b2c.jpg

# Calls to native OCR-D processor should happen through
# the Processing Worker wrapper to hide low level details.
# According to the current requirements, each ProcessingWorker
# is a single OCR-D Processor instance.

import re
from ocrd_utils import (
    getLogger
)
from typing import Callable
from ocrd.network.deployment_utils import CustomDockerClient
from paramiko import SSHClient


class ProcessingWorker:
    def __init__(self, processor_name: str, processor_arguments: dict,
                 queue_address: str, database_address: str) -> None:

        self.log = getLogger(__name__)
        self.processor_name = processor_name
        # Required arguments to run the OCR-D Processor
        self.processor_arguments = processor_arguments  # processor.name is
        # RabbitMQ Address - This contains at least the
        # host name, port, and the virtual host
        self.rmq_address = queue_address
        self.mongodb_address = database_address

        # RMQConsumer object must be created here, reference: RabbitMQ Library (WebAPI Implementation)
        # Based on the API calls the ProcessingWorker will receive messages from the running instance
        # of the RabbitMQ Server (deployed by the Processing Broker) through the RMQConsumer object.
        self.rmq_consumer = self.configure_consumer(
            config_file="",
            callback_method=self.on_consumed_message
        )

    # TODO: change typehint for return if class is finally part of core(ocrd_network)
    @staticmethod
    def configure_consumer(config_file: str, callback_method: Callable) -> 'RMQConsumer':
        rmq_consumer = 'RMQConsumer Object'
        """
        Here is a template implementation to be adopted later

        rmq_consumer = RMQConsumer(host='localhost', port=5672, vhost='/')
        # The credentials are configured inside definitions.json
        # when building the RabbitMQ docker image
        rmq_consumer.authenticate_and_connect(
            username='default-consumer',
            password='default-consumer'
        )

        #Note: The queue name here is the processor.name by definition
        rmq_consumer.configure_consuming(queue_name='queue_name', callback_method=funcPtr)

        """
        return rmq_consumer

    # Define what happens every time a message is consumed from the queue
    def on_consumed_message(self) -> None:
        pass

    # A separate thread must be created here to listen
    # to the queue since this is a blocking action
    def start_consuming(self) -> None:
        # Blocks here and listens for messages coming from the specified queue
        # self.rmq_consumer.start_consuming()
        pass

    # TODO: queue_address and _database_address are prefixed with underscore because they are not
    # needed yet (otherwise flak8 complains). But they will be needed once the real
    # processing_worker is called here. Then they should be renamed
    @staticmethod
    def start_native_processor(client: SSHClient, name: str, _queue_address: str,
                               _database_address: str) -> str:
        log = getLogger(__name__)
        log.debug(f'start native processor: {name}')
        channel = client.invoke_shell()
        stdin, stdout = channel.makefile('wb'), channel.makefile('rb')
        # TODO: add real command here to start processing server here
        cmd = 'sleep 23s'
        # the only way to make it work to start a process in the background and return early is
        # this construction. The pid of the last started background process is printed with
        # `echo $!` but it is printed inbetween other output. Because of that I added `xyz` before
        # and after the code to easily be able to filter out the pid via regex when returning from
        # the function
        stdin.write(f'{cmd} & \n echo xyz$!xyz \n exit \n')
        output = stdout.read().decode('utf-8')
        stdout.close()
        stdin.close()
        # What does this return and is supposed to return?
        # Putting some comments when using patterns is always appreciated
        # Since the docker version returns PID, this should also return PID for consistency
        # TODO: mypy error: ignore or fix. Problem: re.search returns Optional (can be None, causes
        #       error if try to call)
        return re.search(r'xyz([0-9]+)xyz', output).group(1)

    # TODO: queue_address and _database_address are prefixed with underscore because they are not
    # needed yet (otherwise flak8 complains). But they will be needed once the real
    # processing_worker is called here. Then they should be renamed
    @staticmethod
    def start_docker_processor(client: CustomDockerClient, name: str, _queue_address: str,
                               _database_address: str) -> str:
        log = getLogger(__name__)
        log.debug(f'start docker processor: {name}')
        # TODO: add real command here to start processing server here
        res = client.containers.run('debian', 'sleep 31', detach=True, remove=True)
        assert res and res.id, 'run processor in docker-container failed'
        return res.id
