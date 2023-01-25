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

import pika.spec
import pika.adapters.blocking_connection

from ocrd import Resolver
from ocrd_utils import getLogger
from ocrd.processor.helpers import run_cli, run_processor
from ocrd.network.helpers import (
    verify_database_url,
    verify_and_parse_rabbitmq_addr
)
from ocrd.network.rabbitmq_utils import (
    OcrdProcessingMessage,
    OcrdResultMessage,
    RMQConsumer
)


class ProcessingWorker:
    def __init__(self, rabbitmq_addr, mongodb_addr, processor_name, ocrd_tool: dict, processor_class=None) -> None:
        self.log = getLogger(__name__)

        try:
            self.db_url = verify_database_url(mongodb_addr)
            self.log.debug(f"Verified MongoDB URL: {self.db_url}")
            self.rmq_host, self.rmq_port, self.rmq_vhost = verify_and_parse_rabbitmq_addr(rabbitmq_addr)
            self.log.debug(f"Verified RabbitMQ Server URL: {self.rmq_host}:{self.rmq_port}{self.rmq_vhost}")
        except ValueError as e:
            raise ValueError(e)

        self.ocrd_tool = ocrd_tool

        # The str name of the OCR-D processor instance to be started
        self.processor_name = processor_name

        # The processor class to be used to instantiate the processor
        # Think of this as a func pointer to the constructor of the respective OCR-D processor
        self.processor_class = processor_class

        # Gets assigned when `connect_consumer` is called on the working object
        self.rmq_consumer = None

        # TODO: In case the processing worker should publish OcrdResultMessage type message to
        #  the message queue with name {processor_name}-result, the RMQPublisher should be instantiated
        #  self.rmq_publisher = None

    def connect_consumer(self, username="default", password="default"):
        self.log.debug(f"Connecting RMQConsumer to RabbitMQ server: {self.rmq_host}:{self.rmq_port}{self.rmq_vhost}")
        self.rmq_consumer = RMQConsumer(host=self.rmq_host, port=self.rmq_port, vhost=self.rmq_vhost)
        # TODO: Remove this information before the release
        self.log.debug(f"RMQConsumer authenticates with username: {username}, password: {password}")
        self.rmq_consumer.authenticate_and_connect(username=username, password=password)
        self.log.debug(f"Successfully connected RMQConsumer.")

    # Define what happens every time a message is consumed
    # from the queue with name self.processor_name
    def on_consumed_message(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            delivery: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes) -> None:
        consumer_tag = delivery.consumer_tag
        delivery_tag: int = delivery.delivery_tag
        is_redelivered: bool = delivery.redelivered
        message_headers: dict = properties.headers

        self.log.debug(f"Consumer tag: {consumer_tag}")
        self.log.debug(f"Message delivery tag: {delivery_tag}")
        self.log.debug(f"Is redelivered message: {is_redelivered}")
        self.log.debug(f"Message headers: {message_headers}")

        try:
            self.log.debug(f"Trying to decode processing message with tag: {delivery_tag}")
            # TODO: switch back to pickle?!
            processing_message: OcrdProcessingMessage = OcrdProcessingMessage.decode_yml(body)
        except Exception as e:
            self.log.error(f"Failed to decode processing message body: {body}")
            self.log.error(f"Nacking processing message with tag: {delivery_tag}")
            channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=False)
            raise Exception(f"Failed to decode processing message with tag: {delivery_tag}, reason: {e}")

        try:
            # TODO: Note to peer: ideally we should avoid doing database related actions
            #  in this method, and handle database related interactions inside `self.process_message()`
            self.log.debug(f"Starting to process the received message: {processing_message}")
            self.process_message(processing_message=processing_message)
        except Exception as e:
            self.log.error(f"Failed to process processing message with tag: {delivery_tag}")
            self.log.error(f"Nacking processing message with tag: {delivery_tag}")
            channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=False)
            raise Exception(f"Failed to process processing message with tag: {delivery_tag}, reason: {e}")

        self.log.debug(f"Successfully processed message ")
        self.log.debug(f"Acking message with tag: {delivery_tag}")
        channel.basic_ack(delivery_tag=delivery_tag, multiple=False)

    def start_consuming(self) -> None:
        if self.rmq_consumer:
            self.log.debug(f"Configuring consuming from queue: {self.processor_name}")
            self.rmq_consumer.configure_consuming(
                queue_name=self.processor_name,
                callback_method=self.on_consumed_message
            )
            self.log.debug(f"Starting consuming from queue: {self.processor_name}")
            # Starting consuming is a blocking action
            self.rmq_consumer.start_consuming()
        else:
            raise Exception("The RMQConsumer is not connected/configured properly")

    # TODO: Better error handling required to catch exceptions
    def process_message(self, processing_message: OcrdProcessingMessage):
        # Verify that the processor name in the processing message
        # matches the processor name of the current processing worker
        if self.processor_name != processing_message.processor_name:
            raise ValueError(f"Processor name is not matching. "
                             f"Expected: {self.processor_name}, Got: {processing_message.processor_name}")

        # This can be path if invoking `run_processor`
        # but must be ocrd.Workspace if invoking `run_cli`.
        workspace_path = processing_message.path_to_mets

        # Build the workspace from the workspace_path
        workspace = Resolver().workspace_from_url(workspace_path)

        page_id = processing_message.page_id
        input_file_grps = processing_message.input_file_grps
        output_file_grps = processing_message.output_file_grps
        parameter = processing_message.parameters

        # TODO: Use job_id - will be relevant for the MongoDB to assign job status
        #  Note to peer: We should encapsulate database related actions to keep this method simple
        job_id = processing_message.job_id

        if processing_message.result_queue:
            self.log.warning(f"Publishing results to a message queue from the Processing Worker is not supported yet")

        # TODO: Currently, no caching is performed.
        if self.processor_class:
            self.log.debug(f"Invoking the pythonic processor: {self.processor_name}")
            self.log.debug(f"Invoking the processor_class: {self.processor_class}")
            self.run_processor_from_worker(
                processor_class=self.processor_class,
                workspace=workspace,
                page_id=page_id,
                input_file_grps=input_file_grps,
                output_file_grps=output_file_grps,
                parameter=parameter
            )
        else:
            self.log.debug(f"Invoking the cli: {self.processor_name}")
            self.run_cli_from_worker(
                executable=self.processor_name,
                workspace=workspace,
                page_id=page_id,
                input_file_grps=input_file_grps,
                output_file_grps=output_file_grps,
                parameter=parameter
            )

    def run_processor_from_worker(
            self,
            processor_class,
            workspace,
            page_id: str,
            input_file_grps: List[str],
            output_file_grps: List[str],
            parameter: dict,
    ):
        input_file_grps_str = ','.join(input_file_grps)
        output_file_grps_str = ','.join(output_file_grps)

        success = True
        try:
            # TODO: Use the cached_processor flag here once #972 is merged to core
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
