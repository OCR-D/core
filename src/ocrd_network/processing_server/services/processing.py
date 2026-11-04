from typing import Dict, List, Optional

from fastapi import status

from ...constants import JobState
from ...models import DBProcessorJob, PYJobInput, PYJobOutput
from ...rabbitmq_utils import check_if_queue_exists, get_message_queues, OcrdProcessingMessage
from ...server_utils import (
    create_processing_message,
    raise_http_exception,
)


class ProcessingService:
    """Discover processing workers and submit processing jobs."""

    def __init__(
        self, log, ocrd_all_tool_json, rmq_data, internal_job_callback_url,
        deployer, use_tcp_mets, multiplexing_endpoint
    ):
        self.log = log
        self.ocrd_all_tool_json = ocrd_all_tool_json
        self.rmq_data = rmq_data
        self.internal_job_callback_url = internal_job_callback_url
        self.deployer = deployer
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

    async def cache_processing_job_to_db(self, data: PYJobInput) -> PYJobOutput:
        db_cached_job = DBProcessorJob(
            **data.dict(exclude_unset=True, exclude_none=True),
            internal_callback_url=self.internal_job_callback_url,
            state=JobState.cached,
        )
        await db_cached_job.insert()
        return db_cached_job.to_job_output()

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