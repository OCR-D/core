from typing import List

from pydantic import BaseModel


class OcrdTool(BaseModel):
    executable: str
    categories: List[str]
    description: str
    input_file_grp: List[str]
    output_file_grp: List[str]
    steps: List[str]
    parameters: dict
