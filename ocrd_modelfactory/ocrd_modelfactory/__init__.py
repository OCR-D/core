from datetime import datetime

from PIL import Image

from ocrd_utils import VERSION, MIMETYPE_PAGE
from ocrd_models import OcrdExif
from ocrd_models.ocrd_page import PcGtsType, PageType, MetadataType, parse

__all__ = [
    'exif_from_filename',
    'page_from_file',
    'page_from_image',
]


def exif_from_filename(image_filename):
    if image_filename is None:
        raise Exception("Must pass 'image_filename' to 'exif_from_filename'")
    return OcrdExif(Image.open(image_filename))

def page_from_image(input_file):
    if input_file.local_filename is None:
        raise Exception("input_file must have 'local_filename' property")
    exif = exif_from_filename(input_file.local_filename)
    now = datetime.now()
    return PcGtsType(
        Metadata=MetadataType(
            Creator="OCR-D/core %s" % VERSION,
            Created=now,
            LastChange=now
        ),
        Page=PageType(
            imageWidth=exif.width,
            imageHeight=exif.height,
            # XXX brittle
            imageFilename=input_file.url if input_file.url is not None else 'file://' + input_file.local_filename
        )
    )

def page_from_file(input_file):
    """
    Create a new PAGE-XML from a METS file representing a PAGE-XML or an image.
    """
    #  print("PARSING PARSING '%s'" % input_file)
    if input_file.mimetype.startswith('image'):
        return page_from_image(input_file)
    if input_file.mimetype == MIMETYPE_PAGE:
        return parse(input_file.local_filename, silence=True)
    raise Exception("Unsupported mimetype '%s'" % input_file.mimetype)
