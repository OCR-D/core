# Abstraction for the Processing Server unit in this arch:
# https://user-images.githubusercontent.com/7795705/203554094-62ce135a-b367-49ba-9960-ffe1b7d39b2c.jpg

# Calls to native OCR-D processor should happen through
# the Processing Worker wrapper to hide low level details.
# According to the current requirements, each ProcessingWorker
# is a single OCR-D Processor instance.

from frozendict import frozendict
from functools import lru_cache, wraps
import json
from typing import List

from ocrd_utils import getLogger
from ocrd.processor.helpers import run_cli, run_processor
from ocrd.network.rabbitmq_utils import RMQConsumer
from ocrd.network.rabbitmq_utils import OcrdProcessingMessage, OcrdResultMessage


class ProcessingWorker:
    def __init__(self, processor_name: str, processor_arguments: dict, ocrd_tool: dict,
                 rmq_host: str, rmq_port: int, rmq_vhost: str, db_url: str) -> None:
        self.log = getLogger(__name__)
        # ocr-d processor instance to be started
        self.processor_name = processor_name

        # other potential parameters to be used
        self.processor_arguments = processor_arguments

        # Instantiation of the self.processor_class
        # Instantiated inside `on_consumed_message`
        self.processor_instance = None

        self.ocrd_tool = ocrd_tool

        self.db_url = db_url
        self.rmq_host = rmq_host
        self.rmq_port = rmq_port
        self.rmq_vhost = rmq_vhost

        # These could also be made configurable,
        # not relevant for the current state
        self.rmq_username = "default-consumer"
        self.rmq_password = "default-consumer"

        # self.rmq_consumer = self.connect_consumer()

    def connect_consumer(self) -> RMQConsumer:
        rmq_consumer = RMQConsumer(host=self.rmq_host, port=self.rmq_port, vhost=self.rmq_vhost)
        rmq_consumer.authenticate_and_connect(username=self.rmq_username, password=self.rmq_password)
        return rmq_consumer

    # Define what happens every time a message is consumed from the queue
    def on_consumed_message(self) -> None:
        # 1. Load the OCR-D processor in the memory cache on first message consumed
        # 2. Load the OCR-D processor from the memory cache on every other message consumed
        self.processor_instance = get_processor(self.processor_arguments, self.processor_class)
        if self.processor_instance:
            self.log.debug(f"Loading processor instance of `{self.processor_name}` succeeded.")
        else:
            self.log.debug(f"Loading processor instance of `{self.processor_name}` failed.")

        # TODO: Do the processing of the current message
        #  self.processor_instance.X(...)

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

    def process_message(self, ocrd_message: OcrdProcessingMessage):
        pass

    def run_cli_from_worker(
            self,
            executable: str,
            workspace,
            page_id: str,
            input_file_grps: List[str],
            output_file_grps: List[str],
            parameter: dict
    ):
        input_file_grps_str = ','.join(input_file_grps)
        output_file_grps_str = ','.join(output_file_grps)

        return_code = run_cli(
            executable=executable,
            workspace=workspace,
            page_id=page_id,
            input_file_grp=input_file_grps_str,
            output_file_grp=output_file_grps_str,
            parameter=json.dumps(parameter),
            mets_url=workspace.mets_target
        )

        if return_code != 0:
            self.log.error(f'{executable} exited with non-zero return value {return_code}.')
        else:
            self.log.debug(f'{executable} exited with success.')

    def run_processor_from_worker(
            self,
            processor_class,
            workspace,
            page_id: str,
            parameter: dict,
            input_file_grps: List[str],
            output_file_grps: List[str]
    ):
        input_file_grps_str = ','.join(input_file_grps)
        output_file_grps_str = ','.join(output_file_grps)

        success = True
        try:
            run_processor(
                processorClass=processor_class,
                workspace=workspace,
                page_id=page_id,
                parameter=parameter,
                input_file_grp=input_file_grps_str,
                output_file_grp=output_file_grps_str
            )
        except Exception as e:
            success = False
            self.log.exception(e)

        if not success:
            self.log.error(f'{processor_class} failed with an exception.')
        else:
            self.log.debug(f'{processor_class} exited with success.')


# Method adopted from Triet's implementation
# https://github.com/OCR-D/core/pull/884/files#diff-8b69cb85b5ffcfb93a053791dec62a2f909a0669ae33d8a2412f246c3b01f1a3R260
def freeze_args(func):
    """
    Transform mutable dictionary into immutable. Useful to be compatible with cache
    Code taken from `this post <https://stackoverflow.com/a/53394430/1814420>`_
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([frozendict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


# Method adopted from Triet's implementation
# https://github.com/OCR-D/core/pull/884/files#diff-8b69cb85b5ffcfb93a053791dec62a2f909a0669ae33d8a2412f246c3b01f1a3R260
@freeze_args
@lru_cache(maxsize=32)
def get_processor(parameter: dict, processor_class=None):
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
