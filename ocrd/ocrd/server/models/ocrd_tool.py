from pydantic import BaseModel


class OcrdTool(BaseModel):
    executable: str
    categories: list[str]
    description: str
    input_file_grp: list[str]
    output_file_grp: list[str]
    steps: list[str]
    parameters: dict
