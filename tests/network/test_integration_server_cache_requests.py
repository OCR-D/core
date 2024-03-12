from typing import List
from src.ocrd_network.constants import JobState
from src.ocrd_network.database import sync_db_get_processing_job, sync_db_update_processing_job
from src.ocrd_network.models import DBProcessorJob, PYJobInput
from src.ocrd_network.server_cache import CacheProcessingRequests


def test_update_request_counter():
    requests_cache = CacheProcessingRequests()
    workspace_key = "/path/to/mets.xml"
    requests_cache.update_request_counter(workspace_key=workspace_key, by_value=0)
    assert requests_cache.processing_counter[workspace_key] == 0
    requests_cache.update_request_counter(workspace_key=workspace_key, by_value=3)
    assert requests_cache.processing_counter[workspace_key] == 3
    requests_cache.update_request_counter(workspace_key=workspace_key, by_value=-1)
    requests_cache.update_request_counter(workspace_key=workspace_key, by_value=-1)
    requests_cache.update_request_counter(workspace_key=workspace_key, by_value=-1)
    assert requests_cache.processing_counter[workspace_key] == 0


def test_cache_request(processing_request_1: PYJobInput):
    requests_cache = CacheProcessingRequests()
    workspace_key = "/path/to/mets.xml"
    requests_cache.cache_request(workspace_key=workspace_key, data=processing_request_1)
    requests_cache.cache_request(workspace_key=workspace_key, data=processing_request_1)
    # two cached requests for the workspace key entry
    assert len(requests_cache.processing_requests[workspace_key]) == 2
    # one workspace key entry in the processing requests cache
    assert len(requests_cache.processing_requests) == 1


def test_has_workspace_cached_requests(processing_request_1: PYJobInput):
    requests_cache = CacheProcessingRequests()
    workspace_key = "/path/to/mets.xml"
    processing_request_1.path_to_mets = workspace_key
    assert not requests_cache.has_workspace_cached_requests(workspace_key=workspace_key)
    requests_cache.cache_request(workspace_key=workspace_key, data=processing_request_1)
    assert requests_cache.has_workspace_cached_requests(workspace_key=workspace_key)
    assert not requests_cache.has_workspace_cached_requests(workspace_key="non-existing")


def test_is_caching_required(processing_jobs_list: List[DBProcessorJob]):
    requests_cache = CacheProcessingRequests()

    # depends on nothing, should not be cached
    assert not requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[0].depends_on)
    # depends on processing_job_1, should be cached
    assert requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[1].depends_on)
    # depends on processing_job_2, should be cached
    assert requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[2].depends_on)
    # depends on processing_job_2, should be cached
    assert requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[3].depends_on)

    sync_db_update_processing_job(processing_jobs_list[0].job_id, state=JobState.success)
    # the dependent job has successfully finished, no caching required
    assert not requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[1].depends_on)
    sync_db_update_processing_job(processing_jobs_list[1].job_id, state=JobState.success)
    # the dependent job has successfully finished, no caching required for job 3 and job 4
    assert not requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[2].depends_on)
    assert not requests_cache.sync_is_caching_required(job_dependencies=processing_jobs_list[3].depends_on)


def test_cancel_dependent_jobs(processing_jobs_list: List[DBProcessorJob]):
    requests_cache = CacheProcessingRequests()
    # Must match with the workspace_key in the processing_jobs_list fixture
    workspace_key = "/path/to/mets.xml"
    db_processing_job_1 = sync_db_update_processing_job(processing_jobs_list[0].job_id, state=JobState.failed)
    assert db_processing_job_1.state == JobState.failed
    requests_cache.sync_cancel_dependent_jobs(
        workspace_key=workspace_key, processing_job_id=processing_jobs_list[0].job_id
    )
    db_processing_job_2 = sync_db_get_processing_job(job_id=processing_jobs_list[1].job_id)
    db_processing_job_3 = sync_db_get_processing_job(job_id=processing_jobs_list[2].job_id)
    db_processing_job_4 = sync_db_get_processing_job(job_id=processing_jobs_list[3].job_id)
    assert db_processing_job_2.state == JobState.cancelled
    assert db_processing_job_3.state == JobState.cancelled
    assert db_processing_job_4.state == JobState.cancelled


def test_consume_cached_requests(processing_jobs_list: List[DBProcessorJob]):
    requests_cache = CacheProcessingRequests()
    # Must match with the workspace_key in the processing_jobs_list fixture
    workspace_key = "/path/to/mets.xml"
    db_processing_job_1 = sync_db_update_processing_job(processing_jobs_list[0].job_id, state=JobState.success)
    assert db_processing_job_1.state == JobState.success
    # Consumes only processing job 2 since only that job's dependencies (i.e., job 1) have succeeded
    consumed_jobs = requests_cache.sync_consume_cached_requests(workspace_key=workspace_key)
    assert len(consumed_jobs) == 1

    db_processing_job_2 = sync_db_update_processing_job(processing_jobs_list[1].job_id, state=JobState.success)
    assert db_processing_job_2.state == JobState.success
    # Consumes processing job 3 and job 4 since they depend on job 2
    consumed_jobs = requests_cache.sync_consume_cached_requests(workspace_key=workspace_key)
    assert len(consumed_jobs) == 2
