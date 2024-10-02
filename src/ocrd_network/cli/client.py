import click
from json import dumps
from typing import List, Optional, Tuple
from ocrd.decorators.parameter_option import parameter_option, parameter_override_option
from ocrd_network.constants import JobState
from ocrd_utils import DEFAULT_METS_BASENAME
from ocrd_utils.introspect import set_json_key_value_overrides
from ocrd_utils.str import parse_json_string_or_file
from ..client import Client


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
@click.option('--address',
              help='The address of the Processing Server. If not provided, '
                   'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
def check_deployed_processors(address: Optional[str]):
    """
    Get a list of deployed processing workers/processor servers.
    Each processor is shown only once regardless of the amount of deployed instances.
    """
    client = Client(server_addr_processing=address)
    processors_list = client.check_deployed_processors()
    print(dumps(processors_list, indent=4))


@discovery_cli.command('processor')
@click.option('--address',
              help='The address of the Processing Server. If not provided, '
                   'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
@click.argument('processor_name', required=True, type=click.STRING)
def check_processor_ocrd_tool(address: Optional[str], processor_name: str):
    """
    Get the json tool of a deployed processor specified with `processor_name`
    """
    client = Client(server_addr_processing=address)
    ocrd_tool = client.check_deployed_processor_ocrd_tool(processor_name=processor_name)
    print(dumps(ocrd_tool, indent=4))


@client_cli.group('processing')
def processing_cli():
    """
    The processing endpoint of the WebAPI
    """
    pass


@processing_cli.command('check-log')
@click.option('--address',
              help='The address of the Processing Server. If not provided, '
                   'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
@click.option('-j', '--processing-job-id', required=True)
def check_processing_job_status(address: Optional[str], processing_job_id: str):
    """
    Check the log of a previously submitted processing job.
    """
    client = Client(server_addr_processing=address)
    response = client.check_job_log(job_id=processing_job_id)
    print(response._content.decode(encoding='utf-8'))


@processing_cli.command('check-status')
@click.option('--address',
              help='The address of the Processing Server. If not provided, '
                   'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
@click.option('-j', '--processing-job-id', required=True)
def check_processing_job_status(address: Optional[str], processing_job_id: str):
    """
    Check the status of a previously submitted processing job.
    """
    client = Client(server_addr_processing=address)
    job_status = client.check_job_status(processing_job_id)
    assert job_status
    print(f"Processing job status: {job_status}")


@processing_cli.command('run')
@click.argument('processor_name', required=True, type=click.STRING)
@click.option('--address',
              help='The address of the Processing Server. If not provided, '
                   'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
@click.option('-m', '--mets', required=True, default=DEFAULT_METS_BASENAME)
@click.option('-I', '--input-file-grp', default='OCR-D-INPUT')
@click.option('-O', '--output-file-grp', default='OCR-D-OUTPUT')
@click.option('-g', '--page-id')
@parameter_option
@parameter_override_option
@click.option('--result-queue-name')
@click.option('--callback-url')
@click.option('--agent-type', default='worker')
@click.option('-b', '--block', default=False, is_flag=True,
              help='If set, the client will block till job timeout, fail or success.')
@click.option('-p', '--print-state', default=False, is_flag=True,
              help='If set, the client will print job states by each iteration.')
def send_processing_job_request(
    address: Optional[str],
    processor_name: str,
    mets: str,
    input_file_grp: str,
    output_file_grp: Optional[str],
    page_id: Optional[str],
    parameter: List[str],
    parameter_override: List[Tuple[str, str]],
    result_queue_name: Optional[str],
    callback_url: Optional[str],
    # TODO: This is temporally available to toggle
    #  between the ProcessingWorker/ProcessorServer
    agent_type: Optional[str],
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
        "agent_type": agent_type
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
    processing_job_id = client.send_processing_job_request(
        processor_name=processor_name, req_params=req_params)
    assert processing_job_id
    print(f"Processing job id: {processing_job_id}")
    if block:
        client.poll_job_status(job_id=processing_job_id, print_state=print_state)


@client_cli.group('workflow')
def workflow_cli():
    """
    The workflow endpoint of the WebAPI
    """
    pass


@workflow_cli.command('check-status')
@click.option('--address', help='The address of the Processing Server. If not provided, '
                                'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
@click.option('-j', '--workflow-job-id', required=True)
def check_workflow_job_status(address: Optional[str], workflow_job_id: str):
    """
    Check the status of a previously submitted workflow job.
    """
    client = Client(server_addr_processing=address)
    job_status = client.check_workflow_status(workflow_job_id)
    assert job_status
    print(f"Workflow job status: {job_status}")


@workflow_cli.command('run')
@click.option('--address', help='The address of the Processing Server. If not provided, '
                                'the "OCRD_NETWORK_SERVER_ADDR_PROCESSING" env variable is used by default')
@click.option('-m', '--path-to-mets', required=True)
@click.option('-w', '--path-to-workflow', required=True)
@click.option('--page-wise/--no-page-wise', is_flag=True, default=False, help="Whether to generate per-page jobs")
@click.option('-b', '--block', default=False, is_flag=True,
              help='If set, the client will block till job timeout, fail or success.')
@click.option('-p', '--print-state', default=False, is_flag=True,
              help='If set, the client will print job states by each iteration.')
def send_workflow_job_request(
    address: Optional[str],
    path_to_mets: str,
    path_to_workflow: str,
    page_wise: bool,
    block: bool,
    print_state: bool
):
    """
    Submit a workflow job to the processing server.
    """
    client = Client(server_addr_processing=address)
    workflow_job_id = client.send_workflow_job_request(
        path_to_wf=path_to_workflow,
        path_to_mets=path_to_mets,
        page_wise=page_wise,
    )
    assert workflow_job_id
    print(f"Workflow job id: {workflow_job_id}")
    if block:
        print(f"Polling state of workflow job {workflow_job_id}")
        state = client.poll_workflow_status(job_id=workflow_job_id, print_state=print_state)
        if state != JobState.success:
            print(f"Workflow failed with {state}")
            exit(1)
        else:
            print(f"Workflow succeeded")
            exit(0)

@client_cli.group('workspace')
def workspace_cli():
    """
    The workspace endpoint of the WebAPI
    """
    pass
