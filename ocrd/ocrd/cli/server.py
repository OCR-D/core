"""
OCR-D CLI: start the processing server

.. click:: ocrd.cli.server:server_cli
    :prog: ocrd server
    :nested: full

"""
import click
import uvicorn

from ocrd.server.main import create_server
from ocrd_utils import parse_json_string_with_comments, initLogging
from ocrd_validators import OcrdToolValidator


@click.command('server')
@click.argument('json_file', type=click.File(mode='r'))
@click.option('-t', '--tool', help='Name of the tool in the ocrd-tool.json file', required=True)
@click.option('--ip', help='Host name/IP to listen at.', required=True)
@click.option('--port', help='TCP port to listen at', required=True, type=click.INT)
def server_cli(json_file, tool, ip, port):
    content = json_file.read()
    ocrd_tool = parse_json_string_with_comments(content)

    # Validate the schema
    report = OcrdToolValidator.validate(ocrd_tool)
    if not report.is_valid:
        click.echo(report.to_xml())
        return 128

    initLogging()

    # Create the server
    app = create_server(title=ocrd_tool['tools'][tool]['executable'],
                        description=ocrd_tool['tools'][tool]['description'],
                        version=ocrd_tool['version'],
                        ocrd_tool=ocrd_tool['tools'][tool],
                        processor_class=None)

    uvicorn.run(app, host=ip, port=port, access_log=False)
