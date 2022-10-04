from typing import Optional, List

from beanie import PydanticObjectId
from pydantic import BaseModel

from ocrd.server.models.job import StateEnum


class MockJob(BaseModel):
    path: str
    description: Optional[str]
    state: StateEnum
    input_file_grps: List[str]
    output_file_grps: Optional[List[str]]
    page_id: Optional[str]
    parameters: Optional[dict]

    async def insert(self, *, link_rule=None, session=None, skip_actions=None):
        pass

    @classmethod
    async def get(cls, document_id):
        if document_id == PydanticObjectId('60cd778664dc9f75f4aadec8'):
            return MockJob(path='', state=StateEnum.failed, input_file_grps=['TEST'])
        return None

    class Settings:
        name = 'mocked'
