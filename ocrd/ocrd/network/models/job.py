# These are the models directly taken from the Triet's implementation:
# REST API wrapper for the processor #884

# TODO: In the OCR-D WebAPI implementation we did a clear separation between
#  the business response models and the low level database models. In order to achieve
#  better modularity, we should use the same approach in the network package as well.


from datetime import datetime
from enum import Enum
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel


class StateEnum(str, Enum):
    queued = 'QUEUED'
    running = 'RUNNING'
    success = 'SUCCESS'  # TODO: SUCCEEDED for consistency
    failed = 'FAILED'


class JobInput(BaseModel):
    path: str
    description: Optional[str] = None
    input_file_grps: List[str]
    output_file_grps: Optional[List[str]]
    page_id: Optional[str] = None
    parameters: dict = None  # Always set to an empty dict when it's None, otherwise it won't pass the ocrd validation

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


class Job(Document):
    path: str
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
