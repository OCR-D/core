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
    path: str
    description: Optional[str] = None
    input_file_grps: List[str]
    output_file_grps: Optional[List[str]]
    page_id: Optional[str] = None
    parameters: dict = {}  # Default to empty object, otherwise it won't pass the ocrd validation

    class Config:
        schema_extra = {
            "example": {
                "path": "/path/to/mets.xml",
                "description": "The description of this execution",
                "input_file_grps": ["INPUT_FILE_GROUP"],
                "output_file_grps": ["OUTPUT_FILE_GROUP"],
                "page_id": "PAGE_ID",
                "parameters": {}
            }
        }


class Job(Document):
    path: str
    description: Optional[str]
    state: StateEnum
    input_file_grps: List[str]
    output_file_grps: Optional[List[str]]
    page_id: Optional[str]
    parameters: Optional[dict]

    class Settings:
        use_enum_values = True
