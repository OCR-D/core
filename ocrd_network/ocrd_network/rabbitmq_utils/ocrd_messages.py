from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
import yaml
from ocrd_network.models.job import Job


class OcrdProcessingMessage:
    def __init__(
            self,
            job_id: str = None,
            processor_name: str = None,
            path_to_mets: str = None,
            workspace_id: Optional[str] = None,
            input_file_grps: List[str] = None,
            output_file_grps: Optional[List[str]] = None,
            page_id: Optional[str] = None,
            parameters: Dict[str, Any] = None,
            result_queue_name: Optional[str] = None,
            callback_url: Optional[str] = None,
            created_time: Optional[int] = None
    ) -> None:
        if not job_id:
            raise ValueError('job_id must be provided')
        if not processor_name:
            raise ValueError('processor_name must be provided')
        if not input_file_grps or len(input_file_grps) == 0:
            raise ValueError('input_file_grps must be provided and contain at least 1 element')
        if not (workspace_id or path_to_mets):
            raise ValueError('Either "workspace_id" or "path_to_mets" must be provided')
        if not created_time:
            # We should not raise a ValueError but just calculate it
            created_time = int(datetime.utcnow().timestamp())

        self.job_id = job_id  # uuid
        self.processor_name = processor_name  # "ocrd-.*"
        # Either of these two below
        self.workspace_id = workspace_id  # uuid
        self.path_to_mets = path_to_mets  # absolute path
        self.input_file_grps = input_file_grps
        self.output_file_grps = output_file_grps
        # e.g., "PHYS_0005..PHYS_0010" will process only pages between 5-10
        self.page_id = page_id if page_id else None
        # processor parameters
        self.parameters = parameters if parameters else None
        self.result_queue_name = result_queue_name
        self.callback_url = callback_url
        self.created_time = created_time

    @staticmethod
    def encode_yml(ocrd_processing_message: OcrdProcessingMessage) -> bytes:
        """convert OcrdProcessingMessage to yml
        """
        return yaml.dump(ocrd_processing_message.__dict__, indent=2).encode('utf-8')

    @staticmethod
    def decode_yml(ocrd_processing_message: bytes) -> OcrdProcessingMessage:
        """Parse OcrdProcessingMessage from yml
        """
        msg = ocrd_processing_message.decode('utf-8')
        data = yaml.load(msg, Loader=yaml.Loader)
        return OcrdProcessingMessage(
            job_id=data.get('job_id', None),
            processor_name=data.get('processor_name', None),
            created_time=data.get('created_time', None),
            path_to_mets=data.get('path_to_mets', None),
            workspace_id=data.get('workspace_id', None),
            input_file_grps=data.get('input_file_grps', None),
            output_file_grps=data.get('output_file_grps', None),
            page_id=data.get('page_id', None),
            parameters=data.get('parameters', None),
            result_queue_name=data.get('result_queue_name', None),
            callback_url=data.get('callback_url', None)
        )

    @staticmethod
    def from_job(job: Job) -> OcrdProcessingMessage:
        return OcrdProcessingMessage(
            job_id=job.job_id,
            processor_name=job.processor_name,
            path_to_mets=job.path_to_mets,
            input_file_grps=job.input_file_grps,
            output_file_grps=job.output_file_grps,
            page_id=job.page_id,
            parameters=job.parameters,
            result_queue_name=job.result_queue_name,
            callback_url=job.callback_url
        )


class OcrdResultMessage:
    def __init__(self, job_id: str, state: str,
                 path_to_mets: Optional[str] = None,
                 workspace_id: Optional[str] = None) -> None:
        self.job_id = job_id
        self.state = state
        self.workspace_id = workspace_id
        self.path_to_mets = path_to_mets

    @staticmethod
    def encode_yml(ocrd_result_message: OcrdResultMessage) -> bytes:
        """convert OcrdResultMessage to yml
        """
        return yaml.dump(ocrd_result_message.__dict__, indent=2).encode('utf-8')

    @staticmethod
    def decode_yml(ocrd_result_message: bytes) -> OcrdResultMessage:
        """Parse OcrdResultMessage from yml
        """
        msg = ocrd_result_message.decode('utf-8')
        data = yaml.load(msg, Loader=yaml.Loader)
        return OcrdResultMessage(
            job_id=data.get('job_id', None),
            state=data.get('state', None),
            path_to_mets=data.get('path_to_mets', None),
            workspace_id=data.get('workspace_id', None),
        )
