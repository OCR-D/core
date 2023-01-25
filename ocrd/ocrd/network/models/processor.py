from pydantic import BaseModel
from typing import Dict, Any, Optional


class ProcessorArgs(BaseModel):
    workspace_id: str = ''
    input_file_grps: str = ''
    output_file_grps: str = ''
    page_id: str = ''
    parameters: Optional[Dict[str, Any]] = {}


# TODO: this does not conform to the openapi.yml. It should?!
class ProcessorJob(BaseModel):
    job_id: str
    workspace_id: str
    processor_name: str
