# This model is directly taken from the Triet's implementation:
# REST API wrapper for the processor #884

from typing import List, Optional

from pydantic import BaseModel


class OcrdTool(BaseModel):
    executable: str
    categories: List[str]
    description: str
    input_file_grp: List[str]
    output_file_grp: Optional[List[str]]
    steps: List[str]
    parameters: Optional[dict] = None
