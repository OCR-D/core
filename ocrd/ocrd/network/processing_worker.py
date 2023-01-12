# Abstraction for the Processing Server unit in this arch:
# https://user-images.githubusercontent.com/7795705/203554094-62ce135a-b367-49ba-9960-ffe1b7d39b2c.jpg

# Calls to native OCR-D processor should happen through
# the Processing Worker wrapper to hide low level details.
# According to the current requirements, each ProcessingWorker
# is a single OCR-D Processor instance.

from frozendict import frozendict
from functools import lru_cache, wraps
from paramiko import SSHClient
from re import search as re_search
from typing import Callable, Union

from ocrd_utils import getLogger

from ocrd.network.deployment_utils import CustomDockerClient
from ocrd.network.rabbitmq_utils import RMQConsumer


class ProcessingWorker:
    def __init__(self, processor_name: str, processor_arguments: dict,
                 rmq_host: str, rmq_port: int, rmq_vhost: str, db_url: str) -> None:

        self.log = getLogger(__name__)
        # ocr-d processor instance to be started
        self.processor_name = processor_name
        # other potential parameters to be used
        self.processor_arguments = processor_arguments

        self.db_url = db_url

        self.rmq_host = rmq_host
        self.rmq_port = rmq_port
        self.rmq_vhost = rmq_vhost

        # These could also be made configurable,
        # not relevant for the current state
        self.rmq_username = "default-consumer"
        self.rmq_password = "default-consumer"

        # self.rmq_consumer = self.connect_consumer()

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

    def connect_consumer(self) -> RMQConsumer:
        rmq_consumer = RMQConsumer(host=self.rmq_host, port=self.rmq_port, vhost=self.rmq_vhost)
        rmq_consumer.authenticate_and_connect(username=self.rmq_username, password=self.rmq_password)
        return rmq_consumer

    # Define what happens every time a message is consumed from the queue
    def on_consumed_message(self) -> None:
        # TODO: Get the OCR-D processor instance back from the memory cache
        # self.get_processor(...)
        pass

    def start_consuming(self) -> None:
        if self.rmq_consumer:
            self.rmq_consumer.configure_consuming(
                queue_name=self.processor_name,
                callback_method=self.on_consumed_message
            )
            # TODO: A separate thread must be created here to listen
            #  to the queue since this is a blocking action
            self.rmq_consumer.start_consuming()
        else:
            raise Exception("The RMQ Consumer is not connected/configured properly")



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
        return re_search(r'xyz([0-9]+)xyz', output).group(1)

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
