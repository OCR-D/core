"""
OCR-D CLI: start the processing worker

.. click:: ocrd.cli.processing_worker:zip_cli
    :prog: ocrd processing-worker
    :nested: full
"""
import click
from ocrd_utils import initLogging
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
        # TODO: Check here if the provided `processor_name` exists
        processor_name = "ocrd-dummy"

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

    processing_worker = ProcessingWorker(
        processor_name=processor_name,
        processor_arguments={},
        rmq_host=rmq_host,
        rmq_port=rmq_port,
        rmq_vhost=rmq_vhost,
        db_url=db_url
    )

    #  TODO: Load the OCR-D processor in the memory cache

    # Start consuming with the configuration settings above
    # processing_worker.start_consuming()
