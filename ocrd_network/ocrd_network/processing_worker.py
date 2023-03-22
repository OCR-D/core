"""
Abstraction for the Processing Server unit in this arch:
https://user-images.githubusercontent.com/7795705/203554094-62ce135a-b367-49ba-9960-ffe1b7d39b2c.jpg

Calls to native OCR-D processor should happen through
the Processing Worker wrapper to hide low level details.
According to the current requirements, each ProcessingWorker
is a single OCR-D Processor instance.
"""

import json
import logging
from os import environ, getpid
import requests
from typing import Any, List

import pika.spec
import pika.adapters.blocking_connection

from ocrd import Resolver
from ocrd_utils import getLogger
from ocrd.processor.helpers import run_cli, run_processor

from .database import (
    sync_initiate_database,
    sync_set_processing_job_state
)
from .models import StateEnum
from .rabbitmq_utils import (
    OcrdProcessingMessage,
    OcrdResultMessage,
    RMQConsumer,
    RMQPublisher
)
from .utils import (
    verify_database_uri,
    verify_and_parse_mq_uri
)

try:
    # This env variable must be set before importing from Keras
    environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    from tensorflow.keras.utils import disable_interactive_logging
    # Enabled interactive logging throws an exception
    # due to a call of sys.stdout.flush()
    disable_interactive_logging()
except Exception:
    # Nothing should be handled here if TF is not available
    pass


class ProcessingWorker:
    def __init__(self, rabbitmq_addr, mongodb_addr, processor_name, ocrd_tool: dict, processor_class=None) -> None:
        self.log = getLogger(__name__)
        # TODO: Provide more flexibility for configuring file logging (i.e. via ENV variables)
        file_handler = logging.FileHandler(f'/tmp/worker_{processor_name}_{getpid()}.log', mode='a')
        logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_handler.setFormatter(logging.Formatter(logging_format))
        file_handler.setLevel(logging.DEBUG)
        self.log.addHandler(file_handler)

        try:
            verify_database_uri(mongodb_addr)
            self.log.debug(f'Verified MongoDB URL: {mongodb_addr}')
            rmq_data = verify_and_parse_mq_uri(rabbitmq_addr)
            self.rmq_username = rmq_data['username']
            self.rmq_password = rmq_data['password']
            self.rmq_host = rmq_data['host']
            self.rmq_port = rmq_data['port']
            self.rmq_vhost = rmq_data['vhost']
            self.log.debug(f'Verified RabbitMQ Credentials: {self.rmq_username}:{self.rmq_password}')
            self.log.debug(f'Verified RabbitMQ Server URL: {self.rmq_host}:{self.rmq_port}{self.rmq_vhost}')
        except ValueError as e:
            raise ValueError(e)

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
        # The publisher is connected when the `result_queue` field of the OcrdProcessingMessage is set for first time
        # Used to publish OcrdResultMessage type message to the queue with name {processor_name}-result
        self.rmq_publisher = None

    def connect_consumer(self) -> None:
        self.log.info(f'Connecting RMQConsumer to RabbitMQ server: '
                      f'{self.rmq_host}:{self.rmq_port}{self.rmq_vhost}')
        self.rmq_consumer = RMQConsumer(
            host=self.rmq_host,
            port=self.rmq_port,
            vhost=self.rmq_vhost
        )
        self.log.debug(f'RMQConsumer authenticates with username: '
                       f'{self.rmq_username}, password: {self.rmq_password}')
        self.rmq_consumer.authenticate_and_connect(
            username=self.rmq_username,
            password=self.rmq_password
        )
        self.log.info(f'Successfully connected RMQConsumer.')

    def connect_publisher(self, enable_acks: bool = True) -> None:
        self.log.info(f'Connecting RMQPublisher to RabbitMQ server: '
                      f'{self.rmq_host}:{self.rmq_port}{self.rmq_vhost}')
        self.rmq_publisher = RMQPublisher(
            host=self.rmq_host,
            port=self.rmq_port,
            vhost=self.rmq_vhost
        )
        self.log.debug(f'RMQPublisher authenticates with username: '
                       f'{self.rmq_username}, password: {self.rmq_password}')
        self.rmq_publisher.authenticate_and_connect(
            username=self.rmq_username,
            password=self.rmq_password
        )
        if enable_acks:
            self.rmq_publisher.enable_delivery_confirmations()
            self.log.info('Delivery confirmations are enabled')
        self.log.info('Successfully connected RMQPublisher.')

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

        self.log.debug(f'Consumer tag: {consumer_tag}, '
                       f'message delivery tag: {delivery_tag}, '
                       f'redelivered: {is_redelivered}')
        self.log.debug(f'Message headers: {message_headers}')

        try:
            self.log.debug(f'Trying to decode processing message with tag: {delivery_tag}')
            processing_message: OcrdProcessingMessage = OcrdProcessingMessage.decode_yml(body)
        except Exception as e:
            self.log.error(f'Failed to decode processing message body: {body}')
            self.log.error(f'Nacking processing message with tag: {delivery_tag}')
            channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=False)
            raise Exception(f'Failed to decode processing message with tag: {delivery_tag}, reason: {e}')

        try:
            self.log.info(f'Starting to process the received message: {processing_message}')
            self.process_message(processing_message=processing_message)
        except Exception as e:
            self.log.error(f'Failed to process processing message with tag: {delivery_tag}')
            self.log.error(f'Nacking processing message with tag: {delivery_tag}')
            channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=False)
            raise Exception(f'Failed to process processing message with tag: {delivery_tag}, reason: {e}')

        self.log.info(f'Successfully processed RabbitMQ message')
        self.log.debug(f'Acking message with tag: {delivery_tag}')
        channel.basic_ack(delivery_tag=delivery_tag, multiple=False)

    def start_consuming(self) -> None:
        if self.rmq_consumer:
            self.log.info(f'Configuring consuming from queue: {self.processor_name}')
            self.rmq_consumer.configure_consuming(
                queue_name=self.processor_name,
                callback_method=self.on_consumed_message
            )
            self.log.info(f'Starting consuming from queue: {self.processor_name}')
            # Starting consuming is a blocking action
            self.rmq_consumer.start_consuming()
        else:
            raise Exception('The RMQConsumer is not connected/configured properly')

    # TODO: Better error handling required to catch exceptions
    def process_message(self, processing_message: OcrdProcessingMessage) -> None:
        # Verify that the processor name in the processing message
        # matches the processor name of the current processing worker
        if self.processor_name != processing_message.processor_name:
            raise ValueError(f'Processor name is not matching. Expected: {self.processor_name},'
                             f'Got: {processing_message.processor_name}')

        # This can be path if invoking `run_processor`
        # but must be ocrd.Workspace if invoking `run_cli`.
        path_to_mets = processing_message.path_to_mets
        # Build the workspace from the workspace_path
        workspace = Resolver().workspace_from_url(path_to_mets)

        job_id = processing_message.job_id
        sync_set_processing_job_state(job_id=job_id, job_state=StateEnum.running)
        if self.processor_class:
            self.log.debug(f'Invoking the pythonic processor: {self.processor_name}')
            return_status = self.run_processor_from_worker(
                processor_class=self.processor_class,
                workspace=workspace,
                page_id=processing_message.page_id,
                input_file_grps=processing_message.input_file_grps,
                output_file_grps=processing_message.output_file_grps,
                parameter=processing_message.parameters
            )
        else:
            self.log.debug(f'Invoking the cli: {self.processor_name}')
            return_status = self.run_cli_from_worker(
                executable=self.processor_name,
                workspace=workspace,
                page_id=processing_message.page_id,
                input_file_grps=processing_message.input_file_grps,
                output_file_grps=processing_message.output_file_grps,
                parameter=processing_message.parameters
            )
        job_state = StateEnum.success if return_status else StateEnum.failed
        sync_set_processing_job_state(job_id=job_id, job_state=job_state)

        result_queue_name = processing_message.result_queue_name
        callback_url = processing_message.callback_url

        if result_queue_name or callback_url:
            result_message = OcrdResultMessage(
                job_id=job_id,
                state=job_state.value,
                path_to_mets=path_to_mets,
                # May not be always available
                workspace_id=processing_message.workspace_id
            )
            self.log.info(f'Result message: {result_message}')

            # If the result_queue field is set, send the result message to a result queue
            if result_queue_name:
                self.publish_to_result_queue(result_queue_name, result_message)

            # If the callback_url field is set, post the result message to a callback url
            if callback_url:
                self.post_to_callback_url(processing_message.callback_url, result_message)

    def publish_to_result_queue(self, result_queue: str, result_message: OcrdResultMessage):
        if self.rmq_publisher is None:
            self.connect_publisher()
        # create_queue method is idempotent - nothing happens if
        # a queue with the specified name already exists
        self.rmq_publisher.create_queue(queue_name=result_queue)
        self.log.info(f'Publishing result message to queue: {result_queue}')
        encoded_result_message = OcrdResultMessage.encode_yml(result_message)
        self.rmq_publisher.publish_to_queue(
            queue_name=result_queue,
            message=encoded_result_message
        )

    def post_to_callback_url(self, callback_url: str, result_message: OcrdResultMessage):
        self.log.info(f'Posting result message to callback_url "{callback_url}"')
        headers = {"Content-Type": "application/json"}
        json_data = {
            "job_id": result_message.job_id,
            "state": result_message.state,
            "path_to_mets": result_message.path_to_mets,
            "workspace_id": result_message.workspace_id
        }
        response = requests.post(url=callback_url, headers=headers, json=json_data)
        self.log.info(f'Response from callback_url "{response}"')

    def run_processor_from_worker(
            self,
            processor_class,
            workspace,
            page_id: str,
            input_file_grps: List[str],
            output_file_grps: List[str],
            parameter: dict,
    ) -> bool:
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
                output_file_grp=output_file_grps_str,
                instance_caching=True
            )
        except Exception as e:
            success = False
            self.log.exception(e)

        if not success:
            self.log.error(f'{processor_class} failed with an exception.')
        else:
            self.log.debug(f'{processor_class} exited with success.')
        return success

    def run_cli_from_worker(
            self,
            executable: str,
            workspace,
            page_id: str,
            input_file_grps: List[str],
            output_file_grps: List[str],
            parameter: dict
    ) -> bool:
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
            return False
        else:
            self.log.debug(f'{executable} exited with success.')
            return True
