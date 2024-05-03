from src.ocrd_network.constants import JobState
from tests.network.config import test_config
from tests.network.utils import poll_till_timeout_fail_or_success, post_ps_workflow_request

PROCESSING_SERVER_URL = test_config.PROCESSING_SERVER_URL


def _test_ocrd_all_workflow():
    # This test is supposed to run with ocrd_all not with just core on its own
    # Note: the used workflow path is volume mapped
    path_to_wf = "/ocrd-data/assets/ocrd_all-test-workflow.txt"
    path_to_mets = "/data/mets.xml"
    wf_job_id = post_ps_workflow_request(PROCESSING_SERVER_URL, path_to_wf, path_to_mets)
    job_state = poll_till_timeout_fail_or_success(
        test_url=f"{PROCESSING_SERVER_URL}/workflow/job-simple/{wf_job_id}",
        tries=30,
        wait=10
    )
    assert job_state == JobState.success
