from dataclasses import dataclass, field
import copy
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

class OcrdPageResultVariadicListWrapper():
    """
    Proxy object for :py:class:`ocrd.SingleOcrdPageResult` allowing
    list semantics (i.e. multi-valued return from
    :py:func:`ocrd.Processor.process_page_pcgts`) without changing
    the API introduced in version 3.0.

    Everything but list access will yield the old (singular valued)
    semantics.
    """
    def __init__(
            self,
            pcgts: OcrdPage,
            *args):
        self._results = [SingleOcrdPageResult(pcgts)] + [
            SingleOcrdPageResult(arg) for arg in args]

    def __getitem__(self, key):
        return self._results[key]

    def __contains__(self, key):
        return key in self._results

    def __len__(self):
        return len(self._results)

    def __iter__(self):
        return iter(self._results)

    def __repr__(self):
        return repr(self._results)

    # allow copy() without infinite recursion
    def __copy__(self):
        return OcrdPageResultVariadicListWrapper(*copy.copy(self._results))

    # allow deepcopy() without infinite recursion
    def __deepcopy__(self, memo):
        return OcrdPageResultVariadicListWrapper(*copy.deepcopy(self._results))

    # delegate to all members of first result
    def __getattr__(self, name):
        return getattr(self._results[0], name)

SingleOcrdPageResult, OcrdPageResult = OcrdPageResult, OcrdPageResultVariadicListWrapper
