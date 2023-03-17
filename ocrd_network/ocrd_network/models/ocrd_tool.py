from pydantic import BaseModel
from typing import List, Optional


class OcrdTool(BaseModel):
    executable: str
    categories: List[str]
    description: str
    input_file_grp: List[str]
    output_file_grp: Optional[List[str]]
    steps: List[str]
    parameters: Optional[dict] = None
