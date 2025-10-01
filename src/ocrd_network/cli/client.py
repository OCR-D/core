import sys
import click
from json import dumps
from typing import List, Optional, Tuple
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile

from ocrd.decorators.parameter_option import parameter_option, parameter_override_option
from ocrd_network.constants import JobState
from ocrd_utils import DEFAULT_METS_BASENAME
from ocrd_utils.introspect import set_json_key_value_overrides
from ocrd_utils.str import parse_json_string_or_file
from ..client import Client
from requests import RequestException


ADDRESS_HELP = 'The URL of the Processing Server. If not provided, ' + \
    'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" environment variable is used by default'


class URLType(click.types.StringParamType):
    name = "url"
    def convert(self, value, param, ctx):
        try:
            parsed = urlparse(value)
            if parsed.scheme not in ("http", "https"):
                self.fail(f"invalid URL scheme ({parsed.scheme}): only HTTP allowed",
                          param, ctx)
            return value
        except ValueError as err:
            self.fail(err, param, ctx)
URL = URLType()

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


@discovery_cli.command('processors')
@click.option('--address', type=URL, help=ADDRESS_HELP)
def check_deployed_processors(address: Optional[str]):
    """
    Get a list of deployed processing workers.
    Each processor is shown only once regardless of the amount of deployed instances.
    """
    client = Client(server_addr_processing=address)
    try:
        processors_list = client.check_deployed_processors()
    except RequestException as e:
        print(
            getattr(e, 'detail_message', str(e)),
            f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
        )
        sys.exit(1)
    print(dumps(processors_list, indent=4))


@discovery_cli.command('processor')
@click.option('--address', type=URL, help=ADDRESS_HELP)
@click.argument('processor_name', required=True, type=click.STRING)
def check_processor_ocrd_tool(address: Optional[str], processor_name: str):
    """
    Get the json tool of a deployed processor specified with `processor_name`
    """
    client = Client(server_addr_processing=address)
    try:
        ocrd_tool = client.check_deployed_processor_ocrd_tool(processor_name=processor_name)
    except RequestException as e:
        print(
            getattr(e, 'detail_message', str(e)),
            f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
        )
        sys.exit(1)
    print(dumps(ocrd_tool, indent=4))


@client_cli.group('processing')
def processing_cli():
    """
    The processing endpoint of the WebAPI
    """
    pass


@processing_cli.command('check-log')
@click.option('--address', type=URL, help=ADDRESS_HELP)
@click.option('-j', '--processing-job-id', required=True)
def check_processing_job_log(address: Optional[str], processing_job_id: str):
    """
    Check the log of a previously submitted processing job.
    """
    client = Client(server_addr_processing=address)
    try:
        response = client.check_job_log(job_id=processing_job_id)
    except RequestException as e:
        print(
            getattr(e, 'detail_message', str(e)),
            f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
        )
        sys.exit(1)
    print(response._content.decode(encoding='utf-8'))


@processing_cli.command('check-status')
@click.option('--address', type=URL, help=ADDRESS_HELP)
@click.option('-j', '--processing-job-id', required=True)
def check_processing_job_status(address: Optional[str], processing_job_id: str):
    """
    Check the status of a previously submitted processing job.
    """
    client = Client(server_addr_processing=address)
    try:
        job_status = client.check_job_status(processing_job_id)
    except RequestException as e:
        print(
            getattr(e, 'detail_message', str(e)),
            f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
        )
        sys.exit(1)
    print(f"Processing job status: {job_status}")


@processing_cli.command('run')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('--address', type=URL, help=ADDRESS_HELP)
@click.option('-m', '--mets', required=True, default=DEFAULT_METS_BASENAME)
@click.option('-I', '--input-file-grp', default='OCR-D-INPUT')
@click.option('-O', '--output-file-grp', default='OCR-D-OUTPUT')
@click.option('-g', '--page-id')
@parameter_option
@parameter_override_option
@click.option('--result-queue-name')
@click.option('--callback-url')
@click.option('-b', '--block', default=False, is_flag=True,
              help='If set, the client will block till job timeout, fail or success.')
@click.option('-p', '--print-state', default=False, is_flag=True,
              help='If set, the client will print job states by each iteration.')
def send_processing_job_request(
    processor_name: str,
    address: Optional[str],
    mets: str,
    input_file_grp: str,
    output_file_grp: Optional[str],
    page_id: Optional[str],
    parameter: List[str],
    parameter_override: List[Tuple[str, str]],
    result_queue_name: Optional[str],
    callback_url: Optional[str],
    block: Optional[bool],
    print_state: Optional[bool]
):
    """
    Submit a processing job to the processing server.
    """
    req_params = {
        "path_to_mets": mets,
        "description": "OCR-D Network client request",
        "input_file_grps": input_file_grp.split(','),
    }
    if output_file_grp:
        req_params["output_file_grps"] = output_file_grp.split(',')
    if page_id:
        req_params["page_id"] = page_id
    req_params["parameters"] = set_json_key_value_overrides(parse_json_string_or_file(*parameter), *parameter_override)
    if result_queue_name:
        req_params["result_queue_name"] = result_queue_name
    if callback_url:
        req_params["callback_url"] = callback_url
    client = Client(server_addr_processing=address)
    try:
        processing_job_id = client.send_processing_job_request(
            processor_name=processor_name, req_params=req_params)
    except RequestException as e:
        print(
            getattr(e, 'detail_message', str(e)),
            f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
        )
        sys.exit(1)
    print(f"Processing job id: {processing_job_id}")

    if block:
        try:
            client.poll_job_status(job_id=processing_job_id, print_state=print_state)
        except RequestException as e:
            print(
                getattr(e, 'detail_message', str(e)),
                f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
            )
            sys.exit(1)


@client_cli.group('workflow')
def workflow_cli():
    """
    The workflow endpoint of the WebAPI
    """
    pass


@workflow_cli.command('check-status')
@click.option('--address', type=URL, help=ADDRESS_HELP)
@click.option('-j', '--workflow-job-id', required=True)
def check_workflow_job_status(address: Optional[str], workflow_job_id: str):
    """
    Check the status of a previously submitted workflow job.
    """
    client = Client(server_addr_processing=address)
    try:
        job_status = client.check_workflow_status(workflow_job_id)
    except RequestException as e:
        print(
            getattr(e, 'detail_message', str(e)),
            f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
        )
        sys.exit(1)
    print(f"Workflow job status: {job_status}")


@workflow_cli.command('run')
@click.option('--address', type=URL, help=ADDRESS_HELP)
@click.option('-m', '--path-to-mets', required=True, help="path to METS file of workspace to be processed (server-side path)")
@click.option('-w', '--path-to-workflow', required=False, help="path to workflow file (server- or client-side path)")
@click.option('--page-wise', is_flag=True, default=False, help="Whether to generate per-page jobs")
@click.option('-b', '--block', default=False, is_flag=True,
              help='If set, the client will block till job timeout, fail or success.')
@click.option('-p', '--print-state', default=False, is_flag=True,
              help='If set, the client will print job states by each iteration.')
@click.argument('tasks', nargs=-1)
def send_workflow_job_request(
    address: Optional[str],
    path_to_mets: str,
    path_to_workflow: Optional[str],
    page_wise: bool,
    block: bool,
    print_state: bool,
    tasks: List[str]
):
    """
    Submit a workflow job to the processing server.

    Provide workflow either via `tasks` arguments (same syntax
    as in ``ocrd process`` tasks arguments), or via `-w` file path
    (same syntax, but newline separated).
    """
    if (path_to_workflow) != bool(len(tasks)):
        raise ValueError("either -w/path-to-workflow or task argument(s) is required")

    client = Client(server_addr_processing=address)
    with NamedTemporaryFile() as workflow_file:
        for task in tasks:
            workflow_file.write((task + '\n').encode('utf-8'))
        workflow_file.flush()
        workflow_job_id = client.send_workflow_job_request(
            path_to_wf=path_to_workflow or workflow_file.name,
            path_to_mets=path_to_mets,
            page_wise=page_wise,
        )
    print(f"Workflow job id: {workflow_job_id}")
    if block:
        print(f"Polling state of workflow job {workflow_job_id}")
        try:
            state = client.poll_workflow_status(job_id=workflow_job_id, print_state=print_state)
        except RequestException as e:
            print(
                getattr(e, 'detail_message', str(e)),
                f"Requested URL: {getattr(getattr(e, 'response', ''), 'url', '')}"
            )
            sys.exit(1)
        if state != JobState.success:
            print(f"Workflow failed with {state}")
            exit(1)
        else:
            print("Workflow succeeded")
            exit(0)


@client_cli.group('workspace')
def workspace_cli():
    """
    The workspace endpoint of the WebAPI
    """
    pass
