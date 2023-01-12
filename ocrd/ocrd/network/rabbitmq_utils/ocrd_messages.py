# Check here for more details: Message structure #139
from datetime import datetime
from typing import Any, Dict, List


class OcrdProcessingMessage:
    def __init__(
            self,
            job_id: str = None,
            processor_name: str = None,
            created_time: int = None,
            path_to_mets: str = None,
            workspace_id: str = None,
            input_file_grps: List[str] = None,
            output_file_grps: List[str] = None,
            page_id: str = None,
            parameters: Dict[str, Any] = None,
            result_queue_name: str = None,
    ):
        if not job_id:
            raise ValueError(f"job_id must be set")
        if not processor_name:
            raise ValueError(f"processor_name must be set")
        if not created_time:
            # We should not raise a ValueError but just calculate it
            created_time = int(datetime.utcnow().timestamp())
        if not input_file_grps or len(input_file_grps) == 0:
            raise ValueError(f"input_file_grps must be set and contain at least 1 element")
        if not (workspace_id or path_to_mets):
            raise ValueError(f"Either `workspace_id` or `path_to_mets` must be set")

        self.job_id = job_id  # uuid
        self.processor_name = processor_name  # "ocrd-.*"
        # Either of these two below
        self.workspace_id = workspace_id  # uuid
        self.path_to_mets = path_to_mets  # absolute path
        self.input_file_grps = input_file_grps
        self.output_file_grps = output_file_grps
        # e.g., "PHYS_0005..PHYS_0010" will process only pages between 5-10
        self.page_id = page_id
        # e.g., "ocrd-cis-ocropy-binarize-result"
        self.result_queue = result_queue_name
        # processor parameters
        self.parameters = parameters
        self.created_time = created_time

    # TODO: Implement the validator checks, e.g.,
    #  if the processor name matches the expected regex


class OcrdResultMessage:
    def __init__(self, job_id: str, status: str, workspace_id: str, path_to_mets: str):
        self.job_id = job_id
        self.status = status
        # Either of these two below
        self.workspace_id = workspace_id
        self.path_to_mets = path_to_mets
