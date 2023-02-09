# Check here for more details: Message structure #139
from __future__ import annotations
from datetime import datetime
from pickle import dumps, loads
from typing import Any, Dict, List, Optional
import yaml
from ocrd.network.models.job import Job
from pathlib import Path


# TODO: Maybe there is a more compact way to achieve the serialization/deserialization?
#  Using ProtocolBuffers should decrease the size of the messages in bytes.
#  It should be considered once we have a basic running prototype.

class OcrdProcessingMessage:
    def __init__(
            self,
            job_id: str = None,
            processor_name: str = None,
            created_time: int = None,
            path_to_mets: str = None,
            workspace_id: str = None,
            input_file_grps: List[str] = None,
            output_file_grps: Optional[List[str]] = None,
            page_id: str = None,
            parameters: Dict[str, Any] = None,
            result_queue_name: str = None,
    ) -> None:
        if not job_id:
            raise ValueError('job_id must be set')
        if not processor_name:
            raise ValueError('processor_name must be set')
        if not created_time:
            # We should not raise a ValueError but just calculate it
            created_time = int(datetime.utcnow().timestamp())
        if not input_file_grps or len(input_file_grps) == 0:
            raise ValueError('input_file_grps must be set and contain at least 1 element')
        if not (workspace_id or path_to_mets):
            raise ValueError('Either `workspace_id` or `path_to_mets` must be set')

        self.job_id = job_id  # uuid
        self.processor_name = processor_name  # "ocrd-.*"
        # Either of these two below
        self.workspace_id = workspace_id  # uuid
        self.path_to_mets = path_to_mets  # absolute path
        self.input_file_grps = input_file_grps
        self.output_file_grps = output_file_grps
        # e.g., "PHYS_0005..PHYS_0010" will process only pages between 5-10
        self.page_id = page_id if page_id else None
        # e.g., "ocrd-cis-ocropy-binarize-result"
        self.result_queue = result_queue_name if result_queue_name else (self.processor_name + "-result")
        # processor parameters
        self.parameters = parameters if parameters else None
        self.created_time = created_time

    # TODO: Implement the validator checks, e.g.,
    #  if the processor name matches the expected regex

    @staticmethod
    def encode(ocrd_processing_message: OcrdProcessingMessage) -> bytes:
        return dumps(ocrd_processing_message)

    @staticmethod
    def decode(ocrd_processing_message: bytes, encoding='utf-8') -> OcrdProcessingMessage:
        data = loads(ocrd_processing_message, encoding=encoding)
        return OcrdProcessingMessage(
            job_id=data.job_id,
            processor_name=data.processor_name,
            created_time=data.created_time,
            path_to_mets=data.path_to_mets,
            workspace_id=data.workspace_id,
            input_file_grps=data.input_file_grps,
            output_file_grps=data.output_file_grps,
            page_id=data.page_id,
            parameters=data.parameters,
            result_queue_name=data.result_queue
        )

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
            result_queue_name=data.get('result_queue', None),
        )

    @staticmethod
    def from_job(job: Job) -> OcrdProcessingMessage:
        return OcrdProcessingMessage(
            job_id=job.id,
            processor_name=job.processor_name,
            path_to_mets=job.path,
            input_file_grps=job.input_file_grps,
            output_file_grps=job.output_file_grps,
            page_id=job.page_id,
            parameters=job.parameters,
        )


class OcrdResultMessage:
    def __init__(self, job_id: str, status: str, workspace_id: str, path_to_mets: str) -> None:
        self.job_id = job_id
        self.status = status
        # Either of these two below
        self.workspace_id = workspace_id
        self.path_to_mets = path_to_mets

    @staticmethod
    def encode(ocrd_result_message: OcrdResultMessage) -> bytes:
        return dumps(ocrd_result_message)

    @staticmethod
    def decode(ocrd_result_message: bytes, encoding: str = 'utf-8') -> OcrdResultMessage:
        data = loads(ocrd_result_message, encoding=encoding)
        return OcrdResultMessage(
            job_id=data.job_id,
            status=data.status,
            workspace_id=data.workspace_id,
            path_to_mets=data.path_to_mets
        )

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
            status=data.get('status', None),
            path_to_mets=data.get('path_to_mets', None),
            workspace_id=data.get('workspace_id', None),
        )
