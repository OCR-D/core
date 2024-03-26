from __future__ import annotations
from typing import Any, Dict, List, Optional
from yaml import dump, safe_load
from ocrd_validators import OcrdNetworkMessageValidator


class OcrdProcessingMessage:
    def __init__(
        self, job_id: str, processor_name: str, created_time: int, input_file_grps: List[str],
        output_file_grps: Optional[List[str]], path_to_mets: Optional[str], workspace_id: Optional[str],
        page_id: Optional[str], result_queue_name: Optional[str], callback_url: Optional[str],
        internal_callback_url: Optional[str], parameters: Dict[str, Any] = None
    ) -> None:
        if not job_id:
            raise ValueError("job_id must be provided")
        if not processor_name:
            raise ValueError("processor_name must be provided")
        if not created_time:
            raise ValueError("created time must be provided")
        if not input_file_grps or len(input_file_grps) == 0:
            raise ValueError("input_file_grps must be provided and contain at least 1 element")
        if not (workspace_id or path_to_mets):
            raise ValueError("Either 'workspace_id' or 'path_to_mets' must be provided")

        self.job_id = job_id
        self.processor_name = processor_name
        self.created_time = created_time
        self.input_file_grps = input_file_grps
        if output_file_grps:
            self.output_file_grps = output_file_grps
        if path_to_mets:
            self.path_to_mets = path_to_mets
        if workspace_id:
            self.workspace_id = workspace_id
        if page_id:
            self.page_id = page_id
        if result_queue_name:
            self.result_queue_name = result_queue_name
        if callback_url:
            self.callback_url = callback_url
        if internal_callback_url:
            self.internal_callback_url = internal_callback_url
        self.parameters = parameters if parameters else {}

    @staticmethod
    def encode_yml(ocrd_processing_message: OcrdProcessingMessage, encode_type: str = "utf-8") -> bytes:
        return dump(ocrd_processing_message.__dict__, indent=2).encode(encode_type)

    @staticmethod
    def decode_yml(ocrd_processing_message: bytes, decode_type: str = "utf-8") -> OcrdProcessingMessage:
        msg = ocrd_processing_message.decode(decode_type)
        data = safe_load(msg)
        report = OcrdNetworkMessageValidator.validate_message_processing(data)
        if not report.is_valid:
            raise ValueError(f"Validating the processing message has failed:\n{report.errors}")
        return OcrdProcessingMessage(
            job_id=data.get("job_id", None),
            processor_name=data.get("processor_name", None),
            created_time=data.get("created_time", None),
            path_to_mets=data.get("path_to_mets", None),
            workspace_id=data.get("workspace_id", None),
            input_file_grps=data.get("input_file_grps", None),
            output_file_grps=data.get("output_file_grps", None),
            page_id=data.get("page_id", None),
            parameters=data.get("parameters", None),
            result_queue_name=data.get("result_queue_name", None),
            callback_url=data.get("callback_url", None),
            internal_callback_url=data.get("internal_callback_url", None)
        )


class OcrdResultMessage:
    def __init__(self, job_id: str, state: str, path_to_mets: Optional[str], workspace_id: Optional[str] = '') -> None:
        self.job_id = job_id
        self.state = state
        self.workspace_id = workspace_id
        self.path_to_mets = path_to_mets

    @staticmethod
    def encode_yml(ocrd_result_message: OcrdResultMessage, encode_type: str = "utf-8") -> bytes:
        return dump(ocrd_result_message.__dict__, indent=2).encode(encode_type)

    @staticmethod
    def decode_yml(ocrd_result_message: bytes, decode_type: str = "utf-8") -> OcrdResultMessage:
        msg = ocrd_result_message.decode(decode_type)
        data = safe_load(msg)
        report = OcrdNetworkMessageValidator.validate_message_result(data)
        if not report.is_valid:
            raise ValueError(f"Validating the result message has failed:\n{report.errors}")
        return OcrdResultMessage(
            job_id=data.get("job_id", None),
            state=data.get("state", None),
            path_to_mets=data.get("path_to_mets", None),
            workspace_id=data.get("workspace_id", ''),
        )
