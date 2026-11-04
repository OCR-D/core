import asyncio
from typing import Dict, List

from fastapi import status

from ...constants import JobState
from ...database import (
    db_claim_result_callback,
    db_claim_result_counter_decrement,
    db_complete_result_callback,
    db_release_result_callback_claim,
    db_get_processing_job,
    db_update_processing_job,
)
from ...models import DBWorkflowJob, PYJobInput, PYResultMessage
from ...server_cache import CacheLockedPages, CacheProcessingRequests
from ...server_utils import get_from_database_workspace, raise_http_exception
from ...utils import expand_page_ids


class WorkspaceService:
    """Manage workspace locks, page locks and cached processing requests."""

    def __init__(self, log, deployer):
        self.log = log
        self.deployer = deployer
        self.workspace_locks: Dict[str, asyncio.Lock] = {}
        self.cache_locked_pages = CacheLockedPages()
        self.cache_processing_requests = CacheProcessingRequests()
        self.processing_service = None
        self.workflow_service = None

    def set_services(self, processing_service, workflow_service) -> None:
        self.processing_service = processing_service
        self.workflow_service = workflow_service

    def get_workspace_lock(self, workspace_key: str) -> asyncio.Lock:
        if workspace_key not in self.workspace_locks:
            self.workspace_locks[workspace_key] = asyncio.Lock()
        return self.workspace_locks[workspace_key]

    def _get_workspace_lock(self, workspace_key: str) -> asyncio.Lock:
        return self.get_workspace_lock(workspace_key)

    def lock_pages(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> None:
        self.cache_locked_pages.lock_pages(
            workspace_key=workspace_key,
            output_file_grps=output_file_grps,
            page_ids=page_ids,
        )

    def unlock_pages(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> None:
        self.cache_locked_pages.unlock_pages(
            workspace_key=workspace_key,
            output_file_grps=output_file_grps,
            page_ids=page_ids,
        )

    async def _lock_pages_of_workspace(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> None:
        self.lock_pages(workspace_key, output_file_grps, page_ids)

    async def _unlock_pages_of_workspace(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> None:
        self.unlock_pages(workspace_key, output_file_grps, page_ids)

    async def maybe_stop_mets_server(
        self, workspace_key: str, mets_server_url: str, path_to_mets: str
    ) -> bool:
        async with self.get_workspace_lock(workspace_key):
            return await self._maybe_stop_mets_server_locked(
                workspace_key, mets_server_url, path_to_mets
            )

    async def _maybe_stop_mets_server(
        self, workspace_key: str, mets_server_url: str, path_to_mets: str
    ) -> bool:
        return await self.maybe_stop_mets_server(
            workspace_key, mets_server_url, path_to_mets
        )

    async def _maybe_stop_mets_server_locked(
        self, workspace_key: str, mets_server_url: str, path_to_mets: str
    ) -> bool:
        if self.cache_processing_requests.processing_counter.get(workspace_key, 0) > 0:
            return False
        if self.cache_processing_requests.processing_requests.get(workspace_key):
            return False

        workflow_submitting = await DBWorkflowJob.find_one(
            DBWorkflowJob.path_to_mets == path_to_mets,
            DBWorkflowJob.submission_complete == False,
        )
        if workflow_submitting:
            self.log.debug(
                f"Deferring METS server shutdown for {path_to_mets}: "
                "workflow submission is incomplete"
            )
            return False

        self.log.debug(f"Stopping the METS server: {mets_server_url}")
        self.deployer.stop_uds_mets_server(
            mets_server_url=mets_server_url,
            path_to_mets=path_to_mets,
        )

        workflow_job = await DBWorkflowJob.find_one(
            DBWorkflowJob.path_to_mets == path_to_mets,
            DBWorkflowJob.mets_server_stopped == False,
        )
        if workflow_job:
            workflow_job.mets_server_stopped = True
            await workflow_job.save()
            if self.workflow_service is not None:
                await self.workflow_service.maybe_finish_workflow(workflow_job.job_id)

        self.cache_processing_requests.processing_requests.pop(workspace_key, None)
        return True

    async def consume_cached_jobs_of_workspace(
        self, workspace_key: str, mets_server_url: str, path_to_mets: str
    ) -> List[PYJobInput]:
        if not self.cache_processing_requests.processing_requests.get(workspace_key):
            request_counter = self.cache_processing_requests.processing_counter.get(
                workspace_key, 0
            )
            if request_counter <= 0:
                await self._maybe_stop_mets_server_locked(
                    workspace_key, mets_server_url, path_to_mets
                )
                self.log.debug(
                    f"Contents of the locked pages cache for: {workspace_key}"
                )
                locked_pages = self.cache_locked_pages.get_locked_pages(
                    workspace_key=workspace_key
                )
                for output_file_grp in locked_pages:
                    self.log.debug(f"{output_file_grp}: {locked_pages[output_file_grp]}")
            else:
                self.log.debug(
                    "Internal request cache is empty but waiting for "
                    f"{request_counter} result callbacks."
                )
            return []

        if workspace_key not in self.cache_processing_requests.processing_requests:
            self.log.debug(
                f"No internal queue available for workspace with key: {workspace_key}"
            )
            return []

        return await self.cache_processing_requests.consume_cached_requests(
            workspace_key=workspace_key
        )

    async def _consume_cached_jobs_of_workspace(
        self, workspace_key: str, mets_server_url: str, path_to_mets: str
    ) -> List[PYJobInput]:
        return await self.consume_cached_jobs_of_workspace(
            workspace_key, mets_server_url, path_to_mets
        )

    async def push_cached_jobs_to_workers(
        self, processing_jobs: List[PYJobInput]
    ) -> None:
        if not processing_jobs:
            self.log.debug("No processing jobs were consumed from the requests cache")
            return
        if self.processing_service is None:
            raise RuntimeError("ProcessingService has not been connected")

        for data in processing_jobs:
            self.log.info(
                f"Changing the job status of: {data.job_id} "
                f"from {JobState.cached} to {JobState.queued}"
            )
            db_consumed_job = await db_update_processing_job(
                job_id=data.job_id, state=JobState.queued
            )
            workspace_key = data.path_to_mets if data.path_to_mets else data.workspace_id

            await self._lock_pages_of_workspace(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=expand_page_ids(data.page_id),
            )
            job_output = await self.processing_service.push_job_to_worker(
                data=data, db_job=db_consumed_job
            )
            if not job_output:
                self.log.exception(
                    f"Failed to create job output for job input data: {data}"
                )

    async def cancel_cached_dependent_jobs(
        self, workspace_key: str, job_id: str
    ) -> None:
        await self.cache_processing_requests.cancel_dependent_jobs(
            workspace_key=workspace_key,
            processing_job_id=job_id,
        )

    async def _cancel_cached_dependent_jobs(
        self, workspace_key: str, job_id: str
    ) -> None:
        await self.cancel_cached_dependent_jobs(workspace_key, job_id)

    async def remove_job_from_request_cache(
        self, result_message: PYResultMessage
    ) -> None:
        result_job_id = result_message.job_id
        result_job_state = result_message.state
        path_to_mets = result_message.path_to_mets
        workspace_id = result_message.workspace_id

        self.log.info(f"Result job_id: {result_job_id}, state: {result_job_state}")
        db_workspace = await get_from_database_workspace(
            self.log, workspace_id, path_to_mets
        )
        mets_server_url = db_workspace.mets_server_url
        workspace_key = path_to_mets if path_to_mets else workspace_id

        try:
            db_result_job = await db_get_processing_job(result_job_id)
        except ValueError as error:
            raise_http_exception(
                self.log, status.HTTP_404_NOT_FOUND,
                f"Processing result job with id '{result_job_id}' not found in the DB.",
                error,
            )

        if not await db_claim_result_callback(result_job_id):
            self.log.info(f"Ignoring duplicate result callback for job {result_job_id}")
            return

        try:
            if result_job_state == JobState.failed:
                await self._cancel_cached_dependent_jobs(workspace_key, result_job_id)

            async with self.get_workspace_lock(workspace_key):
                await self._unlock_pages_of_workspace(
                    workspace_key=workspace_key,
                    output_file_grps=db_result_job.output_file_grps,
                    page_ids=expand_page_ids(db_result_job.page_id),
                )

                if await db_claim_result_counter_decrement(result_job_id):
                    self.cache_processing_requests.update_request_counter(
                        workspace_key=workspace_key, by_value=-1
                    )

                consumed_cached_jobs = await self._consume_cached_jobs_of_workspace(
                    workspace_key=workspace_key,
                    mets_server_url=mets_server_url,
                    path_to_mets=path_to_mets,
                )
                if consumed_cached_jobs:
                    self.cache_processing_requests.update_request_counter(
                        workspace_key=workspace_key,
                        by_value=len(consumed_cached_jobs),
                    )

            await self.push_cached_jobs_to_workers(consumed_cached_jobs)

            if not await db_complete_result_callback(result_job_id):
                raise RuntimeError(
                    "Failed to mark result callback as processed for job "
                    f"{result_job_id}"
                )
        except Exception:
            await db_release_result_callback_claim(result_job_id)
            raise