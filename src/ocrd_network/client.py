from typing import Optional
from ocrd_utils import config, getLogger, LOG_FORMAT
from .client_utils import (
    get_ps_deployed_processors,
    get_ps_deployed_processor_ocrd_tool,
    get_ps_processing_job_log,
    get_ps_processing_job_status,
    get_ps_workflow_job_status,
    poll_job_status_till_timeout_fail_or_success,
    poll_wf_status_till_timeout_fail_or_success,
    post_ps_processing_request,
    post_ps_workflow_request,
    verify_server_protocol
)


class Client:
    def __init__(
        self,
        server_addr_processing: Optional[str],
        timeout: int = config.OCRD_NETWORK_CLIENT_POLLING_TIMEOUT,
        wait: int = config.OCRD_NETWORK_CLIENT_POLLING_SLEEP
    ):
        self.log = getLogger(f"ocrd_network.client")
        if not server_addr_processing:
            server_addr_processing = config.OCRD_NETWORK_SERVER_ADDR_PROCESSING
        self.server_addr_processing = server_addr_processing
        verify_server_protocol(self.server_addr_processing)
        self.polling_timeout = timeout
        self.polling_wait = wait
        self.polling_tries = int(timeout / wait)

    def check_deployed_processors(self):
        return get_ps_deployed_processors(ps_server_host=self.server_addr_processing)

    def check_deployed_processor_ocrd_tool(self, processor_name: str):
        return get_ps_deployed_processor_ocrd_tool(
            ps_server_host=self.server_addr_processing, processor_name=processor_name)

    def check_job_log(self, job_id: str):
        return get_ps_processing_job_log(self.server_addr_processing, processing_job_id=job_id)

    def check_job_status(self, job_id: str):
        return get_ps_processing_job_status(self.server_addr_processing, processing_job_id=job_id)

    def check_workflow_status(self, workflow_job_id: str):
        return get_ps_workflow_job_status(self.server_addr_processing, workflow_job_id=workflow_job_id)

    def poll_job_status(self, job_id: str, print_state: bool = False) -> str:
        return poll_job_status_till_timeout_fail_or_success(
            ps_server_host=self.server_addr_processing, job_id=job_id, tries=self.polling_tries, wait=self.polling_wait,
            print_state=print_state)

    def poll_workflow_status(self, job_id: str, print_state: bool = False) -> str:
        return poll_wf_status_till_timeout_fail_or_success(
            ps_server_host=self.server_addr_processing, job_id=job_id, tries=self.polling_tries, wait=self.polling_wait,
            print_state=print_state)

    def send_processing_job_request(self, processor_name: str, req_params: dict) -> str:
        return post_ps_processing_request(
            ps_server_host=self.server_addr_processing, processor=processor_name, job_input=req_params)

    def send_workflow_job_request(self, path_to_wf: str, path_to_mets: str, page_wise: bool = False):
        return post_ps_workflow_request(
            ps_server_host=self.server_addr_processing, path_to_wf=path_to_wf, path_to_mets=path_to_mets,
            page_wise=page_wise)
