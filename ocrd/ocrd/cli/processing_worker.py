"""
OCR-D CLI: start the processing worker

.. click:: ocrd.cli.processing_worker:zip_cli
    :prog: ocrd processing-worker
    :nested: full
"""
import click
from subprocess import run, PIPE
from ocrd_utils import (
    initLogging,
    parse_json_string_with_comments
)
from ocrd.network import ProcessingWorker


@click.command('processing-worker')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('-q', '--queue',
              default="localhost:5672/",
              help='The host, port, and virtual host of the RabbitMQ Server')
@click.option('-d', '--database',
              default="localhost:27018",
              help='The host and port of the MongoDB')
def processing_worker_cli(processor_name: str, queue: str, database: str):
    """
    Start a processing worker (a specific ocr-d processor)
    """
    initLogging()
    try:
        # TODO: Parse the actual RabbitMQ Server address - `queue`
        rmq_host = "localhost"
        rmq_port = 5672
        rmq_vhost = "/"
        rmq_url = f"{rmq_host}:{rmq_port}{rmq_vhost}"

        # TODO: Parse the actual MongoDB address - `database`
        db_prefix = "mongodb://"
        db_host = "localhost"
        db_port = 27018
        db_url = f"{db_prefix}{db_host}:{db_port}"
    except ValueError:
        raise click.UsageError('Wrong/Bad arguments format provided. Check the help sections')

    ocrd_tool = parse_json_string_with_comments(
        run([processor_name, '--dump-json'], stdout=PIPE, check=True, universal_newlines=True).stdout
    )

    processing_worker = ProcessingWorker(
        processor_name=processor_name,
        processor_arguments={},
        # TODO: Send the proper processor_class. How?
        processor_class="",
        ocrd_tool=ocrd_tool,
        rmq_host=rmq_host,
        rmq_port=rmq_port,
        rmq_vhost=rmq_vhost,
        db_url=db_url
    )

    # TODO: Remove. It's just to test starting the OCR-D processor
    processing_worker.on_consumed_message()

    # Start consuming with the configuration settings above
    # processing_worker.start_consuming()
