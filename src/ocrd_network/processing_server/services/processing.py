from pathlib import Path
from typing import Dict, List, Optional

from fastapi import status

from ...constants import JobState
from ...database import db_update_workspace
from ...models import DBProcessorJob, PYJobInput, PYJobOutput
from ...rabbitmq_utils import check_if_queue_exists, get_message_queues, OcrdProcessingMessage
from ...server_utils import (
    create_processing_message,
    create_workspace_if_not_exists,
    get_from_database_workspace,
    raise_http_exception,
    validate_and_return_mets_path,
    validate_job_input,
)
from ...utils import expand_page_ids, generate_id


class ProcessingService:
    """Discover processing workers and submit processing jobs."""

    def __init__(
        self, log, ocrd_all_tool_json, rmq_data, internal_job_callback_url,
        deployer, workspace_service, use_tcp_mets, multiplexing_endpoint
    ):
        self.log = log
        self.ocrd_all_tool_json = ocrd_all_tool_json
        self.rmq_data = rmq_data
        self.internal_job_callback_url = internal_job_callback_url
        self.deployer = deployer
        self.workspace_service = workspace_service
        self.use_tcp_mets = use_tcp_mets
        self.multiplexing_endpoint = multiplexing_endpoint
        self.rmq_publisher = None

    async def get_worker_ocrd_tool(self, processor_name: Optional[str]) -> Dict:
        if not processor_name:
            raise_http_exception(
                self.log, status.HTTP_404_NOT_FOUND,
                "No processor name (None) was provided."
            )

        ocrd_tool = self.ocrd_all_tool_json.get(processor_name)
        if not ocrd_tool:
            raise_http_exception(
                self.log, status.HTTP_404_NOT_FOUND,
                f"Ocrd tool of processing Worker '{processor_name}' "
                "not found in ocrd_all_tool.json."
            )
        return ocrd_tool

    def exists_worker(self, processor_name: Optional[str]) -> bool:
        if not processor_name:
            return False
        if processor_name == "ocrd-dummy":
            return True
        return bool(check_if_queue_exists(
            self.log, self.rmq_data, processor_name=processor_name
        ))

    def validate_worker_existence(self, processor_name: Optional[str]) -> None:
        if not processor_name:
            raise_http_exception(
                self.log, status.HTTP_422_UNPROCESSABLE_ENTITY,
                "No processor name (None) was provided."
            )
        if not self.exists_worker(processor_name):
            raise_http_exception(
                self.log, status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Processing Worker '{processor_name}' not found."
            )

    async def is_request_caching_required(
        self, workspace_key: str, output_file_grps: list[str],
        page_ids: list[str], depends_on: list[str]
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

    async def cache_processing_job_to_db(
        self, workspace_key: str, data: PYJobInput
    ) -> PYJobOutput:
        self.workspace_service.cache_processing_requests.cache_request(
            workspace_key, data
        )
        db_cached_job = DBProcessorJob(
            **data.dict(exclude_unset=True, exclude_none=True),
            internal_callback_url=self.internal_job_callback_url,
            state=JobState.cached,
        )
        await db_cached_job.insert()
        return db_cached_job.to_job_output()

    async def validate_and_forward_job_to_worker(
        self, processor_name: str, data: PYJobInput
    ) -> PYJobOutput:
        data.processor_name = processor_name
        self.validate_worker_existence(data.processor_name)

        if data.job_id:
            raise_http_exception(
                self.log, status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Processing request job id field is set but must not be: {data.job_id}"
            )

        data.job_id = generate_id()
        ocrd_tool = await self.get_worker_ocrd_tool(data.processor_name)
        validate_job_input(self.log, data.processor_name, ocrd_tool, data)

        if data.workspace_id:
            await get_from_database_workspace(self.log, data.workspace_id)
            workspace_key = data.workspace_id
        elif data.path_to_mets:
            await create_workspace_if_not_exists(self.log, mets_path=data.path_to_mets)
            workspace_key = data.path_to_mets
        else:
            raise_http_exception(
                self.log, status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Either 'path_to_mets' or 'workspace_id' must be set for the provided workspace."
            )

        cache = self.workspace_service.cache_processing_requests
        cache.update_request_counter(workspace_key=workspace_key, by_value=0)

        request_mets_path = await validate_and_return_mets_path(self.log, data)
        page_ids = expand_page_ids(data.page_id)
        cache_current_request = await self.is_request_caching_required(
            workspace_key, data.output_file_grps, page_ids, data.depends_on
        )

        if cache_current_request:
            return await self.cache_processing_job_to_db(workspace_key, data)

        return await self.dispatch_processing_job(
            data=data,
            workspace_key=workspace_key,
            page_ids=page_ids,
            request_mets_path=request_mets_path,
        )

    async def dispatch_processing_job(
        self, data: PYJobInput, workspace_key: str,
        page_ids: List[str], request_mets_path: str
    ) -> PYJobOutput:
        async with self.workspace_service.get_workspace_lock(workspace_key):
            self.workspace_service.lock_pages(
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
            return await self.push_job_to_worker(data=data, db_job=db_queued_job)

    async def push_job_to_worker(
        self, data: PYJobInput, db_job: DBProcessorJob
    ) -> PYJobOutput:
        self.log.debug(
            f"Pushing to Processing Worker: "
            f"{data.processor_name}, {data.page_id}, {data.job_id}"
        )
        job_output = await self.push_job_to_processing_queue(db_job=db_job)

        if not job_output:
            raise_http_exception(
                self.log, status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Failed to create job output for job input: {data}"
            )
        return job_output

    async def push_job_to_processing_queue(
        self, db_job: DBProcessorJob
    ) -> PYJobOutput:
        if not self.rmq_publisher:
            raise_http_exception(
                self.log, status.HTTP_500_INTERNAL_SERVER_ERROR,
                "The Processing Server has no connection to RabbitMQ Server. "
                "RMQPublisher is not connected."
            )

        processing_message = create_processing_message(self.log, db_job)
        try:
            encoded_message = OcrdProcessingMessage.encode_yml(processing_message)
            self.rmq_publisher.publish_to_queue(
                queue_name=db_job.processor_name,
                message=encoded_message,
            )
        except Exception as error:
            message = (
                "Processing server has failed to push processing message "
                f"to queue: {db_job.processor_name}, Processing message: "
                f"{processing_message.__dict__}"
            )
            raise_http_exception(
                self.log, status.HTTP_500_INTERNAL_SERVER_ERROR, message, error
            )
        return db_job.to_job_output()

    async def get_processor_job(self, job_id: str) -> PYJobOutput:
        from ...server_utils import _get_processor_job
        return await _get_processor_job(self.log, job_id)

    async def get_processor_job_log(self, job_id: str):
        from ...server_utils import _get_processor_job_log
        return await _get_processor_job_log(self.log, job_id)

    async def list_processors(self) -> List[str]:
        return get_message_queues(self.log, self.rmq_data)