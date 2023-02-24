from datetime import datetime
from enum import Enum
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel


class StateEnum(str, Enum):
    queued = 'QUEUED'
    running = 'RUNNING'
    success = 'SUCCESS'
    failed = 'FAILED'


class JobInput(BaseModel):
    """ Wraps the parameters required to make a run-processor-request
    """
    path: Optional[str] = None
    workspace_id: Optional[str] = None
    description: Optional[str] = None
    input_file_grps: List[str]
    output_file_grps: Optional[List[str]]
    page_id: Optional[str] = None
    parameters: dict = {}  # Always set to empty dict when None, otherwise it fails ocr-d-validation

    class Config:
        schema_extra = {
            'example': {
                'path': '/path/to/mets.xml',
                'description': 'The description of this execution',
                'input_file_grps': ['INPUT_FILE_GROUP'],
                'output_file_grps': ['OUTPUT_FILE_GROUP'],
                'page_id': 'PAGE_ID',
                'parameters': {}
            }
        }


class JobOutput(BaseModel):
    """ Wraps output information for a job-response
    """
    job_id: str
    processor_name: str
    state: StateEnum
    workspace_path: Optional[str]
    workspace_id: Optional[str]


class Job(Document):
    """ Job representation in the database
    """
    processor_name: str
    path: str
    workspace_id: Optional[str]
    description: Optional[str]
    state: StateEnum
    input_file_grps: List[str]
    output_file_grps: Optional[List[str]]
    page_id: Optional[str]
    parameters: Optional[dict]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    class Settings:
        use_enum_values = True

    def to_job_output(self) -> JobOutput:
        return JobOutput(
            job_id=str(self.id),
            processor_name=self.processor_name,
            state=self.state,
            workspace_path=self.path if not self.workspace_id else None,
            workspace_id=self.workspace_id,
        )
