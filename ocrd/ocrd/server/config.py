from typing import Type

from ocrd import Processor


class Config:
    processor_class: Type[Processor] = None
    title: str
    description: str
    version: str
    ocrd_tool: dict
    db_url: str
    collection_name: str
