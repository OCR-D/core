"""
OCR-D CLI: start the processing server

.. click:: ocrd.cli.server:server_cli
    :prog: ocrd server
    :nested: full

"""
from subprocess import run, PIPE

import click
import uvicorn

from ocrd.helpers import parse_server_input, parse_version_string
from ocrd.server.main import ProcessorAPI
from ocrd_utils import parse_json_string_with_comments, initLogging


@click.command('processing-server')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('--address',
              help='Host name/IP, port, and connection string to a Mongo DB in the format IP:PORT:MONGO_URL',
              required=True,
              type=click.STRING)
def server_cli(processor_name, address):
    try:
        ip, port, mongo_url = parse_server_input(address)
    except ValueError:
        raise click.UsageError('The --server option must have the format IP:PORT:MONGO_URL')

    ocrd_tool = parse_json_string_with_comments(
        run([processor_name, '--dump-json'], stdout=PIPE, check=True, universal_newlines=True).stdout
    )
    version = parse_version_string(
        run([processor_name, '--version'], stdout=PIPE, check=True, universal_newlines=True).stdout
    )

    initLogging()

    # Start the server
    app = ProcessorAPI(
        title=ocrd_tool['executable'],
        description=ocrd_tool['description'],
        version=version,
        ocrd_tool=ocrd_tool,
        db_url=mongo_url
    )
    uvicorn.run(app, host=ip, port=port, access_log=False)
