from __future__ import absolute_import

import click
from ocrd.webservice.processor import create as create_processor_ws

@click.group()
def cli():
    """
    Start OCR-D web services
    """

@cli.command()
@click.option('-p', '--port', help="Port to run processor webservice on", default=5010)
def processor(port):
    """
    Start a server exposing the processors as webservices
    """
    create_processor_ws().run(port=port)
