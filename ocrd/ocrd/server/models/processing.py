from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, TEXT

from ocrd.server.config import Config


class Workspace(BaseModel):
    id: str = Field(..., alias='@id')
    description: str = None


class Processing(Document):
    workspace: Workspace
    input_file_grps: str
    output_file_grps: str
    page_id: str = None
    parameters: dict

    class Settings:
        name = Config.collection_name
        indexes = [
            IndexModel(
                [('workspace.@id', TEXT)],
                name='workspace_id_index'
            )
        ]
