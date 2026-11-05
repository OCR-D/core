from logging import Logger
from pathlib import Path
from typing import List

from fastapi import status

from ...constants import JobState
from ...database import db_update_processing_job, db_update_workspace
from ...models import DBProcessorJob, PYJobInput, PYJobOutput
from ...runtime_data import Deployer
from ...server_utils import (
    create_workspace_if_not_exists,
    get_from_database_workspace,
    raise_http_exception,
    validate_and_return_mets_path,
    validate_job_input
)
from ...utils import expand_page_ids, generate_id

from .processing import ProcessingService
from .workspace import WorkspaceService


class ProcessingCoordinator:
    """Coordinates processing jobs across processing and workspace services."""

    def __init__(
        self,
        log: Logger,
        deployer: Deployer,
        processing_service: ProcessingService,
        workspace_service: WorkspaceService,
        internal_job_callback_url: str,
        use_tcp_mets: bool,
        multiplexing_endpoint: str
    ):
        self.log = log
        self.deployer = deployer
        self.processing_service = processing_service
        self.workspace_service = workspace_service
        self.internal_job_callback_url = internal_job_callback_url
        self.use_tcp_mets = use_tcp_mets
        self.multiplexing_endpoint = multiplexing_endpoint

    async def _is_request_caching_required(
        self,
        workspace_key: str,
        output_file_grps: List[str],
        page_ids: List[str],
        depends_on: List[str],
    ) -> bool:
        cache = self.workspace_service.cache_processing_requests
        cache_current_request = False

        if depends_on:
            cache_current_request = await cache.is_caching_required(depends_on)

        if not cache_current_request:
            cache_current_request = (
                self.workspace_service.cache_locked_pages
                .check_if_locked_pages_for_output_file_grps(
                    workspace_key=workspace_key,
                    output_file_grps=output_file_grps,
                    page_ids=page_ids,
                )
            )
        return cache_current_request

    async def _cache_processing_job_to_db(
        self, workspace_key: str, data: PYJobInput
    ) -> PYJobOutput:
        self.workspace_service.cache_processing_requests.cache_request(
            workspace_key, data
        )
        return await self.processing_service.cache_processing_job_to_db(data)

    async def validate_and_forward_job_to_worker(
        self, processor_name: str, data: PYJobInput
    ) -> PYJobOutput:
        data.processor_name = processor_name
        self.processing_service.validate_worker_existence(data.processor_name)

        if data.job_id:
            raise_http_exception(
                self.log,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Processing request job id field is set but must not be: {data.job_id}",
            )

        data.job_id = generate_id()
        ocrd_tool = await self.processing_service.get_worker_ocrd_tool(
            data.processor_name
        )
        validate_job_input(self.log, data.processor_name, ocrd_tool, data)

        if data.workspace_id:
            await get_from_database_workspace(self.log, data.workspace_id)
            workspace_key = data.workspace_id
        elif data.path_to_mets:
            await create_workspace_if_not_exists(
                self.log, mets_path=data.path_to_mets
            )
            workspace_key = data.path_to_mets
        else:
            raise_http_exception(
                self.log,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Either 'path_to_mets' or 'workspace_id' must be set "
                "for the provided workspace.",
            )

        self.workspace_service.cache_processing_requests.update_request_counter(
            workspace_key=workspace_key, by_value=0
        )

        request_mets_path = await validate_and_return_mets_path(self.log, data)
        page_ids = expand_page_ids(data.page_id)
        cache_current_request = await self._is_request_caching_required(
            workspace_key, data.output_file_grps, page_ids, data.depends_on
        )

        if cache_current_request:
            return await self._cache_processing_job_to_db(workspace_key, data)

        return await self._dispatch_processing_job(
            data=data,
            workspace_key=workspace_key,
            page_ids=page_ids,
            request_mets_path=request_mets_path,
        )

    async def _dispatch_processing_job(
        self,
        data: PYJobInput,
        workspace_key: str,
        page_ids: List[str],
        request_mets_path: str,
    ) -> PYJobOutput:
        async with self.workspace_service.get_workspace_lock(workspace_key):
            self.workspace_service.lock_pages_of_workspace(
                workspace_key=workspace_key,
                output_file_grps=data.output_file_grps,
                page_ids=page_ids,
            )
            ws_dir_path = str(Path(request_mets_path).parent)
            mets_server_url = self.deployer.start_uds_mets_server(
                ws_dir_path=ws_dir_path
            )

            if self.use_tcp_mets:
                mets_server_url = self.multiplexing_endpoint

            await db_update_workspace(
                workspace_id=data.workspace_id,
                workspace_mets_path=data.path_to_mets,
                mets_server_url=mets_server_url,
            )

            db_queued_job = DBProcessorJob(
                **data.dict(exclude_unset=True, exclude_none=True),
                internal_callback_url=self.internal_job_callback_url,
                state=JobState.queued,
            )
            await db_queued_job.insert()
            self.workspace_service.cache_processing_requests.update_request_counter(
                workspace_key=workspace_key, by_value=1
            )
            return await self.processing_service.push_job_to_worker(
                data=data, db_job=db_queued_job
            )

    async def push_cached_jobs_to_workers(
        self, processing_jobs: List[PYJobInput]
    ) -> None:
        if not processing_jobs:
            self.log.debug("No processing jobs were consumed from the requests cache")
            return

        for data in processing_jobs:
            self.log.info(
                f"Changing the job status of: {data.job_id} "
                f"from {JobState.cached} to {JobState.queued}"
            )
            db_consumed_job = await db_update_processing_job(
                job_id=data.job_id, state=JobState.queued
            )
            workspace_key = (
                data.path_to_mets if data.path_to_mets else data.workspace_id
            )

            self.workspace_service.lock_pages_of_workspace(
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