"""
Abstraction for the Processing Server unit in this arch:
https://user-images.githubusercontent.com/7795705/203554094-62ce135a-b367-49ba-9960-ffe1b7d39b2c.jpg

Calls to native OCR-D processor should happen through
the Processing Worker wrapper to hide low level details.
According to the current requirements, each ProcessingWorker
is a single OCR-D Processor instance.
"""

from datetime import datetime
from os import getpid
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic

from ocrd_utils import getLogger
from .constants import JobState
from .database import sync_initiate_database, sync_db_get_workspace, sync_db_update_processing_job, verify_database_uri
from .logging_utils import (
    configure_file_handler_with_formatter,
    get_processing_job_logging_file_path,
    get_processing_worker_logging_file_path,
)
from .process_helpers import invoke_processor
from .rabbitmq_utils import (
    connect_rabbitmq_consumer,
    connect_rabbitmq_publisher,
    OcrdProcessingMessage,
    OcrdResultMessage,
    verify_and_parse_mq_uri
)
from .utils import calculate_execution_time, post_to_callback_url


class ProcessingWorker:
    def __init__(self, rabbitmq_addr, mongodb_addr, processor_name, ocrd_tool: dict, processor_class=None) -> None:
        self.log = getLogger(f'ocrd_network.processing_worker')
        log_file = get_processing_worker_logging_file_path(processor_name=processor_name, pid=getpid())
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        try:
            verify_database_uri(mongodb_addr)
            self.log.debug(f'Verified MongoDB URL: {mongodb_addr}')
            self.rmq_data = verify_and_parse_mq_uri(rabbitmq_addr)
        except ValueError as error:
            msg = f"Failed to parse data, error: {error}"
            self.log.exception(msg)
            raise ValueError(msg)

        sync_initiate_database(mongodb_addr)  # Database client
        self.ocrd_tool = ocrd_tool
        # The str name of the OCR-D processor instance to be started
        self.processor_name = processor_name
        # The processor class to be used to instantiate the processor
        # Think of this as a func pointer to the constructor of the respective OCR-D processor
        self.processor_class = processor_class
        # Gets assigned when `connect_consumer` is called on the worker object
        # Used to consume OcrdProcessingMessage from the queue with name {processor_name}
        self.rmq_consumer = None
        # Gets assigned when the `connect_publisher` is called on the worker object
        # Used to publish OcrdResultMessage type message to the queue with name {processor_name}-result
        self.rmq_publisher = None

    def connect_consumer(self):
        self.rmq_consumer = connect_rabbitmq_consumer(self.log, self.rmq_data)
        # Always create a queue (idempotent)
        self.rmq_consumer.create_queue(queue_name=self.processor_name)

    def connect_publisher(self, enable_acks: bool = True):
        self.rmq_publisher = connect_rabbitmq_publisher(self.log, self.rmq_data, enable_acks=enable_acks)

    # Define what happens every time a message is consumed
    # from the queue with name self.processor_name
    def on_consumed_message(
        self,
        channel: BlockingChannel,
        delivery: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
    ) -> None:
        consumer_tag = delivery.consumer_tag
        delivery_tag: int = delivery.delivery_tag
        is_redelivered: bool = delivery.redelivered
        message_headers: dict = properties.headers

        ack_message = f"Acking message with tag: {delivery_tag}"
        nack_message = f"Nacking processing message with tag: {delivery_tag}"

        self.log.debug(
            f"Consumer tag: {consumer_tag}"
            f", message delivery tag: {delivery_tag}"
            f", redelivered: {is_redelivered}"
        )
        self.log.debug(f"Message headers: {message_headers}")

        try:
            self.log.debug(f"Trying to decode processing message with tag: {delivery_tag}")
            processing_message: OcrdProcessingMessage = OcrdProcessingMessage.decode_yml(body)
        except Exception as error:
            msg = f"Failed to decode processing message with tag: {delivery_tag}, error: {error}"
            self.log.exception(msg)
            self.log.info(nack_message)
            channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=False)
            raise Exception(msg)

        try:
            self.log.info(f"Starting to process the received message: {processing_message.__dict__}")
            self.process_message(processing_message=processing_message)
        except Exception as error:
            message = (
                f"Failed to process message with tag: {delivery_tag}. "
                f"Processing message: {processing_message.__dict__}"
            )
            self.log.exception(f"{message}, error: {error}")
            self.log.info(nack_message)
            channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=False)
            raise Exception(message)

        self.log.info(f"Successfully processed RabbitMQ message")
        self.log.debug(ack_message)
        channel.basic_ack(delivery_tag=delivery_tag, multiple=False)

    def start_consuming(self) -> None:
        if self.rmq_consumer:
            self.log.info(f"Configuring consuming from queue: {self.processor_name}")
            self.rmq_consumer.configure_consuming(
                queue_name=self.processor_name,
                callback_method=self.on_consumed_message
            )
            self.log.info(f"Starting consuming from queue: {self.processor_name}")
            # Starting consuming is a blocking action
            self.rmq_consumer.start_consuming()
        else:
            msg = f"The RMQConsumer is not connected/configured properly."
            self.log.exception(msg)
            raise Exception(msg)

    # TODO: Better error handling required to catch exceptions
    def process_message(self, processing_message: OcrdProcessingMessage) -> None:
        # Verify that the processor name in the processing message
        # matches the processor name of the current processing worker
        if self.processor_name != processing_message.processor_name:
            message = (
                "Processor name is not matching. "
                f"Expected: {self.processor_name}, "
                f"Got: {processing_message.processor_name}"
            )
            self.log.exception(message)
            raise ValueError(message)

        # All of this is needed because the OcrdProcessingMessage object
        # may not contain certain keys. Simply passing None in the OcrdProcessingMessage constructor
        # breaks the message validator schema which expects String, but not None due to the Optional[] wrapper.
        pm_keys = processing_message.__dict__.keys()
        job_id = processing_message.job_id
        input_file_grps = processing_message.input_file_grps
        output_file_grps = processing_message.output_file_grps if "output_file_grps" in pm_keys else None
        path_to_mets = processing_message.path_to_mets if "path_to_mets" in pm_keys else None
        workspace_id = processing_message.workspace_id if "workspace_id" in pm_keys else None
        page_id = processing_message.page_id if "page_id" in pm_keys else None
        parameters = processing_message.parameters if processing_message.parameters else {}

        if not path_to_mets and not workspace_id:
            msg = f"Both 'path_to_mets' and 'workspace_id' are missing in the OcrdProcessingMessage."
            self.log.exception(msg)
            raise ValueError(msg)

        mets_server_url = sync_db_get_workspace(workspace_mets_path=path_to_mets).mets_server_url
        if not path_to_mets and workspace_id:
            path_to_mets = sync_db_get_workspace(workspace_id).workspace_mets_path
            mets_server_url = sync_db_get_workspace(workspace_id).mets_server_url

        execution_failed = False
        self.log.debug(f"Invoking processor: {self.processor_name}")
        start_time = datetime.now()
        job_log_file = get_processing_job_logging_file_path(job_id=job_id)
        sync_db_update_processing_job(
            job_id=job_id,
            state=JobState.running,
            path_to_mets=path_to_mets,
            start_time=start_time,
            log_file_path=job_log_file
        )
        try:
            invoke_processor(
                processor_class=self.processor_class,
                executable=self.processor_name,
                abs_path_to_mets=path_to_mets,
                input_file_grps=input_file_grps,
                output_file_grps=output_file_grps,
                page_id=page_id,
                log_filename=job_log_file,
                parameters=processing_message.parameters,
                mets_server_url=mets_server_url
            )
        except Exception as error:
            message = (
                f"processor_name: {self.processor_name}, "
                f"path_to_mets: {path_to_mets}, "
                f"input_file_grps: {input_file_grps}, "
                f"output_file_grps: {output_file_grps}, "
                f"page_id: {page_id}, "
                f"parameters: {parameters}"
            )
            self.log.exception(f"{message}, error: {error}")
            execution_failed = True
        end_time = datetime.now()
        exec_duration = calculate_execution_time(start_time, end_time)
        job_state = JobState.success if not execution_failed else JobState.failed
        sync_db_update_processing_job(
            job_id=job_id,
            state=job_state,
            end_time=end_time,
            exec_time=f"{exec_duration} ms"
        )
        result_message = OcrdResultMessage(
            job_id=job_id,
            state=job_state.value,
            path_to_mets=path_to_mets,
            # May not be always available
            workspace_id=workspace_id if workspace_id else ''
        )
        self.publish_result_to_all(processing_message=processing_message, result_message=result_message)

    def publish_result_to_all(self, processing_message: OcrdProcessingMessage, result_message: OcrdResultMessage):
        pm_keys = processing_message.__dict__.keys()
        result_queue_name = processing_message.result_queue_name if "result_queue_name" in pm_keys else None
        callback_url = processing_message.callback_url if "callback_url" in pm_keys else None
        internal_callback_url = processing_message.internal_callback_url if "internal_callback_url" in pm_keys else None

        self.log.info(f"Result message: {result_message.__dict__}")
        # If the result_queue field is set, send the result message to a result queue
        if result_queue_name:
            self.log.info(f"Publishing result to message queue: {result_queue_name}")
            self.publish_to_result_queue(result_queue_name, result_message)
        if callback_url:
            self.log.info(f"Publishing result to user defined callback url: {callback_url}")
            # If the callback_url field is set,
            # post the result message (callback to a user defined endpoint)
            post_to_callback_url(self.log, callback_url, result_message)
        if internal_callback_url:
            self.log.info(f"Publishing result to internal callback url (Processing Server): {callback_url}")
            # If the internal callback_url field is set,
            # post the result message (callback to Processing Server endpoint)
            post_to_callback_url(self.log, internal_callback_url, result_message)

    def publish_to_result_queue(self, result_queue: str, result_message: OcrdResultMessage):
        if not self.rmq_publisher:
            self.connect_publisher()
        # create_queue method is idempotent - nothing happens if
        # a queue with the specified name already exists
        self.rmq_publisher.create_queue(queue_name=result_queue)
        self.log.info(f'Publishing result message to queue: {result_queue}')
        encoded_result_message = OcrdResultMessage.encode_yml(result_message)
        self.rmq_publisher.publish_to_queue(queue_name=result_queue, message=encoded_result_message)
