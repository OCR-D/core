"""
OCR-D CLI: management of network components

.. click:: ocrd.cli.network:network_cli
    :prog: ocrd network
    :nested: full
"""

import click
import logging
from ocrd_utils import (
    initLogging,
    get_ocrd_tool_json
)
from ocrd_network import (
    DatabaseParamType,
    ProcessingServer,
    ProcessingWorker,
    ProcessorServer,
    ServerAddressParamType,
    QueueServerParamType,
)


@click.group("network")
def network_cli():
    """
    Managing network components
    """
    initLogging()
    # TODO: Remove after the logging fix in core
    logging.getLogger('paramiko.transport').setLevel(logging.INFO)
    logging.getLogger('ocrd.network').setLevel(logging.DEBUG)


@network_cli.command('processing-server')
@click.argument('path_to_config', required=True, type=click.STRING)
@click.option('-a', '--address',
              default="localhost:8080",
              help='The URL of the Processing server, format: host:port',
              type=ServerAddressParamType(),
              required=True)
def processing_server_cli(path_to_config, address: str):
    """
    Start the Processing Server
    (proxy between the user and the
    Processing Worker(s) / Processor Server(s))
    """

    # Note, the address is already validated with the type field
    host, port = address.split(':')
    processing_server = ProcessingServer(path_to_config, host, port)
    processing_server.start()


@network_cli.command('processor-server')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('-a', '--address',
              help='The URL of the processor server, format: host:port',
              type=ServerAddressParamType(),
              required=True)
@click.option('-d', '--database',
              default="mongodb://localhost:27018",
              help='The URL of the MongoDB, format: mongodb://host:port',
              type=DatabaseParamType(),
              required=True)
def processor_server_cli(processor_name: str, address: str, database: str):
    """
    Start Processor Server
    (standalone REST API OCR-D processor)
    """
    try:
        # TODO: Better validate that inside the ProcessorServer itself
        host, port = address.split(':')
        processor_server = ProcessorServer(
            mongodb_addr=database,
            processor_name=processor_name,
            processor_class=None,  # For readability purposes assigned here
        )
        processor_server.run_server(host=host, port=int(port))
    except Exception as e:
        raise Exception("Processor server has failed with error") from e


@network_cli.command('processing-worker')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('-q', '--queue',
              default="amqp://admin:admin@localhost:5672/",
              help='The URL of the Queue Server, format: amqp://username:password@host:port/vhost',
              type=QueueServerParamType(),
              required=True)
@click.option('-d', '--database',
              default="mongodb://localhost:27018",
              help='The URL of the MongoDB, format: mongodb://host:port',
              type=DatabaseParamType(),
              required=True)
def processing_worker_cli(processor_name: str, queue: str, database: str):
    """
    Start Processing Worker
    (a specific ocr-d processor consuming tasks from RabbitMQ queue)
    """

    # Get the ocrd_tool dictionary
    # ocrd_tool = parse_json_string_with_comments(
    #     run([processor_name, '--dump-json'], stdout=PIPE, check=True, universal_newlines=True).stdout
    # )

    ocrd_tool = get_ocrd_tool_json(processor_name)
    if not ocrd_tool:
        raise Exception(f"The ocrd_tool is empty or missing")

    try:
        processing_worker = ProcessingWorker(
            rabbitmq_addr=queue,
            mongodb_addr=database,
            processor_name=ocrd_tool['executable'],
            ocrd_tool=ocrd_tool,
            processor_class=None,  # For readability purposes assigned here
        )
        # The RMQConsumer is initialized and a connection to the RabbitMQ is performed
        processing_worker.connect_consumer()
        # Start consuming from the queue with name `processor_name`
        processing_worker.start_consuming()
    except Exception as e:
        raise Exception("Processing worker has failed with error") from e
