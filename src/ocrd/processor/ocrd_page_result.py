from dataclasses import dataclass, field
from typing import List, Union, Optional
from ocrd_models.ocrd_page import OcrdPage
from PIL.Image import Image

from ocrd_models.ocrd_page_generateds import AlternativeImageType, PageType


@dataclass
class OcrdPageResultImage():
    """
    Encapsulates a single ``AlternativeImage`` reference to be persisted
    as image file to the :py:class:`ocrd.Workspace`.
    """
    pil: Image
    """
    image data to be saved
    """
    file_id_suffix: str
    """
    a suffix to append to the file name when saving
    (something like ``.IMG`` according to OCR-D
    conventions for PAGE-XML)
    """
    alternative_image: Optional[Union[AlternativeImageType, PageType]]
    """
    the ``AlternativeImage`` instance that references this image;
    to be amended with the actual (final) ``@filename`` when saving

    alternatively, can be a ``Page`` instance: in that case,
    amend its ``@imageFilename`` (i.e. replace the original image
    of the PAGE-XML)
    """


@dataclass
class OcrdPageResult():
    """
    Encapsulates the return type of :py:func:`ocrd.Processor.process_page_pcgts`,
    i.e. an instance of :py:class:`ocrd_models.ocrd_page.OcrdPage` and an
    accompanying list of :py:class:`OcrdPageResultImage` that contain all
    image files referenced via ``AlternativeImage`` to be persisted into the
    :py:class:`ocrd.Workspace` along with the PAGE-XML itself.
    """
    pcgts: OcrdPage
    images: List[OcrdPageResultImage] = field(default_factory=list)
