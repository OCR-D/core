from dataclasses import dataclass, field
from typing import List, Union, Optional
from ocrd_models.ocrd_page import OcrdPage
from PIL.Image import Image

from ocrd_models.ocrd_page_generateds import AlternativeImageType, PageType

@dataclass
class OcrdPageResultImage():
    pil : Image
    file_id_suffix : str
    alternative_image : Optional[Union[AlternativeImageType, PageType]]

@dataclass
class OcrdPageResult():
    pcgts : OcrdPage
    images : List[OcrdPageResultImage] = field(default_factory=list)
