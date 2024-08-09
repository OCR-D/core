from ocrd_utils import config, getLogger, LOG_FORMAT
from .client_utils import (
    poll_job_status_till_timeout_fail_or_success,
    poll_wf_status_till_timeout_fail_or_success,
    post_ps_processing_request,
    post_ps_workflow_request,
    verify_server_protocol
)


class Client:
    def __init__(
        self,
        server_addr_processing: str = config.OCRD_NETWORK_SERVER_ADDR_PROCESSING,
        timeout: int = config.OCRD_NETWORK_CLIENT_POLLING_TIMEOUT,
        wait: int = config.OCRD_NETWORK_CLIENT_POLLING_SLEEP
    ):
        self.log = getLogger(f"ocrd_network.client")
        self.server_addr_processing = server_addr_processing
        verify_server_protocol(self.server_addr_processing)
        self.polling_timeout = timeout
        self.polling_wait = wait
        self.polling_tries = int(timeout/wait)

    def poll_job_status_till_timeout_fail_or_success(self, job_id: str) -> str:
        return poll_job_status_till_timeout_fail_or_success(
            ps_server_host=self.server_addr_processing, job_id=job_id, tries=self.polling_tries, wait=self.polling_wait)

    def poll_wf_status_till_timeout_fail_or_success(self, job_id: str) -> str:
        return poll_wf_status_till_timeout_fail_or_success(
            ps_server_host=self.server_addr_processing, job_id=job_id, tries=self.polling_tries, wait=self.polling_wait)

    def send_processing_job_request(self, processor_name: str, req_params: dict) -> str:
        return post_ps_processing_request(
            ps_server_host=self.server_addr_processing, processor=processor_name, job_input=req_params)

    def send_workflow_job_request(self, path_to_wf: str, path_to_mets: str):
        return post_ps_workflow_request(
            ps_server_host=self.server_addr_processing, path_to_wf=path_to_wf, path_to_mets=path_to_mets)
