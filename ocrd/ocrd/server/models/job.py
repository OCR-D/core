from enum import Enum
from typing import List

from beanie import Document
from pydantic import BaseModel

from ocrd.server.config import Config


class StateEnum(str, Enum):
    queued = 'QUEUED'
    running = 'RUNNING'
    success = 'SUCCESS'
    failed = 'FAILED'


class JobInput(BaseModel):
    path: str
    description: str = None
    input_file_grps: List[str]
    output_file_grps: List[str]
    page_id: str = None
    parameters: dict

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
    description: str = None
    state: StateEnum
    input_file_grps: List[str]
    output_file_grps: List[str]
    page_id: str = None
    parameters: dict

    class Settings:
        name = Config.collection_name
        use_enum_values = True
