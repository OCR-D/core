from dataclasses import dataclass, field
from typing import List
from ocrd_models.ocrd_page import OcrdPage
from PIL.Image import Image

@dataclass
class OcrdPageResultImage():
    pil : Image
    file_id : str
    file_path : str

@dataclass
class OcrdPageResult():
    pcgts : OcrdPage
    images : List[OcrdPageResultImage] = field(default_factory=list)
