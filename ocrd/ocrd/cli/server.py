"""
OCR-D CLI: start the processing server

.. click:: ocrd.cli.server:server_cli
    :prog: ocrd server
    :nested: full

"""
import click
import uvicorn

from ocrd.server.main import app
from ocrd_utils import parse_json_string_with_comments, initLogging
from ocrd_validators import OcrdToolValidator


@click.command('server')
@click.argument('json_file', type=click.File(mode='r'))
@click.option('--ip', help='Host name/IP to listen at.', required=True)
@click.option('--port', help='TCP port to listen at', required=True, type=click.INT)
def server_cli(json_file, ip, port):
    content = json_file.read()
    ocrd_tool = parse_json_string_with_comments(content)

    # Validate the schema
    report = OcrdToolValidator.validate(ocrd_tool)
    if not report.is_valid:
        click.echo(report.to_xml())
        return 128

    initLogging()

    # Get the first key name under "tools"
    processor_name = next(iter(ocrd_tool['tools']))

    # Set other meta-data
    app.title = ocrd_tool['tools'][processor_name]['executable']
    app.description = ocrd_tool['tools'][processor_name]['description']
    app.version = ocrd_tool['version']
    app.processor_info = ocrd_tool['tools'][processor_name]

    uvicorn.run(app, host=ip, port=port, access_log=False)
