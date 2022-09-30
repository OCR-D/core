"""
OCR-D CLI: start the processing server

.. click:: ocrd.cli.server:server_cli
    :prog: ocrd server
    :nested: full

"""
import click
import uvicorn

from ocrd.helpers import parse_server_input
from ocrd.server.main import ProcessorAPI
from ocrd_utils import parse_json_string_with_comments, initLogging
from ocrd_validators import OcrdToolValidator


@click.command('server')
@click.argument('json_file', type=click.File(mode='r'))
@click.option('-t', '--tool', help='Name of the tool in the ocrd-tool.json file', required=True)
@click.option('--server',
              help='Host name/IP, port, and connection string to a Mongo DB in the format IP:PORT:MONGO_URL',
              required=True,
              type=click.STRING)
def server_cli(json_file, tool, server):
    try:
        ip, port, mongo_url = parse_server_input(server)
    except ValueError:
        raise click.UsageError('The --server option must have the format IP:PORT:MONGO_URL')

    content = json_file.read()
    ocrd_tool = parse_json_string_with_comments(content)

    # Validate the schema
    report = OcrdToolValidator.validate(ocrd_tool)
    if not report.is_valid:
        click.echo(report.to_xml())
        return 128

    initLogging()

    # Start the server
    app = ProcessorAPI(
        title=ocrd_tool['tools'][tool]['executable'],
        description=ocrd_tool['tools'][tool]['description'],
        version=ocrd_tool['version'],
        ocrd_tool=ocrd_tool['tools'][tool],
        db_url=mongo_url
    )
    uvicorn.run(app, host=ip, port=port, access_log=False)
