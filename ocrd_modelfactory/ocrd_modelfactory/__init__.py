"""

Factory methods to create models for data, files, URLs.

"""
from datetime import datetime
from pathlib import Path
from yaml import safe_load, safe_dump

from PIL import Image

from ocrd_utils import VERSION, MIMETYPE_PAGE
from ocrd_models import OcrdExif
from ocrd_models.ocrd_page import (
    PcGtsType, PageType, MetadataType,
    parse, parseEtree
)

__all__ = [
    'exif_from_filename',
    'page_from_file',
    'page_from_image',
]


def exif_from_filename(image_filename):
    """
    Create :py:class:`~ocrd_models.ocrd_exif.OcrdExif`
    by opening an image file with PIL and reading its metadata.

    Arguments:
        image_filename (str): Local image path name (relative to workspace).
    """
    if image_filename is None:
        raise Exception("Must pass 'image_filename' to 'exif_from_filename'")
    with Image.open(image_filename) as pil_img:
        ocrd_exif = OcrdExif(pil_img)
    return ocrd_exif

def page_from_image(input_file, with_tree=False):
    """
    Create :py:class:`~ocrd_models.ocrd_page.OcrdPage`
    from an :py:class:`~ocrd_models.ocrd_file.OcrdFile`
    representing an image (i.e. should have ``@mimetype`` starting with ``image/``).

    Arguments:
        input_file (:py:class:`~ocrd_models.ocrd_file.OcrdFile`): file to open \
            and produce a PAGE DOM for
    Keyword arguments:
        with_tree (boolean): whether to return XML node tree, element-node mapping \
            and reverse mapping, too (cf. :py:func:`ocrd_models.ocrd_page.parseEtree`)
    """
    if not input_file.local_filename:
        raise ValueError("input_file must have 'local_filename' property")
    if not Path(input_file.local_filename).exists():
        raise FileNotFoundError("File not found: '%s' (%s)" % (input_file.local_filename, input_file))
    exif = exif_from_filename(input_file.local_filename)
    now = datetime.now()
    pcgts = PcGtsType(
        Metadata=MetadataType(
            Creator="OCR-D/core %s" % VERSION,
            Created=now,
            LastChange=now
        ),
        Page=PageType(
            imageWidth=exif.width,
            imageHeight=exif.height,
            # XXX brittle
            imageFilename=input_file.url if input_file.url is not None else input_file.local_filename
        ),
        pcGtsId=input_file.ID
    )
    if not with_tree:
        return pcgts
    mapping = dict()
    etree = pcgts.to_etree(mapping_=mapping)
    revmap = dict(((node, element) for element, node in mapping.items()))
    return pcgts, etree, mapping, revmap

def page_from_file(input_file, with_tree=False):
    """
    Create a new PAGE-XML from a METS file representing a PAGE-XML or an image.

    Arguments:
        input_file (:py:class:`~ocrd_models.ocrd_file.OcrdFile`): file to open \
            and produce a PAGE DOM for
    Keyword arguments:
        with_tree (boolean): whether to return XML node tree, element-node mapping \
            and reverse mapping, too (cf. :py:func:`ocrd_models.ocrd_page.parseEtree`)
    """
    if not input_file.local_filename:
        raise ValueError("input_file must have 'local_filename' property")
    if not Path(input_file.local_filename).exists():
        raise FileNotFoundError("File not found: '%s' (%s)" % (input_file.local_filename, input_file))
    if input_file.mimetype.startswith('image'):
        return page_from_image(input_file, with_tree=with_tree)
    if input_file.mimetype == MIMETYPE_PAGE:
        return (parseEtree if with_tree else parse)(input_file.local_filename, silence=True)
    raise ValueError("Unsupported mimetype '%s'" % input_file.mimetype)
