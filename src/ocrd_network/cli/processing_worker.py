import click
from ocrd_utils import get_ocrd_tool_json
from ocrd_network import DatabaseParamType, ProcessingWorker, QueueServerParamType


@click.command('processing-worker')
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
        raise Exception("The ocrd_tool is empty or missing")

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
