import click
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

from ocrd.decorators import parameter_option
from ocrd_network import Client
from ocrd_utils import DEFAULT_METS_BASENAME


STOP_WAITING_CALLBACK = False


class ClientCallbackHandler(BaseHTTPRequestHandler):
    """
    A simple callback handler for the network client to be invoked when the Processing Worker
    sends requests to the `callback_url` set in the processing request submitted to the Processing Server.
    """

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write("finished".encode("utf-8"))
        len = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(len).decode("utf-8")
        # TODO: how should the callback-content be handled/printed
        print(f"Processor finished: {data}")
        global STOP_WAITING_CALLBACK
        STOP_WAITING_CALLBACK = True


class ClientCallbackServer(HTTPServer):
    """
    A simple http-server that listens for callbacks from the Processing Server/Worker.
    """
    def __init__(self):
        super().__init__(server_address=("0.0.0.0", 0), RequestHandlerClass=ClientCallbackHandler)
        self.callback_url = f"http://{self.server_address[0]}:{self.server_address[1]}"


@click.group('client')
def client_cli():
    """
    A client for interacting with the network modules.
    The client CLI mimics the WebAPI endpoints
    """
    pass


@client_cli.group('discovery')
def discovery_cli():
    """
    The discovery endpoint of the WebAPI
    """
    pass


@client_cli.group('processing')
def processing_cli():
    """
    The processing endpoint of the WebAPI
    """
    pass


@processing_cli.command('processor')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('--address')
@click.option('-m', '--mets', required=True, default=DEFAULT_METS_BASENAME)
@click.option('-I', '--input-file-grp', default='OCR-D-INPUT')
@click.option('-O', '--output-file-grp', default='OCR-D-OUTPUT')
@click.option('-g', '--page-id')
@parameter_option
@click.option('--result-queue-name')
@click.option('--callback-url')
@click.option('--agent-type', default='worker')
def send_processing_request(
    address: Optional[str],
    processor_name: str,
    mets: str,
    input_file_grp: str,
    output_file_grp: Optional[str],
    page_id: Optional[str],
    parameter: Optional[dict],
    result_queue_name: Optional[str],
    callback_url: Optional[str],
    # TODO: This is temporally available to toggle
    #  between the ProcessingWorker/ProcessorServer
    agent_type: Optional[str]
):
    callback_server = ClientCallbackServer()
    req_params = {
        "path_to_mets": mets,
        "description": "OCR-D Network client request",
        "input_file_grps": input_file_grp.split(','),
        "parameters": parameter if parameter else {},
        "agent_type": agent_type,
        "callback_url": callback_server.callback_url
    }
    if output_file_grp:
        req_params["output_file_grps"] = output_file_grp.split(',')
    if page_id:
        req_params["page_id"] = page_id
    if result_queue_name:
        req_params["result_queue_name"] = result_queue_name
    if callback_url:
        req_params["callback_url"] = callback_url

    client = Client(server_addr_processing=address)
    response = client.send_processing_request(processor_name=processor_name, req_params=req_params)
    processing_job_id = response.get('job_id', None)
    print(f"Processing job id: {processing_job_id}")
    while not STOP_WAITING_CALLBACK:
        callback_server.handle_request()


@client_cli.group('workflow')
def workflow_cli():
    """
    The workflow endpoint of the WebAPI
    """
    pass


@client_cli.group('workspace')
def workspace_cli():
    """
    The workspace endpoint of the WebAPI
    """
    pass
