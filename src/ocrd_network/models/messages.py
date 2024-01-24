from pydantic import BaseModel
from typing import Optional
from .job import StateEnum


class PYResultMessage(BaseModel):
    """ Wraps the parameters required to make a result message request
    """
    job_id: str
    state: StateEnum
    path_to_mets: Optional[str] = None
    workspace_id: Optional[str] = None

    class Config:
        schema_extra = {
            'example': {
                'job_id': '123123123',
                'state': 'SUCCESS',
                'path_to_mets': '/path/to/mets.xml',
                'workspace_id': 'c7f25615-fc17-4365-a74d-ad20e1ddbd0e'
            }
        }
